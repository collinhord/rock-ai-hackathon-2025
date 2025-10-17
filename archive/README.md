# Archive

This directory contains historical hackathon work and prototypes that have been superseded by the reorganized workspace structure.

## Contents

### `metadata-extractor-prototype/`
**Original**: `/metadata-extractor/`  
**Archived**: October 17, 2025  
**Reason**: Prototype created during hackathon. Core functionality (Bedrock client) has been moved to `shared/llm/bedrock_client.py` and enhanced.  
**Value**: Demonstrates excellent code organization patterns that were replicated across the platform.

### `backups/`
**Original**: `/rock-skills/backups/`  
**Archived**: October 17, 2025  
**Reason**: Old file backups. Git history provides sufficient version control.  
**Value**: Safety net during initial development.

## Why Archive Rather Than Delete?

These files demonstrate:
1. Evolution of the codebase from hackathon to production
2. Good patterns that were adopted (e.g., prompts-as-code, separation of concerns)
3. Historical context for architectural decisions

## Access

All archived code remains accessible in this directory and in Git history. To restore any archived file:

```bash
cp archive/metadata-extractor-prototype/some_file.py ./destination/
```

---

**Last Updated**: October 17, 2025

