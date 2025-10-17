#!/usr/bin/env python3
"""
Semantic Similarity Visualization Dashboard

Creates visualizations for semantic similarity analysis:
- Heatmaps by strand
- Network graphs of high-similarity concepts
- Hierarchical clustering dendrograms
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import networkx as nx

class SimilarityVisualizer:
    """Creates visualizations for semantic similarity analysis."""
    
    def __init__(self, validation_outputs_dir: str = 'validation_outputs'):
        """
        Initialize visualizer.
        
        Args:
            validation_outputs_dir: Directory containing validation outputs
        """
        self.output_dir = Path(validation_outputs_dir)
        
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")
        
        print(f"Loading validation outputs from: {self.output_dir}")
        
        # Load similarity matrix
        matrix_path = self.output_dir / 'similarity_matrix.csv'
        if not matrix_path.exists():
            raise FileNotFoundError(f"Similarity matrix not found: {matrix_path}")
        
        self.similarity_df = pd.read_csv(matrix_path, index_col=0)
        print(f"  Loaded similarity matrix: {self.similarity_df.shape}")
        
        # Load duplicates
        duplicates_path = self.output_dir / 'potential_duplicates.csv'
        if duplicates_path.exists():
            self.duplicates_df = pd.read_csv(duplicates_path)
            print(f"  Loaded {len(self.duplicates_df)} potential duplicates")
        else:
            self.duplicates_df = None
        
        # Create visualizations directory
        self.viz_dir = self.output_dir / 'visualizations'
        self.viz_dir.mkdir(exist_ok=True)
        print(f"  Visualizations will be saved to: {self.viz_dir}")
        
        # Parse concept info from index
        self.concepts_info = self._parse_concept_info()
        
    def _parse_concept_info(self):
        """Parse concept information from matrix index."""
        info = []
        for label in self.similarity_df.index:
            # Format: "id:name"
            parts = label.split(':', 1)
            if len(parts) == 2:
                concept_id = int(parts[0])
                name = parts[1]
                info.append({'id': concept_id, 'name': name, 'label': label})
        return info
    
    def create_strand_heatmaps(self, strand_name: str = None, top_n: int = 50):
        """
        Create heatmap visualizations by strand.
        
        Args:
            strand_name: Specific strand to visualize (None for all)
            top_n: Number of concepts to show in each heatmap
        """
        print(f"\nCreating strand heatmaps...")
        
        # If duplicates available, use them to identify strands
        if self.duplicates_df is not None:
            strands = set()
            for path in self.duplicates_df['concept1_path'].unique():
                strand = path.split(' > ')[0] if ' > ' in path else 'Other'
                strands.add(strand)
            
            if strand_name:
                strands = {strand_name}
            
            for strand in sorted(strands):
                self._create_single_strand_heatmap(strand, top_n)
        else:
            # Create overall heatmap
            self._create_overall_heatmap(top_n)
    
    def _create_single_strand_heatmap(self, strand_name: str, top_n: int):
        """Create heatmap for a single strand."""
        # Filter concepts from this strand
        strand_concepts = []
        for info in self.concepts_info:
            # This is approximate - we'd need the original concept data for exact filtering
            # For now, just create the visualization
            strand_concepts.append(info)
        
        # Use top N for visualization
        if len(strand_concepts) > top_n:
            strand_concepts = strand_concepts[:top_n]
        
        if len(strand_concepts) < 2:
            print(f"  Skipping {strand_name} - insufficient concepts")
            return
        
        # Extract submatrix
        labels = [c['label'] for c in strand_concepts]
        submatrix = self.similarity_df.loc[labels, labels].values
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            submatrix,
            xticklabels=[c['name'][:30] for c in strand_concepts],
            yticklabels=[c['name'][:30] for c in strand_concepts],
            cmap='RdYlGn_r',
            vmin=0, vmax=1,
            cbar_kws={'label': 'Cosine Similarity'},
            square=True
        )
        plt.title(f'Semantic Similarity Heatmap: {strand_name} (top {len(strand_concepts)} concepts)')
        plt.xticks(rotation=90, ha='right', fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        
        filename = f'heatmap_{strand_name.replace(" ", "_").lower()}.png'
        save_path = self.viz_dir / filename
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {save_path}")
    
    def _create_overall_heatmap(self, top_n: int):
        """Create overall heatmap with top N concepts."""
        print(f"  Creating overall heatmap (top {top_n} concepts)...")
        
        # Select top N concepts
        concepts = self.concepts_info[:top_n]
        labels = [c['label'] for c in concepts]
        
        submatrix = self.similarity_df.loc[labels, labels].values
        
        plt.figure(figsize=(14, 12))
        sns.heatmap(
            submatrix,
            xticklabels=[c['name'][:25] for c in concepts],
            yticklabels=[c['name'][:25] for c in concepts],
            cmap='RdYlGn_r',
            vmin=0, vmax=1,
            cbar_kws={'label': 'Cosine Similarity'},
            square=True
        )
        plt.title(f'Semantic Similarity Heatmap (top {top_n} concepts)')
        plt.xticks(rotation=90, ha='right', fontsize=7)
        plt.yticks(rotation=0, fontsize=7)
        plt.tight_layout()
        
        save_path = self.viz_dir / 'heatmap_overall.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {save_path}")
    
    def create_network_graph(self, similarity_threshold: float = 0.90, max_nodes: int = 100):
        """
        Create network graph of high-similarity concepts.
        
        Args:
            similarity_threshold: Minimum similarity to draw edge
            max_nodes: Maximum number of nodes to include
        """
        print(f"\nCreating network graph (threshold: {similarity_threshold})...")
        
        if self.duplicates_df is None:
            print("  No duplicates data available")
            return
        
        # Filter high-similarity pairs
        high_sim = self.duplicates_df[self.duplicates_df['similarity'] >= similarity_threshold].copy()
        
        if len(high_sim) == 0:
            print(f"  No pairs above threshold {similarity_threshold}")
            return
        
        # Create graph
        G = nx.Graph()
        
        # Add edges
        for _, row in high_sim.iterrows():
            G.add_edge(
                row['concept1_name'][:40],
                row['concept2_name'][:40],
                weight=row['similarity']
            )
        
        # Limit nodes if too many
        if G.number_of_nodes() > max_nodes:
            # Keep only top connected nodes
            degree_dict = dict(G.degree())
            top_nodes = sorted(degree_dict, key=degree_dict.get, reverse=True)[:max_nodes]
            G = G.subgraph(top_nodes).copy()
        
        print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # Node size by degree
        node_sizes = [300 + 100 * G.degree(node) for node in G.nodes()]
        
        # Draw
        nx.draw_networkx_nodes(
            G, pos,
            node_color='lightblue',
            node_size=node_sizes,
            alpha=0.7
        )
        
        nx.draw_networkx_edges(
            G, pos,
            alpha=0.3,
            width=1.5
        )
        
        nx.draw_networkx_labels(
            G, pos,
            font_size=7,
            font_weight='bold'
        )
        
        plt.title(f'Semantic Similarity Network (≥{similarity_threshold:.2f})', fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        
        save_path = self.viz_dir / f'network_graph_{int(similarity_threshold*100)}.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {save_path}")
        
        # Print summary statistics
        print(f"\n  Network Statistics:")
        print(f"    Nodes: {G.number_of_nodes()}")
        print(f"    Edges: {G.number_of_edges()}")
        print(f"    Connected components: {nx.number_connected_components(G)}")
        
        if G.number_of_nodes() > 0:
            avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
            print(f"    Average degree: {avg_degree:.2f}")
    
    def create_dendrogram(self, max_concepts: int = 100):
        """
        Create hierarchical clustering dendrogram.
        
        Args:
            max_concepts: Maximum number of concepts to include
        """
        print(f"\nCreating hierarchical clustering dendrogram...")
        
        # Select subset of concepts
        n_concepts = min(max_concepts, len(self.concepts_info))
        concepts = self.concepts_info[:n_concepts]
        labels = [c['label'] for c in concepts]
        
        # Extract distance matrix
        sim_matrix = self.similarity_df.loc[labels, labels].values
        
        # Convert similarity to distance
        distance_matrix = 1 - sim_matrix
        
        # Ensure valid distance matrix
        np.fill_diagonal(distance_matrix, 0)
        distance_matrix = np.maximum(distance_matrix, 0)
        
        # Convert to condensed form
        condensed_dist = squareform(distance_matrix, checks=False)
        
        # Perform hierarchical clustering
        linkage_matrix = linkage(condensed_dist, method='average')
        
        # Create dendrogram
        plt.figure(figsize=(14, 10))
        
        dendrogram(
            linkage_matrix,
            labels=[c['name'][:30] for c in concepts],
            orientation='right',
            leaf_font_size=7,
            color_threshold=0.3
        )
        
        plt.title(f'Hierarchical Clustering Dendrogram (top {n_concepts} concepts)', fontsize=14)
        plt.xlabel('Distance (1 - Similarity)', fontsize=12)
        plt.tight_layout()
        
        save_path = self.viz_dir / 'dendrogram.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {save_path}")
    
    def create_similarity_distribution(self):
        """Create histogram of similarity scores."""
        print(f"\nCreating similarity distribution plot...")
        
        # Get upper triangle of similarity matrix (excluding diagonal)
        n = self.similarity_df.shape[0]
        similarities = []
        for i in range(n):
            for j in range(i+1, n):
                similarities.append(self.similarity_df.iloc[i, j])
        
        similarities = np.array(similarities)
        
        plt.figure(figsize=(12, 6))
        
        plt.hist(similarities, bins=100, color='skyblue', edgecolor='black', alpha=0.7)
        plt.axvline(0.85, color='orange', linestyle='--', linewidth=2, label='Medium threshold (0.85)')
        plt.axvline(0.90, color='red', linestyle='--', linewidth=2, label='High threshold (0.90)')
        
        plt.xlabel('Cosine Similarity', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Semantic Similarity Scores', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        save_path = self.viz_dir / 'similarity_distribution.png'
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {save_path}")
        
        # Print statistics
        print(f"\n  Similarity Statistics:")
        print(f"    Mean: {np.mean(similarities):.3f}")
        print(f"    Median: {np.median(similarities):.3f}")
        print(f"    Std Dev: {np.std(similarities):.3f}")
        print(f"    Min: {np.min(similarities):.3f}")
        print(f"    Max: {np.max(similarities):.3f}")
        print(f"    % above 0.85: {100 * np.sum(similarities >= 0.85) / len(similarities):.2f}%")
        print(f"    % above 0.90: {100 * np.sum(similarities >= 0.90) / len(similarities):.2f}%")
    
    def generate_all_visualizations(self):
        """Generate all visualizations."""
        print("="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70)
        
        # Overall heatmap
        self._create_overall_heatmap(top_n=50)
        
        # Network graph
        self.create_network_graph(similarity_threshold=0.90, max_nodes=80)
        
        # Dendrogram
        self.create_dendrogram(max_concepts=80)
        
        # Distribution
        self.create_similarity_distribution()
        
        print(f"\n{'='*70}")
        print("VISUALIZATIONS COMPLETE")
        print(f"{'='*70}")
        print(f"All visualizations saved to: {self.viz_dir}")

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create visualizations for semantic similarity analysis"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='validation_outputs',
        help='Input directory with validation outputs (default: validation_outputs)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("SEMANTIC SIMILARITY VISUALIZER")
    print("="*70)
    print()
    
    # Create visualizer
    viz = SimilarityVisualizer(args.input)
    
    # Generate all visualizations
    viz.generate_all_visualizations()
    
    print(f"\n✓ Complete! View visualizations in: {viz.viz_dir}")

if __name__ == '__main__':
    main()

