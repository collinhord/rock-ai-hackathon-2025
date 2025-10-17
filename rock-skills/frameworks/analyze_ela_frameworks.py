#!/usr/bin/env python3
"""
ELA Framework Comparison and Recommendation Generator

Compares Duke 2021 and Scarborough's Reading Rope frameworks,
identifies convergent concepts, and generates prioritized recommendations.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Concept:
    """Represents a concept from a framework."""
    name: str
    source: str  # 'duke', 'scarborough', or 'both'
    description: str = ""
    grade_range: str = ""
    complexity_band: str = ""
    skill_domain: str = ""
    
def normalize_concept_name(name: str) -> str:
    """Normalize concept names for comparison."""
    return name.lower().strip().replace('-', ' ').replace('/', ' ')

def load_duke_concepts() -> List[Concept]:
    """Load Duke 2021 missing concepts from gap report."""
    duke_concepts = [
        "Reading Fluency",
        "Decoding",
        "Syntactic Knowledge",
        "Attentional Control",
        "Content Knowledge",
        "Reading Strategies",
        "Semantic Knowledge",
        "Prosody",
        "Working Memory"
    ]
    
    return [Concept(name=name, source='duke') for name in duke_concepts]

def load_scarborough_concepts() -> List[Concept]:
    """Load Scarborough missing concepts from gap report and CSV."""
    scarborough_new = [
        "Strand Interaction and Development",
        "Strategic Reading",
        "Skilled Reading",
        "Decoding",
        "Vocabulary",
        "Reading Disability/Difficulty",
        "Reading Fluency",
        "Language Structures"
    ]
    
    concepts = []
    
    # Load from CSV for additional metadata
    csv_path = Path("output/scarborough_full/concepts/ela_master_concepts.csv")
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['MASTER_CONCEPT_NAME']
                if any(normalize_concept_name(name) == normalize_concept_name(new) 
                       for new in scarborough_new):
                    concepts.append(Concept(
                        name=name,
                        source='scarborough',
                        description=row.get('DESCRIPTION', ''),
                        grade_range=row.get('GRADE_RANGE', ''),
                        complexity_band=row.get('COMPLEXITY_BAND', ''),
                        skill_domain=row.get('SKILL_DOMAIN', '')
                    ))
    
    # Add any missing from the list
    existing_names = {normalize_concept_name(c.name) for c in concepts}
    for name in scarborough_new:
        if normalize_concept_name(name) not in existing_names:
            concepts.append(Concept(name=name, source='scarborough'))
    
    return concepts

def identify_convergent_concepts(duke_concepts: List[Concept], 
                                 scarborough_concepts: List[Concept]) -> Dict[str, List[Concept]]:
    """Identify concepts that appear in both frameworks."""
    
    duke_names = {normalize_concept_name(c.name): c for c in duke_concepts}
    scarborough_names = {normalize_concept_name(c.name): c for c in scarborough_concepts}
    
    convergent = {}
    duke_only = []
    scarborough_only = []
    
    # Find exact matches
    for norm_name, duke_concept in duke_names.items():
        if norm_name in scarborough_names:
            convergent[duke_concept.name] = [duke_concept, scarborough_names[norm_name]]
        else:
            duke_only.append(duke_concept)
    
    for norm_name, scar_concept in scarborough_names.items():
        if norm_name not in duke_names:
            scarborough_only.append(scar_concept)
    
    # Check for semantic similarities
    semantic_matches = {
        'reading strategies': 'strategic reading',
        'syntactic knowledge': 'language structures',
        'content knowledge': 'background knowledge',
        'semantic knowledge': 'vocabulary'
    }
    
    for duke_norm, scar_norm in semantic_matches.items():
        duke_match = duke_names.get(duke_norm)
        scar_match = scarborough_names.get(scar_norm)
        
        if duke_match and scar_match and duke_match.name not in convergent:
            convergent[f"{duke_match.name} / {scar_match.name}"] = [duke_match, scar_match]
            if duke_match in duke_only:
                duke_only.remove(duke_match)
            if scar_match in scarborough_only:
                scarborough_only.remove(scar_match)
    
    return {
        'convergent': convergent,
        'duke_only': duke_only,
        'scarborough_only': scarborough_only
    }

def prioritize_concepts(comparison: Dict) -> Dict[str, List]:
    """Prioritize concepts into 3 tiers based on criteria."""
    
    tier1_critical_convergent = []
    tier2_important_single = []
    tier3_supplementary = []
    
    # Tier 1: Convergent concepts (highest priority)
    for concept_name, concept_list in comparison['convergent'].items():
        tier1_critical_convergent.append({
            'name': concept_name,
            'concepts': concept_list,
            'priority': 1,
            'rationale': 'Present in both Duke 2021 and Scarborough frameworks (convergent evidence)',
            'foundational': assess_foundational_importance(concept_name),
            'integration_complexity': 'low'
        })
    
    # Tier 2: High-value single-source concepts
    for concept in comparison['duke_only']:
        if is_foundational(concept.name):
            tier2_important_single.append({
                'name': concept.name,
                'concepts': [concept],
                'priority': 2,
                'rationale': f'Important concept from Duke 2021 framework, foundational to reading',
                'foundational': True,
                'integration_complexity': 'medium'
            })
        else:
            tier3_supplementary.append({
                'name': concept.name,
                'concepts': [concept],
                'priority': 3,
                'rationale': f'Specialized concept from Duke 2021',
                'foundational': False,
                'integration_complexity': 'medium'
            })
    
    for concept in comparison['scarborough_only']:
        if is_foundational(concept.name):
            tier2_important_single.append({
                'name': concept.name,
                'concepts': [concept],
                'priority': 2,
                'rationale': f'Important concept from Scarborough framework, foundational to reading',
                'foundational': True,
                'integration_complexity': 'medium'
            })
        else:
            tier3_supplementary.append({
                'name': concept.name,
                'concepts': [concept],
                'priority': 3,
                'rationale': f'Specialized concept from Scarborough',
                'foundational': False,
                'integration_complexity': 'medium'
            })
    
    return {
        'tier1': tier1_critical_convergent,
        'tier2': tier2_important_single,
        'tier3': tier3_supplementary
    }

def is_foundational(concept_name: str) -> bool:
    """Determine if concept is foundational to reading development."""
    foundational_keywords = ['decoding', 'fluency', 'phonological', 'vocabulary', 
                            'comprehension', 'word recognition', 'language structures',
                            'background knowledge', 'strategic']
    name_lower = concept_name.lower()
    return any(keyword in name_lower for keyword in foundational_keywords)

def assess_foundational_importance(concept_name: str) -> bool:
    """Assess if a convergent concept is foundational."""
    return is_foundational(concept_name)

def map_to_taxonomy_structure(concept_name: str) -> Dict[str, str]:
    """Propose where concept fits in existing taxonomy structure."""
    
    # Mapping based on Scarborough's Reading Rope structure
    mappings = {
        'reading fluency': {'strand': 'Word Recognition', 'pillar': 'Automaticity', 'domain': 'Reading Fluency'},
        'decoding': {'strand': 'Word Recognition', 'pillar': 'Phonics', 'domain': 'Decoding'},
        'syntactic knowledge': {'strand': 'Language Comprehension', 'pillar': 'Linguistic Knowledge', 'domain': 'Syntax'},
        'language structures': {'strand': 'Language Comprehension', 'pillar': 'Linguistic Knowledge', 'domain': 'Language Structures'},
        'attentional control': {'strand': 'Active Self-Regulation', 'pillar': 'Executive Function Skills', 'domain': 'Attention Control'},
        'content knowledge': {'strand': 'Language Comprehension', 'pillar': 'Background Knowledge', 'domain': 'Content Knowledge'},
        'background knowledge': {'strand': 'Language Comprehension', 'pillar': 'Background Knowledge', 'domain': 'World Knowledge'},
        'reading strategies': {'strand': 'Active Self-Regulation', 'pillar': 'Metacognitive Skills', 'domain': 'Reading Strategies'},
        'strategic reading': {'strand': 'Active Self-Regulation', 'pillar': 'Metacognitive Skills', 'domain': 'Strategic Reading'},
        'semantic knowledge': {'strand': 'Language Comprehension', 'pillar': 'Vocabulary', 'domain': 'Semantic Knowledge'},
        'vocabulary': {'strand': 'Language Comprehension', 'pillar': 'Vocabulary', 'domain': 'Lexical Knowledge'},
        'prosody': {'strand': 'Word Recognition', 'pillar': 'Fluency', 'domain': 'Prosodic Features'},
        'working memory': {'strand': 'Active Self-Regulation', 'pillar': 'Executive Function Skills', 'domain': 'Working Memory'},
        'skilled reading': {'strand': 'Reading Proficiency', 'pillar': 'Integrated Reading', 'domain': 'Skilled Reading'},
        'strand interaction': {'strand': 'Reading Proficiency', 'pillar': 'Component Integration', 'domain': 'Strand Coordination'},
        'reading disability': {'strand': 'Reading Development', 'pillar': 'Individual Differences', 'domain': 'Reading Difficulties'}
    }
    
    norm_name = normalize_concept_name(concept_name)
    for key, mapping in mappings.items():
        if key in norm_name:
            return mapping
    
    # Default mapping
    return {'strand': 'Language Comprehension', 'pillar': 'To Be Determined', 'domain': 'To Be Determined'}

def generate_recommendations_report(prioritized: Dict, comparison: Dict) -> str:
    """Generate comprehensive recommendations report."""
    
    report = []
    report.append("# ELA Taxonomy Enhancement Recommendations")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("\n**Based on**: Duke 2021 & Scarborough's Reading Rope Framework Analysis")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## Executive Summary\n")
    total_concepts = len(comparison['convergent']) + len(comparison['duke_only']) + len(comparison['scarborough_only'])
    report.append(f"- **Total Concepts Analyzed**: {total_concepts}")
    report.append(f"- **Convergent Concepts** (both frameworks): {len(comparison['convergent'])}")
    report.append(f"- **Duke-Only Concepts**: {len(comparison['duke_only'])}")
    report.append(f"- **Scarborough-Only Concepts**: {len(comparison['scarborough_only'])}")
    report.append(f"- **Tier 1 Recommendations** (Critical): {len(prioritized['tier1'])}")
    report.append(f"- **Tier 2 Recommendations** (Important): {len(prioritized['tier2'])}")
    report.append(f"- **Tier 3 Recommendations** (Supplementary): {len(prioritized['tier3'])}")
    report.append("\n---\n")
    
    # Tier 1: Critical & Convergent
    report.append("## Tier 1: Critical & Convergent Concepts (IMMEDIATE INTEGRATION)\n")
    report.append("**Priority**: Highest - These concepts appear in BOTH frameworks, indicating strong scientific convergence.\n")
    
    for i, item in enumerate(prioritized['tier1'], 1):
        report.append(f"### {i}. {item['name']}\n")
        report.append(f"**Sources**: Both Duke 2021 and Scarborough")
        report.append(f"**Foundational**: {'Yes' if item['foundational'] else 'No'}")
        report.append(f"**Integration Complexity**: {item['integration_complexity']}")
        
        # Get descriptions from concepts
        for concept in item['concepts']:
            if concept.description:
                report.append(f"\n**Description** ({concept.source.title()}): {concept.description}")
        
        # Taxonomy mapping
        mapping = map_to_taxonomy_structure(item['name'])
        report.append(f"\n**Proposed Taxonomy Location**:")
        report.append(f"- Strand: `{mapping['strand']}`")
        report.append(f"- Pillar: `{mapping['pillar']}`")
        report.append(f"- Domain: `{mapping['domain']}`")
        
        report.append(f"\n**Rationale**: {item['rationale']}")
        report.append(f"\n**Action**: Add to taxonomy immediately as high-priority gap")
        report.append("\n---\n")
    
    # Tier 2: Important Single-Source
    report.append("## Tier 2: Important Single-Source Concepts (NEAR-TERM INTEGRATION)\n")
    report.append("**Priority**: High - Foundational concepts from one framework that fill significant gaps.\n")
    
    for i, item in enumerate(prioritized['tier2'], 1):
        report.append(f"### {i}. {item['name']}\n")
        concept = item['concepts'][0]
        report.append(f"**Source**: {concept.source.title()} framework only")
        report.append(f"**Foundational**: {'Yes' if item['foundational'] else 'No'}")
        
        if concept.description:
            report.append(f"\n**Description**: {concept.description}")
        
        mapping = map_to_taxonomy_structure(item['name'])
        report.append(f"\n**Proposed Taxonomy Location**:")
        report.append(f"- Strand: `{mapping['strand']}`")
        report.append(f"- Pillar: `{mapping['pillar']}`")
        report.append(f"- Domain: `{mapping['domain']}`")
        
        report.append(f"\n**Rationale**: {item['rationale']}")
        report.append("\n---\n")
    
    # Tier 3: Supplementary
    report.append("## Tier 3: Supplementary Concepts (FUTURE CONSIDERATION)\n")
    report.append("**Priority**: Medium - Specialized concepts for future enhancement.\n")
    
    for i, item in enumerate(prioritized['tier3'], 1):
        concept = item['concepts'][0]
        report.append(f"### {i}. {item['name']} ({concept.source.title()})\n")
        report.append(f"**Rationale**: {item['rationale']}\n")
    
    report.append("\n---\n")
    
    # Implementation Roadmap
    report.append("## Implementation Roadmap\n")
    report.append("### Phase 1: Immediate (0-1 month)")
    report.append(f"- Add all {len(prioritized['tier1'])} Tier 1 concepts (convergent evidence)")
    report.append("- Update taxonomy structure to accommodate new domains if needed")
    report.append("- Map to existing ROCK skills via batch mapping pipeline\n")
    
    report.append("### Phase 2: Near-term (1-3 months)")
    report.append(f"- Add {len(prioritized['tier2'])} Tier 2 concepts (important single-source)")
    report.append("- Conduct validation with reading science experts")
    report.append("- Enrich metadata (complexity bands, skill domains)\n")
    
    report.append("### Phase 3: Future (3-6 months)")
    report.append(f"- Evaluate {len(prioritized['tier3'])} Tier 3 concepts for inclusion")
    report.append("- Consider structural enhancements")
    report.append("- Continuous improvement based on new research\n")
    
    report.append("---\n")
    
    # Integration Guide
    report.append("## Integration Guide\n")
    report.append("### For Taxonomy Maintainers:\n")
    report.append("1. **Review Tier 1 concepts** - Start with convergent concepts")
    report.append("2. **Check proposed mappings** - Validate Strand/Pillar/Domain assignments")
    report.append("3. **Generate master concept IDs** - Use MC-ELA-#### format")
    report.append("4. **Run batch mapping** - Map concepts to ROCK skills")
    report.append("5. **Validate mappings** - Review and refine skill alignments")
    report.append("6. **Update taxonomy CSV** - Integrate approved concepts")
    report.append("7. **Document changes** - Track what was added and why\n")
    
    return '\n'.join(report)

def generate_comparison_report(comparison: Dict) -> str:
    """Generate detailed cross-framework comparison."""
    
    report = []
    report.append("# Cross-Framework Comparison: Duke 2021 vs Scarborough")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.append("---\n")
    
    report.append("## Convergent Concepts\n")
    report.append(f"**Count**: {len(comparison['convergent'])}\n")
    report.append("These concepts appear in BOTH frameworks, providing convergent scientific evidence:\n")
    
    for concept_name, concepts in comparison['convergent'].items():
        report.append(f"### {concept_name}")
        for concept in concepts:
            report.append(f"- **{concept.source.title()}**: {concept.name}")
            if concept.description:
                report.append(f"  - {concept.description[:200]}...")
        report.append("")
    
    report.append("\n## Duke 2021 Only\n")
    report.append(f"**Count**: {len(comparison['duke_only'])}\n")
    for concept in comparison['duke_only']:
        report.append(f"- {concept.name}")
    
    report.append("\n## Scarborough Only\n")
    report.append(f"**Count**: {len(comparison['scarborough_only'])}\n")
    for concept in comparison['scarborough_only']:
        report.append(f"- {concept.name}")
        if concept.description:
            report.append(f"  - {concept.description[:150]}...")
    
    return '\n'.join(report)

def create_integration_csv(prioritized: Dict, output_path: Path):
    """Create CSV of recommended concepts ready for integration."""
    
    concepts_to_integrate = []
    concept_id_counter = 100  # Start from MC-ELA-0100
    
    for tier_name, tier_concepts in [('tier1', prioritized['tier1']), 
                                      ('tier2', prioritized['tier2'])]:
        for item in tier_concepts:
            concept_id = f"MC-ELA-{concept_id_counter:04d}"
            concept_id_counter += 1
            
            # Get best description available
            description = ""
            grade_range = ""
            complexity_band = ""
            
            for concept in item['concepts']:
                if concept.description and not description:
                    description = concept.description
                if concept.grade_range and not grade_range:
                    grade_range = concept.grade_range
                if concept.complexity_band and not complexity_band:
                    complexity_band = concept.complexity_band
            
            mapping = map_to_taxonomy_structure(item['name'])
            
            concepts_to_integrate.append({
                'MASTER_CONCEPT_ID': concept_id,
                'MASTER_CONCEPT_NAME': item['name'],
                'DESCRIPTION': description or f"Concept from {', '.join(set(c.source for c in item['concepts']))} framework(s)",
                'SOR_STRAND': mapping['strand'],
                'SOR_PILLAR': mapping['pillar'],
                'SOR_DOMAIN': mapping['domain'],
                'COMPLEXITY_BAND': complexity_band or 'K-12',
                'GRADE_RANGE': grade_range or 'K-12',
                'PRIORITY_TIER': item['priority'],
                'SOURCE_FRAMEWORKS': ', '.join(set(c.source for c in item['concepts'])),
                'FOUNDATIONAL': 'Yes' if item['foundational'] else 'No',
                'INTEGRATION_COMPLEXITY': item['integration_complexity'],
                'SKILL_COUNT': 0,
                'AUTHORITY_COUNT': 0,
                'TEXT_TYPE': '',
                'TEXT_MODE': '',
                'SKILL_DOMAIN': 'reading',
                'PREREQUISITE_CONCEPT_ID': '',
                'EQUIVALENCE_GROUP_ID': '',
                'TAXONOMY_CONFIDENCE': 'High' if item['priority'] == 1 else 'Medium'
            })
    
    # Write CSV
    if concepts_to_integrate:
        fieldnames = list(concepts_to_integrate[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(concepts_to_integrate)
    
    return len(concepts_to_integrate)

def main():
    """Main execution function."""
    print("="*70)
    print("ELA FRAMEWORK COMPARISON & RECOMMENDATION GENERATOR")
    print("="*70)
    print()
    
    # Load concepts
    print("📊 Loading concepts from frameworks...")
    duke_concepts = load_duke_concepts()
    scarborough_concepts = load_scarborough_concepts()
    print(f"  - Duke 2021: {len(duke_concepts)} missing concepts")
    print(f"  - Scarborough: {len(scarborough_concepts)} missing concepts")
    print()
    
    # Identify convergent concepts
    print("🔍 Identifying convergent concepts...")
    comparison = identify_convergent_concepts(duke_concepts, scarborough_concepts)
    print(f"  - Convergent (both frameworks): {len(comparison['convergent'])}")
    print(f"  - Duke-only: {len(comparison['duke_only'])}")
    print(f"  - Scarborough-only: {len(comparison['scarborough_only'])}")
    print()
    
    # Prioritize concepts
    print("📋 Prioritizing concepts into tiers...")
    prioritized = prioritize_concepts(comparison)
    print(f"  - Tier 1 (Critical & Convergent): {len(prioritized['tier1'])}")
    print(f"  - Tier 2 (Important Single-Source): {len(prioritized['tier2'])}")
    print(f"  - Tier 3 (Supplementary): {len(prioritized['tier3'])}")
    print()
    
    # Generate reports
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print("📝 Generating comparison report...")
    comparison_report = generate_comparison_report(comparison)
    comparison_path = output_dir / "ela_framework_comparison.md"
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write(comparison_report)
    print(f"  ✅ Saved to: {comparison_path}")
    
    print("📝 Generating recommendations report...")
    recommendations_report = generate_recommendations_report(prioritized, comparison)
    recommendations_path = output_dir / "ela_taxonomy_recommendations.md"
    with open(recommendations_path, 'w', encoding='utf-8') as f:
        f.write(recommendations_report)
    print(f"  ✅ Saved to: {recommendations_path}")
    
    print("📝 Generating integration-ready CSV...")
    csv_path = output_dir / "recommended_ela_concepts.csv"
    count = create_integration_csv(prioritized, csv_path)
    print(f"  ✅ Saved {count} concepts to: {csv_path}")
    
    print()
    print("="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print()
    print("📁 Output files:")
    print(f"   - {comparison_path}")
    print(f"   - {recommendations_path}")
    print(f"   - {csv_path}")
    print()
    print("🎯 Next steps:")
    print("   1. Review the recommendations report")
    print("   2. Validate proposed taxonomy mappings")
    print("   3. Use the CSV to integrate concepts into taxonomy")
    print("   4. Run batch mapping on new concepts")
    print()

if __name__ == '__main__':
    main()

