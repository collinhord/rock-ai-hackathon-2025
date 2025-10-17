#!/usr/bin/env python3
"""
Taxonomy Coverage Validation Script

Validates whether the 5 "convergent concepts" from framework analysis
are already present in the existing literacy taxonomy.
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import csv

# The 5 concepts to validate
CONCEPTS_TO_VALIDATE = {
    'Reading Fluency': {
        'synonyms': ['fluency', 'fluent reading', 'reading rate', 'reading speed', 
                    'automaticity', 'automatic word recognition', 'prosody', 
                    'expression', 'phrasing', 'reading flow'],
        'related_terms': ['accurate reading', 'smooth reading', 'rapid reading']
    },
    'Decoding': {
        'synonyms': ['decode', 'decoding skills', 'word attack', 'phonics',
                    'letter-sound correspondence', 'sounding out', 'blending',
                    'word recognition', 'phonetic decoding'],
        'related_terms': ['sound out', 'blend sounds', 'phonological decoding']
    },
    'Reading Strategies': {
        'synonyms': ['strategy', 'strategic reading', 'comprehension strategies',
                    'metacognitive', 'self-monitoring', 'fix-up strategies',
                    'repair strategies', 'reading comprehension strategies'],
        'related_terms': ['monitoring comprehension', 'strategy use', 'strategic approach']
    },
    'Syntactic Knowledge': {
        'synonyms': ['syntax', 'grammar', 'sentence structure', 'language structures',
                    'grammatical awareness', 'sentence construction', 'parts of speech',
                    'syntactic awareness', 'grammatical knowledge'],
        'related_terms': ['sentence understanding', 'grammatical understanding', 'linguistic structure']
    },
    'Semantic Knowledge': {
        'synonyms': ['vocabulary', 'word meaning', 'lexical knowledge', 'semantics',
                    'word knowledge', 'word understanding', 'definitional knowledge',
                    'lexical semantics', 'word meanings'],
        'related_terms': ['vocabulary knowledge', 'word comprehension', 'meaning understanding']
    }
}

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

def load_taxonomy(csv_path: Path) -> pd.DataFrame:
    """Load the literacy taxonomy CSV."""
    print(f"Loading taxonomy from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"  Loaded {len(df)} rows")
    print(f"  Columns: {', '.join(df.columns)}")
    return df

def create_search_index(df: pd.DataFrame) -> Dict[str, List[Tuple]]:
    """Create searchable index of all taxonomy content."""
    print("\nCreating search index...")
    index = defaultdict(list)
    
    hierarchy_cols = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
    
    for idx, row in df.iterrows():
        # Index each hierarchy level
        for col in hierarchy_cols:
            if col in df.columns and pd.notna(row[col]):
                text = normalize_text(row[col])
                if text:
                    # Create full path for context
                    path_parts = []
                    for level in hierarchy_cols:
                        if level in df.columns and pd.notna(row[level]):
                            path_parts.append(str(row[level]))
                        if level == col:
                            break
                    
                    full_path = ' > '.join(path_parts)
                    index[text].append({
                        'level': col,
                        'path': full_path,
                        'row_idx': idx,
                        'annotation': normalize_text(row.get('Skill Subset Annotation', ''))
                    })
        
        # Index annotations separately
        if 'Skill Subset Annotation' in df.columns and pd.notna(row['Skill Subset Annotation']):
            annotation = normalize_text(row['Skill Subset Annotation'])
            if annotation:
                path_parts = [str(row[col]) for col in hierarchy_cols if col in df.columns and pd.notna(row[col])]
                full_path = ' > '.join(path_parts)
                index[annotation].append({
                    'level': 'Annotation',
                    'path': full_path,
                    'row_idx': idx,
                    'annotation': annotation
                })
    
    print(f"  Indexed {len(index)} unique terms")
    return index

def search_concept(concept_name: str, concept_def: Dict, index: Dict, df: pd.DataFrame) -> Dict:
    """Search for a concept in the taxonomy."""
    print(f"\n{'='*70}")
    print(f"SEARCHING: {concept_name}")
    print(f"{'='*70}")
    
    results = {
        'concept': concept_name,
        'exact_matches': [],
        'synonym_matches': [],
        'related_matches': [],
        'annotation_matches': [],
        'distributed_evidence': []
    }
    
    # Search for exact name
    concept_norm = normalize_text(concept_name)
    if concept_norm in index:
        results['exact_matches'] = index[concept_norm]
        print(f"✓ EXACT MATCH found: '{concept_name}'")
        for match in results['exact_matches']:
            print(f"  - {match['level']}: {match['path']}")
    
    # Search for synonyms
    for synonym in concept_def['synonyms']:
        synonym_norm = normalize_text(synonym)
        if synonym_norm in index:
            results['synonym_matches'].extend(index[synonym_norm])
            print(f"✓ Synonym found: '{synonym}'")
            for match in index[synonym_norm][:3]:  # Show first 3
                print(f"  - {match['level']}: {match['path']}")
    
    # Search for related terms
    for related in concept_def['related_terms']:
        related_norm = normalize_text(related)
        if related_norm in index:
            results['related_matches'].extend(index[related_norm])
    
    # Search in annotations
    all_synonyms = [concept_norm] + [normalize_text(s) for s in concept_def['synonyms']]
    for term in all_synonyms:
        for key, matches in index.items():
            if term in key and matches[0]['level'] == 'Annotation':
                results['annotation_matches'].extend(matches)
    
    # Check for distributed representation
    if concept_name == 'Reading Fluency':
        # Look for components: speed, accuracy, expression, automaticity
        components = ['speed', 'accuracy', 'expression', 'automaticity', 'rate', 'pace']
        for comp in components:
            if comp in index:
                results['distributed_evidence'].append({
                    'component': comp,
                    'locations': index[comp]
                })
    
    # Calculate summary
    total_matches = (len(results['exact_matches']) + 
                    len(results['synonym_matches']) + 
                    len(results['related_matches']) +
                    len(results['annotation_matches']))
    
    print(f"\nSummary: {total_matches} total matches found")
    print(f"  - Exact: {len(results['exact_matches'])}")
    print(f"  - Synonyms: {len(results['synonym_matches'])}")
    print(f"  - Related: {len(results['related_matches'])}")
    print(f"  - Annotations: {len(results['annotation_matches'])}")
    
    return results

def classify_presence(concept_name: str, search_results: Dict) -> Dict:
    """Classify the presence status of a concept."""
    
    exact = len(search_results['exact_matches'])
    synonyms = len(search_results['synonym_matches'])
    related = len(search_results['related_matches'])
    annotations = len(search_results['annotation_matches'])
    distributed = len(search_results['distributed_evidence'])
    
    total_evidence = exact + synonyms + related + annotations
    
    # Classification logic
    if exact > 0:
        if exact >= 3 or synonyms >= 5:
            status = 'PRESENT & EXPLICIT'
            coverage = 100
            recommendation = 'A'  # No action needed
        else:
            status = 'PRESENT & EXPLICIT'
            coverage = 75
            recommendation = 'B'  # May need reorganization
    elif synonyms >= 5:
        status = 'PRESENT & IMPLICIT'
        coverage = 75
        recommendation = 'B'  # Reorganize/rename
    elif synonyms >= 2 or related >= 3:
        status = 'PARTIALLY PRESENT'
        coverage = 50
        recommendation = 'C'  # Enhance/extend
    elif total_evidence > 0 or distributed > 0:
        status = 'PARTIALLY PRESENT'
        coverage = 25
        recommendation = 'C'  # Enhance/extend
    else:
        status = 'TRULY MISSING'
        coverage = 0
        recommendation = 'D'  # Add as new
    
    # Get unique locations
    locations = set()
    for match_type in ['exact_matches', 'synonym_matches', 'related_matches']:
        for match in search_results[match_type]:
            locations.add(match['path'])
    
    return {
        'concept': concept_name,
        'status': status,
        'coverage': coverage,
        'recommendation': recommendation,
        'evidence_count': total_evidence,
        'unique_locations': len(locations),
        'sample_locations': list(locations)[:5]
    }

def generate_evidence_table(all_results: List[Dict]) -> pd.DataFrame:
    """Generate evidence table for all concepts."""
    
    rows = []
    for result in all_results:
        concept = result['concept']
        search = result['search_results']
        classification = result['classification']
        
        # Get sample locations
        locations = []
        for match in search['exact_matches'][:2]:
            locations.append(match['path'])
        for match in search['synonym_matches'][:3]:
            locations.append(match['path'])
        
        locations_str = '\n'.join(locations[:5])
        if len(locations) > 5:
            locations_str += f"\n... and {len(locations) - 5} more"
        
        # Get current names used
        names = set()
        for match in search['exact_matches'] + search['synonym_matches']:
            path_parts = match['path'].split(' > ')
            if path_parts:
                names.add(path_parts[-1])
        
        names_str = ', '.join(list(names)[:5])
        
        rows.append({
            'Concept': concept,
            'Framework_Term': concept,
            'Status': classification['status'],
            'Coverage_%': classification['coverage'],
            'Evidence_Count': classification['evidence_count'],
            'Locations_Found': classification['unique_locations'],
            'Sample_Locations': locations_str,
            'Current_Names': names_str,
            'Recommendation': classification['recommendation']
        })
    
    return pd.DataFrame(rows)

def get_recommendation_text(rec_code: str) -> str:
    """Get recommendation text from code."""
    recommendations = {
        'A': 'NO ACTION NEEDED - Already present and well-organized',
        'B': 'REORGANIZE/RENAME - Present but needs better organization or terminology',
        'C': 'ENHANCE/EXTEND - Partially present, add missing components',
        'D': 'ADD AS NEW - Truly missing from taxonomy'
    }
    return recommendations.get(rec_code, 'Unknown')

def generate_detailed_report(all_results: List[Dict], df: pd.DataFrame) -> str:
    """Generate detailed validation report."""
    
    report = []
    report.append("# Taxonomy Coverage Validation Report")
    report.append(f"\n**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Taxonomy**: POC_science_of_reading_literacy_skills_taxonomy.csv")
    report.append(f"**Total Rows**: {len(df):,}")
    report.append("\n---\n")
    
    # Summary
    report.append("## Executive Summary\n")
    
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for result in all_results:
        rec = result['classification']['recommendation']
        counts[rec] += 1
    
    report.append("```")
    report.append("┌─────────────────────────────────────────────────────────┐")
    report.append("│          TAXONOMY VALIDATION RESULTS                     │")
    report.append("├─────────────────────────────────────────────────────────┤")
    report.append("│                                                          │")
    report.append(f"│  Already Present & Optimal:        {counts['A']} concepts           │")
    report.append(f"│  Present but Need Reorganization:  {counts['B']} concepts           │")
    report.append(f"│  Partially Present, Need Extension: {counts['C']} concepts          │")
    report.append(f"│  Truly Missing, Should Add:        {counts['D']} concepts           │")
    report.append("│                                                          │")
    report.append("└─────────────────────────────────────────────────────────┘")
    report.append("```\n")
    
    # Detailed findings
    report.append("## Detailed Findings by Concept\n")
    
    for result in all_results:
        concept = result['concept']
        search = result['search_results']
        classification = result['classification']
        
        report.append(f"### {concept}\n")
        report.append(f"**Status**: {classification['status']}")
        report.append(f"**Coverage**: {classification['coverage']}%")
        report.append(f"**Recommendation**: {get_recommendation_text(classification['recommendation'])}\n")
        
        # Evidence
        report.append("**Evidence Found:**")
        report.append(f"- Exact name matches: {len(search['exact_matches'])}")
        report.append(f"- Synonym matches: {len(search['synonym_matches'])}")
        report.append(f"- Related term matches: {len(search['related_matches'])}")
        report.append(f"- Annotation mentions: {len(search['annotation_matches'])}")
        report.append(f"- Total evidence: {classification['evidence_count']}\n")
        
        # Sample locations
        if classification['sample_locations']:
            report.append("**Found in Taxonomy at:**")
            for loc in classification['sample_locations'][:5]:
                report.append(f"- `{loc}`")
            if len(classification['sample_locations']) > 5:
                report.append(f"- ... and {len(classification['sample_locations']) - 5} more locations")
            report.append("")
        
        # Specific matches
        if search['exact_matches']:
            report.append("**Exact Matches:**")
            for match in search['exact_matches'][:3]:
                report.append(f"- {match['level']}: `{match['path']}`")
            report.append("")
        
        if search['synonym_matches']:
            report.append("**Synonym Matches (sample):**")
            shown = set()
            for match in search['synonym_matches'][:10]:
                path = match['path']
                if path not in shown:
                    report.append(f"- `{path}`")
                    shown.add(path)
            report.append("")
        
        report.append("---\n")
    
    # Recommendations
    report.append("## Recommendations\n")
    
    if counts['A'] > 0:
        report.append(f"### No Action Needed ({counts['A']} concepts)\n")
        report.append("These concepts are already well-represented in the taxonomy:\n")
        for result in all_results:
            if result['classification']['recommendation'] == 'A':
                report.append(f"- **{result['concept']}**: {result['classification']['coverage']}% coverage")
        report.append("")
    
    if counts['B'] > 0:
        report.append(f"### Reorganize/Rename ({counts['B']} concepts)\n")
        report.append("These concepts exist but could benefit from reorganization or terminology alignment:\n")
        for result in all_results:
            if result['classification']['recommendation'] == 'B':
                report.append(f"- **{result['concept']}**: Present but scattered or using non-standard terms")
                report.append(f"  - Action: Consider consolidating or renaming for better framework alignment")
        report.append("")
    
    if counts['C'] > 0:
        report.append(f"### Enhance/Extend ({counts['C']} concepts)\n")
        report.append("These concepts are partially present - keep existing content but add missing aspects:\n")
        for result in all_results:
            if result['classification']['recommendation'] == 'C':
                report.append(f"- **{result['concept']}**: {result['classification']['coverage']}% coverage")
                report.append(f"  - Action: Extend existing content to cover full concept")
        report.append("")
    
    if counts['D'] > 0:
        report.append(f"### Add as New ({counts['D']} concepts)\n")
        report.append("These concepts appear to be truly missing:\n")
        for result in all_results:
            if result['classification']['recommendation'] == 'D':
                report.append(f"- **{result['concept']}**: No significant evidence found")
                report.append(f"  - Action: Add as new concept as originally recommended")
        report.append("")
    
    return '\n'.join(report)

def main():
    """Main execution."""
    print("="*70)
    print("TAXONOMY COVERAGE VALIDATION")
    print("="*70)
    print()
    
    # Load taxonomy
    taxonomy_path = Path('../POC_science_of_reading_literacy_skills_taxonomy.csv')
    if not taxonomy_path.exists():
        print(f"Error: Taxonomy file not found at {taxonomy_path}")
        return
    
    df = load_taxonomy(taxonomy_path)
    
    # Create search index
    index = create_search_index(df)
    
    # Search for each concept
    all_results = []
    for concept_name, concept_def in CONCEPTS_TO_VALIDATE.items():
        search_results = search_concept(concept_name, concept_def, index, df)
        classification = classify_presence(concept_name, search_results)
        
        all_results.append({
            'concept': concept_name,
            'search_results': search_results,
            'classification': classification
        })
    
    # Generate outputs
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Evidence table CSV
    evidence_df = generate_evidence_table(all_results)
    evidence_path = output_dir / 'concept_presence_evidence.csv'
    evidence_df.to_csv(evidence_path, index=False)
    print(f"\n✅ Evidence table saved: {evidence_path}")
    
    # Detailed report
    report = generate_detailed_report(all_results, df)
    report_path = output_dir / 'taxonomy_validation_analysis.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Detailed report saved: {report_path}")
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print("\nQuick Summary:")
    for result in all_results:
        concept = result['concept']
        classification = result['classification']
        status = classification['status']
        coverage = classification['coverage']
        rec = classification['recommendation']
        print(f"  {concept:30} | {status:20} | {coverage:3}% | Rec: {rec}")
    
    print(f"\n📊 See detailed results:")
    print(f"   - {report_path}")
    print(f"   - {evidence_path}")

if __name__ == '__main__':
    main()

