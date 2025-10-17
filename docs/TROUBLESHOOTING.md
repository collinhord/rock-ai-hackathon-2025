# ROCK Skills Metadata Extraction - Troubleshooting Guide

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Applies To**: Enhanced Metadata Extractor v1.0+

## Table of Contents

1. [Common Errors](#common-errors)
2. [Performance Issues](#performance-issues)
3. [Quality Problems](#quality-problems)
4. [AWS Bedrock Issues](#aws-bedrock-issues)
5. [spaCy Issues](#spacy-issues)
6. [Data Issues](#data-issues)
7. [Recovery Procedures](#recovery-procedures)

---

## Common Errors

### Error: "Missing dependencies: boto3"

**Symptom**: Script fails immediately with import error

**Solution**:
```bash
# Install required dependencies
pip install boto3 spacy pandas numpy

# Download spaCy language model
python -m spacy download en_core_web_sm
```

---

### Error: "NoCredentialsError: Unable to locate credentials"

**Symptom**: Script fails when trying to call AWS Bedrock

**Cause**: AWS credentials not configured

**Solution**:
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

**Verification**:
```bash
# Test AWS connection
aws bedrock-runtime list-foundation-models --region us-west-2
```

---

### Error: "ReadTimeoutError" or "ConnectTimeout"

**Symptom**: Intermittent API failures with timeout errors

**Cause**: Network latency or Bedrock API overload

**Solution**:
1. The script automatically retries with exponential backoff
2. If persistent, increase timeout in `enhanced_metadata_extractor.py`:
   ```python
   self.bedrock = boto3.client(
       'bedrock-runtime',
       region_name='us-west-2',
       config=Config(read_timeout=600)  # Increase from 300
   )
   ```

---

### Error: "ModelNotFoundException" or "ResourceNotFoundException"

**Symptom**: Cannot find Claude Sonnet 4.5 model

**Cause**: Model ID incorrect or region doesn't support model

**Solution**:
1. Verify model ID in script:
   ```python
   self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
   ```
2. Ensure region is `us-west-2` (cross-region inference profile)
3. Check AWS account has Bedrock access enabled

---

### Error: "ThrottlingException" or "Too Many Requests"

**Symptom**: API calls failing with rate limit errors

**Cause**: Exceeded Bedrock API rate limits

**Solution**:
1. Script has built-in retry logic
2. Add throttling configuration:
   ```python
   config = Config(
       read_timeout=300,
       retries={'max_attempts': 5, 'mode': 'adaptive'}
   )
   ```
3. Contact AWS support to increase rate limits if needed

---

## Performance Issues

### Issue: Extraction too slow (<1 skill/minute)

**Symptoms**:
- Processing takes >10 seconds per skill
- Throughput below 6 skills/minute

**Possible Causes**:
1. Network latency to AWS
2. spaCy model loading repeatedly
3. Large skill descriptions (>500 characters)
4. API throttling

**Solutions**:
1. Verify network connectivity:
   ```bash
   ping bedrock-runtime.us-west-2.amazonaws.com
   ```
2. Ensure spaCy model loads once (initialization)
3. Add progress logging to identify bottleneck
4. Monitor API response times in logs

---

### Issue: High API costs

**Symptoms**:
- Cost per skill >$0.01
- Total cost exceeds estimates

**Possible Causes**:
1. Prompts too long
2. Skills being re-processed
3. Excessive retries

**Solutions**:
1. Check prompt length in `build_llm_prompt()`
2. Use `--skip-existing` to avoid re-processing
3. Review checkpoint files for duplicates
4. Optimize prompt structure (remove unnecessary examples)

---

### Issue: Memory usage too high

**Symptoms**:
- Process memory >2GB
- System slowdown or crashes

**Possible Causes**:
1. Large dataset loaded into memory
2. spaCy model and vectors in memory
3. Accumulating results without checkpointing

**Solutions**:
1. Process in smaller batches
2. Increase checkpoint interval (but don't exceed 500)
3. Use `--limit` for testing
4. Clear intermediate results periodically

---

## Quality Problems

### Issue: Many "not_applicable" values

**Symptoms**:
- >50% of educational metadata fields are "not_applicable"
- Skills seem relevant but metadata is empty

**Possible Causes**:
1. Wrong content area (Math skills with ELA prompts)
2. Skill descriptions too vague
3. LLM prompt too restrictive

**Solutions**:
1. Verify `CONTENT_AREA_NAME` filtering correct
2. Review sample skills with `not_applicable`:
   ```bash
   # Check skills with many N/A values
   python3 -c "
   import pandas as pd
   df = pd.read_csv('output.csv')
   na_cols = ['text_type', 'text_mode', 'text_genre', 'skill_domain', 'scope']
   na_count = df[na_cols].apply(lambda x: (x == 'not_applicable').sum(), axis=1)
   print(df[na_count >= 4][['SKILL_NAME', 'SKILL_AREA_NAME']])
   "
   ```
3. Adjust prompts to be more domain-flexible

---

### Issue: Low confidence rates (<70%)

**Symptoms**:
- Most skills have `llm_confidence = medium` or `low`
- LLM notes indicate uncertainty

**Possible Causes**:
1. Ambiguous skill descriptions
2. LLM prompt unclear about criteria
3. Skills outside expected patterns

**Solutions**:
1. Review low-confidence skills manually:
   ```python
   low_conf = df[df['llm_confidence'] == 'low']
   print(low_conf[['SKILL_NAME', 'llm_notes']])
   ```
2. Add domain-specific examples to prompts
3. Refine classification criteria in prompts
4. Consider creating specialized prompts by skill area

---

### Issue: Contradictory metadata

**Symptoms**:
- `cognitive_demand = recall` but `task_complexity = advanced`
- `text_type = fictional` but `text_genre = expository`

**Possible Causes**:
1. LLM classification inconsistency
2. Skill description ambiguous
3. Classification criteria not well-defined

**Solutions**:
1. Add consistency validation:
   ```python
   # Flag contradictions
   contradictions = df[
       ((df['cognitive_demand'] == 'recall') & (df['task_complexity'] == 'advanced')) |
       ((df['text_type'] == 'fictional') & (df['text_genre'].isin(['expository', 'argumentative'])))
   ]
   ```
2. Add consistency instructions to LLM prompt
3. Implement post-processing consistency checks
4. Manual review flagged skills

---

### Issue: spaCy extraction missing key terms

**Symptoms**:
- `actions` or `targets` empty for clear skills
- Key concepts not captured

**Possible Causes**:
1. Domain vocabulary not in dictionary
2. Complex sentence structure confuses parser
3. Unusual word forms (gerunds, passive voice)

**Solutions**:
1. Extend vocabulary dictionaries in `spacy_processor.py`:
   ```python
   self.educational_verbs.update([
       'solve', 'calculate', 'compute', 'estimate',
       'construct', 'measure', 'graph', 'plot'
   ])
   ```
2. Review missed terms:
   ```python
   empty_actions = df[df['actions'] == '']
   print(empty_actions['SKILL_NAME'])
   ```
3. Add domain-specific NER (Named Entity Recognition)

---

## AWS Bedrock Issues

### Issue: Model access denied

**Symptom**: "AccessDeniedException" or "You don't have access to the model"

**Solution**:
1. Enable model access in AWS Bedrock console
2. Go to: AWS Console → Bedrock → Model Access
3. Request access to Claude Sonnet 4.5
4. Wait for approval (usually instant for Claude models)

---

### Issue: Token limit exceeded

**Symptom**: "ValidationException: messages.0.content must be less than X tokens"

**Solution**:
1. Reduce prompt length
2. Simplify skill descriptions (truncate if >500 chars)
3. Remove unnecessary examples from prompt

---

### Issue: Region not supported

**Symptom**: Service not available in region

**Solution**:
1. Use `us-west-2` region (most Bedrock features available)
2. Or use cross-region inference profile:
   ```python
   model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
   ```

---

## spaCy Issues

### Issue: Language model not found

**Symptom**: "Can't find model 'en_core_web_sm'"

**Solution**:
```bash
# Download the required model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; spacy.load('en_core_web_sm')"
```

---

### Issue: Slow spaCy processing

**Symptom**: spaCy taking >1 second per skill

**Solution**:
1. Disable unnecessary pipeline components:
   ```python
   nlp = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer'])
   ```
2. Use smaller model for speed (but may reduce accuracy)
3. Process in batches with `nlp.pipe()`

---

## Data Issues

### Issue: Input file not found

**Symptom**: "FileNotFoundError: rock_schemas/SKILLS.csv"

**Solution**:
```bash
# Verify file path
ls -l rock-skills/data/input/rock_schemas/SKILLS.csv

# Use absolute path if needed
python3 enhanced_metadata_extractor.py \
    --input /full/path/to/SKILLS.csv
```

---

### Issue: CSV parsing errors

**Symptom**: "ParserError" or "unexpected end of data"

**Solution**:
1. Verify CSV format:
   ```bash
   head -5 SKILLS.csv
   ```
2. Check for malformed rows:
   ```python
   df = pd.read_csv('SKILLS.csv', on_bad_lines='warn')
   ```
3. Ensure UTF-8 encoding
4. Check for unescaped quotes in skill descriptions

---

### Issue: No skills after filtering

**Symptom**: "Filtered to 0 skills"

**Solution**:
1. Verify content area name matches exactly:
   ```bash
   # Check actual values
   cut -d',' -f5 SKILLS.csv | sort | uniq
   ```
2. Correct content area name (case-sensitive):
   - ✓ "English Language Arts"
   - ✓ "Mathematics"
   - ✗ "ELA" (wrong)
   - ✗ "Math" (wrong)

---

## Recovery Procedures

### Recovering from Crashed Extraction

**Scenario**: Extraction process crashes mid-run

**Steps**:
1. **Identify last checkpoint**:
   ```bash
   ls -lt outputs/production_extraction/ela/checkpoint_*.csv | head -1
   ```

2. **Find checkpoint range**:
   ```bash
   # Checkpoint filename format: checkpoint_0_99.csv, checkpoint_100_199.csv
   # If last is checkpoint_400_499.csv, 400 skills completed
   ```

3. **Resume from checkpoint**:
   ```bash
   # Use --skip-existing with last checkpoint
   python3 enhanced_metadata_extractor.py \
       --input ../../data/input/rock_schemas/SKILLS.csv \
       --content-area "English Language Arts" \
       --output-dir ../outputs/production_extraction/ela \
       --skip-existing ../outputs/production_extraction/ela/checkpoint_400_499.csv \
       --checkpoint-interval 100
   ```

4. **Merge results** (after completion):
   ```python
   import pandas as pd
   import glob
   
   # Load all checkpoints
   checkpoints = glob.glob('outputs/production_extraction/ela/checkpoint_*.csv')
   final = glob.glob('outputs/production_extraction/ela/skill_metadata_enhanced_*.csv')
   
   # Combine all
   dfs = [pd.read_csv(f) for f in checkpoints + final]
   combined = pd.concat(dfs, ignore_index=True)
   
   # Remove duplicates (keep last occurrence)
   combined = combined.drop_duplicates(subset=['SKILL_ID'], keep='last')
   
   # Save
   combined.to_csv('outputs/production_extraction/ela_complete.csv', index=False)
   ```

---

### Recovering from Corrupted Output

**Scenario**: Output file is corrupted or incomplete

**Steps**:
1. **Check checkpoint integrity**:
   ```python
   import pandas as pd
   try:
       df = pd.read_csv('checkpoint_100_199.csv')
       print(f"Loaded {len(df)} skills")
       print(df.columns.tolist())
   except Exception as e:
       print(f"Checkpoint corrupted: {e}")
   ```

2. **Use previous good checkpoint**:
   - Identify last valid checkpoint
   - Delete corrupted files
   - Resume from last valid checkpoint

3. **Rebuild from checkpoints**:
   ```bash
   # If final file corrupted but checkpoints valid
   python3 merge_checkpoints.py \
       --checkpoint-dir outputs/production_extraction/ela \
       --output ela_recovered.csv
   ```

---

### Emergency Stop and Restart

**Scenario**: Need to stop extraction gracefully

**Steps**:
1. **Find process ID**:
   ```bash
   ps aux | grep enhanced_metadata_extractor
   ```

2. **Graceful shutdown** (preferred):
   ```bash
   # Send SIGTERM (allows cleanup)
   kill -15 <PID>
   ```

3. **Force kill** (if unresponsive):
   ```bash
   # Send SIGKILL (immediate)
   kill -9 <PID>
   ```

4. **Wait for checkpoint write**:
   - Checkpoints write every 100 skills
   - Last checkpoint may be incomplete if killed during write

5. **Restart**:
   - Use last valid checkpoint
   - Resume as described above

---

## Getting Help

### Self-Diagnosis Checklist

Before seeking help, check:
- [ ] AWS credentials configured correctly
- [ ] Bedrock model access enabled
- [ ] Python dependencies installed
- [ ] spaCy model downloaded
- [ ] Input file path correct
- [ ] Content area name matches exactly
- [ ] Sufficient disk space for outputs
- [ ] Network connectivity to AWS

### Log Analysis

**Enable verbose logging**:
```bash
python3 enhanced_metadata_extractor.py \
    --input SKILLS.csv \
    --content-area "English Language Arts" \
    --output-dir ./output \
    --verbose  # Add this flag
```

**Check logs for patterns**:
```bash
# Find all errors
grep -i error outputs/production_extraction/ela_extraction.log

# Find low-confidence extractions
grep "confidence: low" outputs/production_extraction/ela_extraction.log

# Check API call times
grep "API Call" outputs/production_extraction/ela_extraction.log | \
    awk '{print $NF}' | sort -n | tail -20
```

### Contact Information

For issues not covered in this guide:
1. Check GitHub Issues: [repository URL]
2. Contact: ROCK Skills Analysis Team
3. Slack: #rock-skills-metadata

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Maintained By**: ROCK Skills Analysis Team

