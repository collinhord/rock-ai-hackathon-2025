#!/usr/bin/env python3
"""
Semantic Similarity Validator for Taxonomy

Detects potential duplicate or highly similar concepts within the literacy taxonomy
using semantic embeddings and cosine similarity.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticValidator:
    """
    Validates taxonomy for semantic duplicates and overlaps using embeddings.
    """
    
    def __init__(self, taxonomy_csv_path: str, similarity_threshold: float = 0.85):
        """
        Initialize the semantic validator.
        
        Args:
            taxonomy_csv_path: Path to taxonomy CSV file
            similarity_threshold: Threshold for flagging similar concepts (default 0.85)
        """
        self.taxonomy_path = Path(taxonomy_csv_path)
        self.threshold = similarity_threshold
        self.df = None
        self.concepts = []
        self.embeddings = None
        self.similarity_matrix = None
        
        print(f"Initializing Semantic Validator...")
        print(f"  Similarity threshold: {self.threshold}")
        print(f"  Loading model: all-MiniLM-L6-v2...")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"  ✓ Model loaded successfully")
        
    def load_concepts(self) -> List[Dict]:
        """
        Load and extract all concepts from taxonomy with full context.
        
        Returns:
            List of concept dictionaries with metadata
        """
        print(f"\nLoading taxonomy from: {self.taxonomy_path}")
        self.df = pd.read_csv(self.taxonomy_path)
        print(f"  Loaded {len(self.df)} rows")
        
        hierarchy_cols = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        
        concepts = []
        seen = set()
        
        for idx, row in self.df.iterrows():
            for level in hierarchy_cols:
                if level in self.df.columns and pd.notna(row[level]):
                    concept_name = str(row[level]).strip()
                    
                    # Build full path for context
                    path_parts = []
                    for l in hierarchy_cols:
                        if l in self.df.columns and pd.notna(row[l]):
                            path_parts.append(str(row[l]))
                        if l == level:
                            break
                    
                    full_path = ' > '.join(path_parts)
                    
                    # Create unique key
                    unique_key = f"{level}::{full_path}"
                    
                    if unique_key not in seen:
                        seen.add(unique_key)
                        
                        # Get annotation if available
                        annotation = ""
                        if 'Skill Subset Annotation' in self.df.columns and pd.notna(row['Skill Subset Annotation']):
                            annotation = str(row['Skill Subset Annotation'])
                        
                        # Build rich text for embedding
                        # Include: concept name + parent context + annotation
                        parent_context = ' > '.join(path_parts[:-1]) if len(path_parts) > 1 else ""
                        
                        embed_text = concept_name
                        if parent_context:
                            embed_text += f" (context: {parent_context})"
                        if annotation and level == 'Skill Subset':
                            # Only use annotation for most specific level to avoid noise
                            embed_text += f" - {annotation[:200]}"  # Limit annotation length
                        
                        concepts.append({
                            'id': len(concepts),
                            'name': concept_name,
                            'level': level,
                            'path': full_path,
                            'parent_context': parent_context,
                            'annotation': annotation,
                            'embed_text': embed_text,
                            'row_idx': idx
                        })
        
        self.concepts = concepts
        print(f"  Extracted {len(concepts)} unique concepts across all levels")
        
        # Show distribution by level
        level_counts = defaultdict(int)
        for c in concepts:
            level_counts[c['level']] += 1
        
        print(f"\n  Concept distribution by level:")
        for level in hierarchy_cols:
            if level in level_counts:
                print(f"    {level:15}: {level_counts[level]:4} concepts")
        
        return concepts
    
    def generate_embeddings(self):
        """
        Generate semantic embeddings for all concepts.
        """
        print(f"\nGenerating semantic embeddings...")
        
        if not self.concepts:
            raise ValueError("No concepts loaded. Call load_concepts() first.")
        
        texts = [c['embed_text'] for c in self.concepts]
        
        print(f"  Encoding {len(texts)} concepts...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        
        print(f"  ✓ Generated embeddings: shape {self.embeddings.shape}")
        
    def calculate_similarity_matrix(self):
        """
        Calculate pairwise cosine similarity matrix.
        """
        print(f"\nCalculating similarity matrix...")
        
        if self.embeddings is None:
            raise ValueError("No embeddings. Call generate_embeddings() first.")
        
        self.similarity_matrix = cosine_similarity(self.embeddings)
        
        print(f"  ✓ Similarity matrix: {self.similarity_matrix.shape}")
        
        # Set diagonal to 0 (ignore self-similarity)
        np.fill_diagonal(self.similarity_matrix, 0)
        
    def find_similar_pairs(self, min_similarity: float = None) -> List[Dict]:
        """
        Find pairs of concepts with high similarity.
        
        Args:
            min_similarity: Minimum similarity threshold (uses self.threshold if None)
            
        Returns:
            List of similar pairs with metadata
        """
        if min_similarity is None:
            min_similarity = self.threshold
        
        print(f"\nFinding similar pairs (threshold: {min_similarity})...")
        
        similar_pairs = []
        
        n = len(self.concepts)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.similarity_matrix[i, j]
                
                if sim >= min_similarity:
                    c1 = self.concepts[i]
                    c2 = self.concepts[j]
                    
                    similar_pairs.append({
                        'concept1_id': c1['id'],
                        'concept1_name': c1['name'],
                        'concept1_level': c1['level'],
                        'concept1_path': c1['path'],
                        'concept2_id': c2['id'],
                        'concept2_name': c2['name'],
                        'concept2_level': c2['level'],
                        'concept2_path': c2['path'],
                        'similarity': sim,
                        'same_level': c1['level'] == c2['level'],
                        'same_strand': c1['path'].split(' > ')[0] == c2['path'].split(' > ')[0] if ' > ' in c1['path'] and ' > ' in c2['path'] else False
                    })
        
        # Sort by similarity (highest first)
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"  Found {len(similar_pairs)} pairs above threshold")
        
        return similar_pairs
    
    def analyze_siblings(self) -> List[Dict]:
        """
        Analyze similarity between sibling concepts (same parent, same level).
        Siblings should ideally be distinct (< threshold).
        
        Returns:
            List of similar siblings that may indicate issues
        """
        print(f"\nAnalyzing sibling similarity...")
        
        # Group concepts by parent
        siblings_by_parent = defaultdict(list)
        
        for concept in self.concepts:
            parent_key = f"{concept['level']}::{concept['parent_context']}"
            siblings_by_parent[parent_key].append(concept)
        
        sibling_conflicts = []
        
        for parent_key, siblings in siblings_by_parent.items():
            if len(siblings) < 2:
                continue
            
            # Check all sibling pairs
            for i in range(len(siblings)):
                for j in range(i + 1, len(siblings)):
                    c1 = siblings[i]
                    c2 = siblings[j]
                    
                    sim = self.similarity_matrix[c1['id'], c2['id']]
                    
                    if sim >= self.threshold:
                        sibling_conflicts.append({
                            'parent': c1['parent_context'],
                            'level': c1['level'],
                            'concept1_name': c1['name'],
                            'concept1_path': c1['path'],
                            'concept2_name': c2['name'],
                            'concept2_path': c2['path'],
                            'similarity': sim,
                            'issue': 'High similarity between siblings'
                        })
        
        sibling_conflicts.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"  Found {len(sibling_conflicts)} sibling pairs with high similarity")
        
        return sibling_conflicts
    
    def analyze_cross_strand(self, high_threshold: float = 0.90) -> List[Dict]:
        """
        Analyze concepts across different strands with very high similarity.
        May indicate duplication or misplacement.
        
        Args:
            high_threshold: Threshold for cross-strand duplicates (default 0.90)
            
        Returns:
            List of cross-strand high-similarity pairs
        """
        print(f"\nAnalyzing cross-strand similarity (threshold: {high_threshold})...")
        
        cross_strand = []
        
        n = len(self.concepts)
        for i in range(n):
            for j in range(i + 1, n):
                c1 = self.concepts[i]
                c2 = self.concepts[j]
                
                # Check if different strands
                strand1 = c1['path'].split(' > ')[0] if ' > ' in c1['path'] else c1['name']
                strand2 = c2['path'].split(' > ')[0] if ' > ' in c2['path'] else c2['name']
                
                if strand1 != strand2:
                    sim = self.similarity_matrix[i, j]
                    
                    if sim >= high_threshold:
                        cross_strand.append({
                            'strand1': strand1,
                            'concept1_name': c1['name'],
                            'concept1_path': c1['path'],
                            'strand2': strand2,
                            'concept2_name': c2['name'],
                            'concept2_path': c2['path'],
                            'similarity': sim,
                            'issue': 'Very high similarity across different strands - potential duplication'
                        })
        
        cross_strand.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"  Found {len(cross_strand)} cross-strand pairs with very high similarity")
        
        return cross_strand
    
    def analyze_parent_child(self, max_acceptable: float = 0.95) -> List[Dict]:
        """
        Analyze parent-child relationships.
        Children should be related but not identical to parents.
        
        Args:
            max_acceptable: Maximum acceptable similarity (default 0.95)
            
        Returns:
            List of parent-child pairs with too-high similarity
        """
        print(f"\nAnalyzing parent-child relationships...")
        
        hierarchy_order = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        
        parent_child_issues = []
        
        for concept in self.concepts:
            # Find parent
            if not concept['parent_context']:
                continue
            
            parent_name = concept['parent_context'].split(' > ')[-1]
            
            # Find parent concept
            for potential_parent in self.concepts:
                if potential_parent['name'] == parent_name and potential_parent['path'] == concept['parent_context']:
                    # Check similarity
                    sim = self.similarity_matrix[concept['id'], potential_parent['id']]
                    
                    if sim >= max_acceptable:
                        parent_child_issues.append({
                            'parent_name': potential_parent['name'],
                            'parent_level': potential_parent['level'],
                            'child_name': concept['name'],
                            'child_level': concept['level'],
                            'child_path': concept['path'],
                            'similarity': sim,
                            'issue': 'Child nearly identical to parent - may indicate redundancy'
                        })
                    break
        
        parent_child_issues.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"  Found {len(parent_child_issues)} parent-child pairs with very high similarity")
        
        return parent_child_issues
    
    def generate_report(self, output_dir: str = 'validation_outputs') -> Dict:
        """
        Generate comprehensive validation report.
        
        Args:
            output_dir: Directory for output files
            
        Returns:
            Dictionary with all analysis results
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"GENERATING VALIDATION REPORT")
        print(f"{'='*70}")
        
        # Run all analyses
        all_similar = self.find_similar_pairs()
        high_similar = self.find_similar_pairs(min_similarity=0.90)
        sibling_conflicts = self.analyze_siblings()
        cross_strand = self.analyze_cross_strand()
        parent_child = self.analyze_parent_child()
        
        # Save similarity matrix
        matrix_path = output_path / 'similarity_matrix.csv'
        matrix_df = pd.DataFrame(
            self.similarity_matrix,
            index=[f"{c['id']}:{c['name']}" for c in self.concepts],
            columns=[f"{c['id']}:{c['name']}" for c in self.concepts]
        )
        matrix_df.to_csv(matrix_path)
        print(f"\n✓ Saved similarity matrix: {matrix_path}")
        
        # Save potential duplicates
        if all_similar:
            duplicates_df = pd.DataFrame(all_similar)
            duplicates_path = output_path / 'potential_duplicates.csv'
            duplicates_df.to_csv(duplicates_path, index=False)
            print(f"✓ Saved potential duplicates: {duplicates_path}")
        
        # Save sibling conflicts
        if sibling_conflicts:
            siblings_df = pd.DataFrame(sibling_conflicts)
            siblings_path = output_path / 'sibling_conflicts.csv'
            siblings_df.to_csv(siblings_path, index=False)
            print(f"✓ Saved sibling conflicts: {siblings_path}")
        
        # Generate markdown report
        report_lines = self._generate_markdown_report(
            all_similar, high_similar, sibling_conflicts, cross_strand, parent_child
        )
        
        report_path = output_path / 'semantic_validation_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"✓ Saved detailed report: {report_path}")
        
        print(f"\n{'='*70}")
        print(f"VALIDATION COMPLETE")
        print(f"{'='*70}")
        
        return {
            'all_similar': all_similar,
            'high_similar': high_similar,
            'sibling_conflicts': sibling_conflicts,
            'cross_strand': cross_strand,
            'parent_child': parent_child,
            'output_dir': str(output_path)
        }
    
    def _generate_markdown_report(self, all_similar, high_similar, sibling_conflicts, 
                                   cross_strand, parent_child) -> List[str]:
        """Generate markdown report content."""
        lines = []
        
        lines.append("# Semantic Similarity Validation Report")
        lines.append(f"\n**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Taxonomy**: {self.taxonomy_path.name}")
        lines.append(f"**Total Concepts Analyzed**: {len(self.concepts):,}")
        lines.append(f"**Similarity Threshold**: {self.threshold}")
        lines.append("\n---\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append("```")
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│       SEMANTIC VALIDATION RESULTS                        │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append("│                                                          │")
        lines.append(f"│  High-priority duplicates (>0.90):    {len(high_similar):4} pairs        │")
        lines.append(f"│  Medium-priority overlaps (≥0.85):    {len(all_similar):4} pairs        │")
        lines.append(f"│  Sibling conflicts:                   {len(sibling_conflicts):4} pairs        │")
        lines.append(f"│  Cross-strand duplicates:             {len(cross_strand):4} pairs        │")
        lines.append(f"│  Parent-child redundancies:           {len(parent_child):4} pairs        │")
        lines.append("│                                                          │")
        lines.append("└─────────────────────────────────────────────────────────┘")
        lines.append("```\n")
        
        # Interpretation
        lines.append("## Interpretation Guide\n")
        lines.append("- **High-priority (>0.90)**: Very likely duplicates or near-duplicates requiring immediate review")
        lines.append("- **Medium-priority (0.85-0.90)**: Significant overlap, may indicate redundancy or need for clarification")
        lines.append("- **Sibling conflicts**: Concepts at same level under same parent should be distinct")
        lines.append("- **Cross-strand**: High similarity across different strands may indicate misplacement")
        lines.append("- **Parent-child**: Children nearly identical to parents suggest possible redundancy\n")
        
        # High-Priority Duplicates
        lines.append("## High-Priority Duplicates (>0.90 Similarity)\n")
        if high_similar:
            lines.append(f"Found {len(high_similar)} pairs with very high similarity:\n")
            for i, pair in enumerate(high_similar[:20], 1):  # Show top 20
                lines.append(f"### {i}. Similarity: {pair['similarity']:.3f}\n")
                lines.append(f"**Concept 1**: `{pair['concept1_name']}`")
                lines.append(f"- Level: {pair['concept1_level']}")
                lines.append(f"- Path: {pair['concept1_path']}\n")
                lines.append(f"**Concept 2**: `{pair['concept2_name']}`")
                lines.append(f"- Level: {pair['concept2_level']}")
                lines.append(f"- Path: {pair['concept2_path']}\n")
                lines.append(f"**Same Level**: {pair['same_level']}")
                lines.append(f"**Same Strand**: {pair['same_strand']}\n")
                lines.append("**Recommendation**: Review for potential consolidation or disambiguation\n")
                lines.append("---\n")
            
            if len(high_similar) > 20:
                lines.append(f"\n*... and {len(high_similar) - 20} more. See `potential_duplicates.csv` for full list.*\n")
        else:
            lines.append("✓ No high-priority duplicates found!\n")
        
        # Medium-Priority Overlaps
        lines.append("## Medium-Priority Overlaps (0.85-0.90 Similarity)\n")
        medium = [p for p in all_similar if 0.85 <= p['similarity'] < 0.90]
        if medium:
            lines.append(f"Found {len(medium)} pairs with significant overlap:\n")
            for i, pair in enumerate(medium[:10], 1):  # Show top 10
                lines.append(f"{i}. **{pair['concept1_name']}** ↔ **{pair['concept2_name']}** (sim: {pair['similarity']:.3f})")
                lines.append(f"   - Paths: `{pair['concept1_path']}` vs `{pair['concept2_path']}`\n")
            
            if len(medium) > 10:
                lines.append(f"\n*... and {len(medium) - 10} more. See `potential_duplicates.csv`.*\n")
        else:
            lines.append("✓ No medium-priority overlaps found!\n")
        
        # Sibling Conflicts
        lines.append("## Sibling Conflicts\n")
        if sibling_conflicts:
            lines.append(f"Found {len(sibling_conflicts)} pairs of siblings with high similarity:\n")
            lines.append("Siblings (concepts at the same level with same parent) should be distinct.\n")
            for i, conflict in enumerate(sibling_conflicts[:15], 1):
                lines.append(f"\n### {i}. Under Parent: `{conflict['parent']}`\n")
                lines.append(f"- **{conflict['concept1_name']}** ↔ **{conflict['concept2_name']}**")
                lines.append(f"- Similarity: {conflict['similarity']:.3f}")
                lines.append(f"- Level: {conflict['level']}\n")
                lines.append(f"**Recommendation**: These siblings may be too similar - consider merging or clarifying distinction\n")
            
            if len(sibling_conflicts) > 15:
                lines.append(f"\n*... and {len(sibling_conflicts) - 15} more conflicts.*\n")
        else:
            lines.append("✓ No significant sibling conflicts found!\n")
        
        # Cross-Strand Analysis
        lines.append("## Cross-Strand High Similarity\n")
        if cross_strand:
            lines.append(f"Found {len(cross_strand)} pairs with high similarity across different strands:\n")
            for i, pair in enumerate(cross_strand[:10], 1):
                lines.append(f"\n{i}. **{pair['concept1_name']}** (in `{pair['strand1']}`) ↔ **{pair['concept2_name']}** (in `{pair['strand2']}`) ")
                lines.append(f"   - Similarity: {pair['similarity']:.3f}")
                lines.append(f"   - {pair['issue']}\n")
            
            if len(cross_strand) > 10:
                lines.append(f"\n*... and {len(cross_strand) - 10} more cross-strand pairs.*\n")
        else:
            lines.append("✓ No significant cross-strand duplicates found!\n")
        
        # Parent-Child Analysis
        lines.append("## Parent-Child Redundancy\n")
        if parent_child:
            lines.append(f"Found {len(parent_child)} parent-child pairs with very high similarity:\n")
            for i, pair in enumerate(parent_child[:10], 1):
                lines.append(f"\n{i}. Parent: **{pair['parent_name']}** ({pair['parent_level']}) → Child: **{pair['child_name']}** ({pair['child_level']})")
                lines.append(f"   - Similarity: {pair['similarity']:.3f}")
                lines.append(f"   - Path: `{pair['child_path']}`")
                lines.append(f"   - {pair['issue']}\n")
        else:
            lines.append("✓ No significant parent-child redundancies found!\n")
        
        # Recommendations
        lines.append("## Overall Recommendations\n")
        lines.append("Based on this semantic analysis:\n")
        
        total_issues = len(high_similar) + len([p for p in all_similar if 0.85 <= p['similarity'] < 0.90])
        
        if total_issues == 0:
            lines.append("✅ **Excellent**: No significant semantic duplicates or overlaps detected.")
            lines.append("   Your taxonomy appears to have strong MECE properties (Mutually Exclusive).\n")
        elif total_issues <= 10:
            lines.append("✅ **Good**: Only a few potential overlaps detected.")
            lines.append(f"   - Review the {total_issues} flagged pairs")
            lines.append("   - Most are likely acceptable given different contexts\n")
        elif total_issues <= 30:
            lines.append("⚠️ **Moderate**: Several potential overlaps detected.")
            lines.append(f"   - {len(high_similar)} high-priority duplicates need review")
            lines.append("   - Focus on high-priority items first")
            lines.append("   - Consider clarifying distinctions in annotations\n")
        else:
            lines.append("⚠️ **Attention Needed**: Many potential overlaps detected.")
            lines.append(f"   - {len(high_similar)} high-priority duplicates")
            lines.append(f"   - {len([p for p in all_similar if 0.85 <= p['similarity'] < 0.90])} medium-priority overlaps")
            lines.append("   - Recommend systematic review and consolidation")
            lines.append("   - May indicate need for reorganization\n")
        
        lines.append("### Next Steps\n")
        lines.append("1. Review high-priority duplicates (>0.90) for consolidation")
        lines.append("2. Examine sibling conflicts - clarify or merge as needed")
        lines.append("3. Investigate cross-strand similarities for potential misplacement")
        lines.append("4. Consider adding clearer distinction criteria in annotations")
        lines.append("5. Update taxonomy based on findings")
        lines.append("6. Re-run validation to verify improvements\n")
        
        lines.append("---\n")
        lines.append("*Generated by Semantic Validator using sentence-transformers (all-MiniLM-L6-v2)*")
        
        return lines

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Semantic Similarity Validator for Taxonomy",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--taxonomy', '-t',
        type=str,
        default='../POC_science_of_reading_literacy_skills_taxonomy.csv',
        help='Path to taxonomy CSV file'
    )
    parser.add_argument(
        '--threshold', '-s',
        type=float,
        default=0.85,
        help='Similarity threshold for flagging duplicates (default: 0.85)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='validation_outputs',
        help='Output directory for reports (default: validation_outputs)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("SEMANTIC SIMILARITY VALIDATOR")
    print("="*70)
    print()
    
    # Initialize validator
    validator = SemanticValidator(args.taxonomy, args.threshold)
    
    # Load concepts
    validator.load_concepts()
    
    # Generate embeddings
    validator.generate_embeddings()
    
    # Calculate similarity
    validator.calculate_similarity_matrix()
    
    # Generate report
    results = validator.generate_report(args.output)
    
    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Concepts analyzed: {len(validator.concepts)}")
    print(f"High-priority duplicates (>0.90): {len(results['high_similar'])}")
    print(f"Medium-priority overlaps (≥0.85): {len(results['all_similar'])}")
    print(f"Sibling conflicts: {len(results['sibling_conflicts'])}")
    print(f"Cross-strand issues: {len(results['cross_strand'])}")
    print(f"Parent-child redundancies: {len(results['parent_child'])}")
    print(f"\nOutputs saved to: {results['output_dir']}")

if __name__ == '__main__':
    main()

