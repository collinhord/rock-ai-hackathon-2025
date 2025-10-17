#!/usr/bin/env python3
"""
Framework Concept Tracker

Tracks which concepts appear across multiple authoritative frameworks
to assess scientific grounding and confidence levels.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class FrameworkTracker:
    """Track concept mentions across multiple frameworks."""
    
    def __init__(self, taxonomy_csv_path: str):
        """
        Initialize framework tracker.
        
        Args:
            taxonomy_csv_path: Path to taxonomy CSV
        """
        self.taxonomy_path = Path(taxonomy_csv_path)
        self.taxonomy_df = None
        self.taxonomy_concepts = []
        self.frameworks = {}
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Initializing Framework Tracker...")
        print(f"  Loading taxonomy from: {self.taxonomy_path}")
        
        self._load_taxonomy()
        
    def _load_taxonomy(self):
        """Load taxonomy and extract concepts."""
        self.taxonomy_df = pd.read_csv(self.taxonomy_path)
        print(f"  Loaded {len(self.taxonomy_df)} rows")
        
        hierarchy_cols = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        
        seen = set()
        for idx, row in self.taxonomy_df.iterrows():
            for level in hierarchy_cols:
                if level in self.taxonomy_df.columns and pd.notna(row[level]):
                    concept_name = str(row[level]).strip()
                    
                    # Build path
                    path_parts = []
                    for l in hierarchy_cols:
                        if l in self.taxonomy_df.columns and pd.notna(row[l]):
                            path_parts.append(str(row[l]))
                        if l == level:
                            break
                    
                    full_path = ' > '.join(path_parts)
                    unique_key = f"{level}::{full_path}"
                    
                    if unique_key not in seen:
                        seen.add(unique_key)
                        self.taxonomy_concepts.append({
                            'id': len(self.taxonomy_concepts),
                            'name': concept_name,
                            'level': level,
                            'path': full_path,
                            'frameworks_supporting': []
                        })
        
        print(f"  Extracted {len(self.taxonomy_concepts)} unique concepts")
    
    def load_framework(self, framework_name: str, extraction_json_path: str):
        """
        Load framework extraction from JSON.
        
        Args:
            framework_name: Name of framework (e.g., "Duke 2021")
            extraction_json_path: Path to extraction JSON file
        """
        print(f"\nLoading framework: {framework_name}")
        print(f"  From: {extraction_json_path}")
        
        path = Path(extraction_json_path)
        if not path.exists():
            print(f"  ⚠ File not found, skipping")
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract concepts from the framework
        concepts = []
        
        # Try multiple possible locations
        if 'extraction' in data:
            # Check for extracted_concepts
            if 'extracted_concepts' in data['extraction']:
                for concept in data['extraction']['extracted_concepts']:
                    concept_name = concept.get('name', '')
                    if concept_name:
                        concepts.append({
                            'name': concept_name,
                            'description': concept.get('description', ''),
                            'level': concept.get('level', ''),
                            'metadata': concept.get('subject_metadata', {})
                        })
            # Check for concepts
            elif 'concepts' in data['extraction']:
                for concept in data['extraction']['concepts']:
                    concept_name = concept.get('name', '')
                    if concept_name:
                        concepts.append({
                            'name': concept_name,
                            'description': concept.get('description', ''),
                            'level': concept.get('level', ''),
                            'metadata': concept.get('metadata', {})
                        })
        
        # Also check for gap_analysis format
        if len(concepts) == 0 and 'gap_analysis' in data:
            if 'new_concepts' in data['gap_analysis']:
                for concept in data['gap_analysis']['new_concepts']:
                    concept_name = concept.get('concept_name', concept.get('name', ''))
                    if concept_name:
                        concepts.append({
                            'name': concept_name,
                            'description': concept.get('description', ''),
                            'level': '',
                            'metadata': {}
                        })
        
        self.frameworks[framework_name] = {
            'concepts': concepts,
            'source_file': str(path),
            'concept_count': len(concepts)
        }
        
        print(f"  Loaded {len(concepts)} concepts")
    
    def match_frameworks_to_taxonomy(self, similarity_threshold: float = 0.75):
        """
        Match framework concepts to taxonomy concepts using semantic similarity.
        
        Args:
            similarity_threshold: Minimum similarity for a match
        """
        print(f"\nMatching frameworks to taxonomy (threshold: {similarity_threshold})...")
        
        if not self.frameworks:
            print("  No frameworks loaded")
            return
        
        # Generate embeddings for taxonomy concepts
        print("  Generating taxonomy embeddings...")
        taxonomy_texts = [c['name'] for c in self.taxonomy_concepts]
        taxonomy_embeddings = self.model.encode(taxonomy_texts, show_progress_bar=False)
        
        # Process each framework
        for framework_name, framework_data in self.frameworks.items():
            print(f"\n  Processing {framework_name}...")
            
            if not framework_data['concepts']:
                continue
            
            # Generate embeddings for framework concepts
            framework_texts = [c['name'] for c in framework_data['concepts']]
            framework_embeddings = self.model.encode(framework_texts, show_progress_bar=False)
            
            # Calculate similarity matrix
            sim_matrix = cosine_similarity(taxonomy_embeddings, framework_embeddings)
            
            # Find matches
            matches = 0
            for tax_idx, tax_concept in enumerate(self.taxonomy_concepts):
                # Find best match for this taxonomy concept
                best_match_idx = np.argmax(sim_matrix[tax_idx])
                best_similarity = sim_matrix[tax_idx, best_match_idx]
                
                if best_similarity >= similarity_threshold:
                    framework_concept = framework_data['concepts'][best_match_idx]
                    tax_concept['frameworks_supporting'].append({
                        'framework': framework_name,
                        'matched_concept': framework_concept['name'],
                        'similarity': float(best_similarity),
                        'confidence': 'high' if best_similarity >= 0.85 else 'medium'
                    })
                    matches += 1
            
            print(f"    Matched {matches} taxonomy concepts to {framework_name}")
    
    def calculate_convergence_scores(self) -> pd.DataFrame:
        """
        Calculate convergence scores for all taxonomy concepts.
        
        Returns:
            DataFrame with convergence analysis
        """
        print(f"\nCalculating convergence scores...")
        
        results = []
        
        for concept in self.taxonomy_concepts:
            frameworks_supporting = concept['frameworks_supporting']
            convergence_score = len(frameworks_supporting)
            
            # Classify evidence strength
            if convergence_score >= 3:
                strength = 'strong'
                recommendation = 'Keep - strong multi-framework support'
            elif convergence_score == 2:
                strength = 'moderate'
                recommendation = 'Keep - solid evidence from 2 frameworks'
            elif convergence_score == 1:
                strength = 'weak'
                recommendation = 'Review - single-framework support, seek additional evidence'
            else:
                strength = 'unvalidated'
                recommendation = 'Review - no framework support found'
            
            # Get framework names
            framework_names = [f['framework'] for f in frameworks_supporting]
            
            results.append({
                'Concept_ID': concept['id'],
                'Concept_Name': concept['name'],
                'Taxonomy_Level': concept['level'],
                'Taxonomy_Path': concept['path'],
                'Convergence_Score': convergence_score,
                'Frameworks': ', '.join(framework_names) if framework_names else 'None',
                'Evidence_Strength': strength,
                'Recommendation': recommendation,
                'Framework_Details': str(frameworks_supporting) if frameworks_supporting else ''
            })
        
        df = pd.DataFrame(results)
        
        # Summary statistics
        print(f"\n  Summary Statistics:")
        print(f"    Total concepts: {len(df)}")
        print(f"    Strong evidence (3+ frameworks): {len(df[df['Evidence_Strength'] == 'strong'])}")
        print(f"    Moderate evidence (2 frameworks): {len(df[df['Evidence_Strength'] == 'moderate'])}")
        print(f"    Weak evidence (1 framework): {len(df[df['Evidence_Strength'] == 'weak'])}")
        print(f"    Unvalidated (0 frameworks): {len(df[df['Evidence_Strength'] == 'unvalidated'])}")
        
        return df
    
    def generate_convergence_report(self, convergence_df: pd.DataFrame, output_dir: str = 'validation_outputs'):
        """
        Generate convergence analysis reports.
        
        Args:
            convergence_df: DataFrame from calculate_convergence_scores
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\nGenerating convergence reports...")
        
        # Save CSV
        csv_path = output_path / 'concept_confidence.csv'
        convergence_df.to_csv(csv_path, index=False)
        print(f"  ✓ Saved: {csv_path}")
        
        # Generate markdown report
        report_lines = self._generate_convergence_markdown(convergence_df)
        
        report_path = output_path / 'framework_convergence_summary.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"  ✓ Saved: {report_path}")
        
        # Generate coverage matrix
        self._generate_coverage_matrix(convergence_df, output_path)
        
        return output_path
    
    def _generate_convergence_markdown(self, df: pd.DataFrame) -> List[str]:
        """Generate markdown convergence report."""
        lines = []
        
        lines.append("# Framework Convergence Analysis")
        lines.append(f"\n**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Frameworks Analyzed**: {len(self.frameworks)}")
        lines.append("\n---\n")
        
        # Framework list
        lines.append("## Frameworks Included\n")
        for name, data in self.frameworks.items():
            lines.append(f"- **{name}**: {data['concept_count']} concepts")
        lines.append("")
        
        # Summary statistics
        lines.append("## Summary Statistics\n")
        lines.append("```")
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│     FRAMEWORK CONVERGENCE ANALYSIS                      │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append("│                                                          │")
        lines.append(f"│  Total taxonomy concepts:              {len(df):5}          │")
        lines.append(f"│  Concepts with strong evidence (3+):   {len(df[df['Evidence_Strength'] == 'strong']):5}          │")
        lines.append(f"│  Concepts with moderate evidence (2):  {len(df[df['Evidence_Strength'] == 'moderate']):5}          │")
        lines.append(f"│  Concepts with weak evidence (1):      {len(df[df['Evidence_Strength'] == 'weak']):5}          │")
        lines.append(f"│  Unvalidated concepts (0):             {len(df[df['Evidence_Strength'] == 'unvalidated']):5}          │")
        lines.append("│                                                          │")
        lines.append("└─────────────────────────────────────────────────────────┘")
        lines.append("```\n")
        
        # High-confidence concepts
        strong_concepts = df[df['Evidence_Strength'] == 'strong'].sort_values('Convergence_Score', ascending=False)
        
        lines.append(f"## High-Confidence Concepts ({len(strong_concepts)} concepts)\n")
        if len(strong_concepts) > 0:
            lines.append("These concepts appear in 3+ frameworks:\n")
            for _, row in strong_concepts.head(20).iterrows():
                lines.append(f"- **{row['Concept_Name']}** ({row['Convergence_Score']} frameworks: {row['Frameworks']})")
                lines.append(f"  - Location: `{row['Taxonomy_Path']}`\n")
            
            if len(strong_concepts) > 20:
                lines.append(f"\n*... and {len(strong_concepts) - 20} more. See CSV for full list.*\n")
        else:
            lines.append("No concepts found in 3+ frameworks.\n")
        
        # Moderate evidence
        moderate_concepts = df[df['Evidence_Strength'] == 'moderate'].sort_values('Convergence_Score', ascending=False)
        
        lines.append(f"## Moderate-Evidence Concepts ({len(moderate_concepts)} concepts)\n")
        if len(moderate_concepts) > 0:
            lines.append("These concepts appear in 2 frameworks:\n")
            for _, row in moderate_concepts.head(15).iterrows():
                lines.append(f"- **{row['Concept_Name']}** ({row['Frameworks']})")
                lines.append(f"  - `{row['Taxonomy_Path']}`\n")
            
            if len(moderate_concepts) > 15:
                lines.append(f"\n*... and {len(moderate_concepts) - 15} more.*\n")
        else:
            lines.append("No concepts found in exactly 2 frameworks.\n")
        
        # Single-source concepts
        weak_concepts = df[df['Evidence_Strength'] == 'weak'].head(20)
        
        lines.append(f"## Single-Source Concepts (Weak Evidence)\n")
        lines.append(f"Found {len(df[df['Evidence_Strength'] == 'weak'])} concepts in only 1 framework.\n")
        lines.append("**Recommendation**: Seek additional evidence or flag for expert review.\n")
        
        if len(weak_concepts) > 0:
            lines.append("Sample concepts:\n")
            for _, row in weak_concepts.iterrows():
                lines.append(f"- {row['Concept_Name']} (from {row['Frameworks']})")
            lines.append("")
        
        # Unvalidated concepts
        unvalidated = df[df['Evidence_Strength'] == 'unvalidated']
        
        lines.append(f"## Unvalidated Concepts ({len(unvalidated)} concepts)\n")
        lines.append("These taxonomy concepts were not found in any loaded frameworks.\n")
        lines.append("**Note**: This may indicate:\n")
        lines.append("- Concepts are more granular than framework concepts\n")
        lines.append("- Concepts use different terminology\n")
        lines.append("- Concepts are novel/custom to this taxonomy\n")
        lines.append("- Need to load additional frameworks\n")
        
        # Recommendations
        lines.append("## Recommendations\n")
        
        validated_pct = 100 * (len(df) - len(unvalidated)) / len(df) if len(df) > 0 else 0
        
        lines.append(f"### Overall Coverage: {validated_pct:.1f}%\n")
        
        if validated_pct >= 80:
            lines.append("✅ **Excellent**: High proportion of concepts validated by frameworks")
        elif validated_pct >= 60:
            lines.append("✅ **Good**: Majority of concepts have framework support")
        elif validated_pct >= 40:
            lines.append("⚠️ **Moderate**: Many concepts lack framework validation")
        else:
            lines.append("⚠️ **Low**: Significant number of unvalidated concepts")
        
        lines.append("\n### Action Items\n")
        lines.append("1. **High Priority**: Review strong-evidence concepts for completeness")
        lines.append("2. **Medium Priority**: Validate single-source concepts with additional frameworks")
        lines.append("3. **Low Priority**: Assess unvalidated concepts - determine if novel or need different terminology")
        lines.append("4. **Ongoing**: Add new frameworks to increase validation coverage\n")
        
        lines.append("---\n")
        lines.append("*Generated by Framework Convergence Tracker*")
        
        return lines
    
    def _generate_coverage_matrix(self, df: pd.DataFrame, output_path: Path):
        """Generate coverage matrix showing which frameworks support which concepts."""
        print(f"  Generating coverage matrix...")
        
        # Get top concepts by convergence
        top_concepts = df.nlargest(30, 'Convergence_Score')
        
        matrix_lines = []
        matrix_lines.append("# Framework Coverage Matrix\n")
        matrix_lines.append("Top 30 concepts by framework support:\n")
        matrix_lines.append("```")
        
        # Header
        framework_names = list(self.frameworks.keys())
        header = "Concept".ljust(40)
        for fw in framework_names:
            header += " | " + fw[:10].ljust(10)
        matrix_lines.append(header)
        matrix_lines.append("-" * len(header))
        
        # Rows
        for _, row in top_concepts.iterrows():
            concept_name = row['Concept_Name'][:38]
            line = concept_name.ljust(40)
            
            supporting_frameworks = row['Frameworks'].split(', ') if row['Frameworks'] != 'None' else []
            
            for fw in framework_names:
                if fw in supporting_frameworks:
                    line += " |     ✓     "
                else:
                    line += " |           "
            
            matrix_lines.append(line)
        
        matrix_lines.append("```\n")
        
        matrix_path = output_path / 'framework_coverage_matrix.md'
        with open(matrix_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(matrix_lines))
        
        print(f"  ✓ Saved: {matrix_path}")

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Framework Convergence Tracker")
    parser.add_argument('--taxonomy', '-t', type=str,
                        default='../POC_science_of_reading_literacy_skills_taxonomy.csv',
                        help='Path to taxonomy CSV')
    parser.add_argument('--output', '-o', type=str,
                        default='validation_outputs',
                        help='Output directory')
    
    args = parser.parse_args()
    
    print("="*70)
    print("FRAMEWORK CONVERGENCE TRACKER")
    print("="*70)
    
    # Initialize tracker
    tracker = FrameworkTracker(args.taxonomy)
    
    # Load frameworks
    print("\n" + "="*70)
    print("LOADING FRAMEWORKS")
    print("="*70)
    
    # Duke 2021
    tracker.load_framework(
        "Duke 2021",
        "output/my_first_run/Reading Research Quarterly - 2021 - Duke - The Science of Reading Progresses  Communicating Advances Beyond the Simple View_gap_analysis.json"
    )
    
    # Scarborough
    tracker.load_framework(
        "Scarborough Reading Rope",
        "output/scarborough_full/extraction/Scarborough-Reading-Rope-Key-Ideas-Behind-the-Metaphor_extraction.json"
    )
    
    # Cambridge Math
    tracker.load_framework(
        "Cambridge Mathematics",
        "output/cambridge_full/extraction/cambridge_mathematics_ontology_extraction.json"
    )
    
    # Match frameworks to taxonomy
    print("\n" + "="*70)
    print("MATCHING FRAMEWORKS TO TAXONOMY")
    print("="*70)
    tracker.match_frameworks_to_taxonomy(similarity_threshold=0.75)
    
    # Calculate convergence
    print("\n" + "="*70)
    print("CALCULATING CONVERGENCE")
    print("="*70)
    convergence_df = tracker.calculate_convergence_scores()
    
    # Generate reports
    print("\n" + "="*70)
    print("GENERATING REPORTS")
    print("="*70)
    output_path = tracker.generate_convergence_report(convergence_df, args.output)
    
    print(f"\n{'='*70}")
    print("CONVERGENCE ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Reports saved to: {output_path}")

if __name__ == '__main__':
    main()

