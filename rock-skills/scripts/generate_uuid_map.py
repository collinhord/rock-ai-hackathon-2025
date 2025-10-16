"""
UUID Mapping Generator

Generates deterministic UUIDs for taxonomy entries based on their full path.
Creates a separate JSON mapping file that maintains backward compatibility
with existing CSV structure.

The UUIDs are deterministic: same path = same UUID across regenerations.

Usage:
    python generate_uuid_map.py [--input taxonomy.csv] [--output taxonomy_uuid_map.json]
"""

import pandas as pd
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from uuid import UUID, uuid5, NAMESPACE_DNS


class UUIDMapGenerator:
    """Generates UUID mapping for taxonomy entries."""
    
    # Namespace UUID for this taxonomy (generated once)
    TAXONOMY_NAMESPACE = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    
    def __init__(self, csv_path: Path):
        """Initialize with path to taxonomy CSV."""
        self.csv_path = Path(csv_path)
        self.df = None
        self.uuid_map = {}
        self.reverse_map = {}
        
    def load(self):
        """Load the taxonomy CSV."""
        print(f"Loading taxonomy from: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} rows")
        
    def build_taxonomy_path(self, row: pd.Series) -> str:
        """
        Build full taxonomy path from row.
        
        Format: Strand > Pillar > Domain > Skill Area > Skill Set > Skill Subset
        """
        levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        path_parts = []
        
        for level in levels:
            value = row.get(level, '')
            if pd.notna(value) and str(value).strip():
                path_parts.append(str(value).strip())
        
        return ' > '.join(path_parts)
    
    def generate_uuid(self, taxonomy_path: str) -> str:
        """
        Generate deterministic UUID from taxonomy path.
        
        Uses UUID5 (SHA-1 hash) with custom namespace to ensure:
        - Same path always generates same UUID
        - Different paths generate different UUIDs
        - UUIDs are valid RFC 4122 compliant
        """
        return str(uuid5(self.TAXONOMY_NAMESPACE, taxonomy_path))
    
    def compute_path_hash(self, taxonomy_path: str) -> str:
        """Compute SHA-256 hash of taxonomy path for verification."""
        return hashlib.sha256(taxonomy_path.encode('utf-8')).hexdigest()
    
    def extract_levels(self, row: pd.Series) -> Dict[str, str]:
        """Extract taxonomy levels as dictionary."""
        levels = {}
        level_names = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        
        for level in level_names:
            value = row.get(level, '')
            if pd.notna(value) and str(value).strip():
                levels[level.lower().replace(' ', '_')] = str(value).strip()
            else:
                levels[level.lower().replace(' ', '_')] = None
                
        return levels
    
    def generate_mapping(self):
        """Generate UUID mapping for all taxonomy entries and all intermediate levels."""
        print("\nGenerating UUID mappings...")
        
        entries = []
        seen_paths = set()
        
        for idx, row in self.df.iterrows():
            # Extract all levels from this row
            level_names = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
            path_parts = []
            
            for level in level_names:
                value = row.get(level, '')
                if pd.notna(value) and str(value).strip():
                    path_parts.append(str(value).strip())
                    
                    # Create entry for this partial path (e.g., just Strand, then Strand > Pillar, etc.)
                    partial_path = ' > '.join(path_parts)
                    
                    # Skip if we've already seen this path
                    if partial_path in seen_paths:
                        continue
                    seen_paths.add(partial_path)
                    
                    # Generate UUID for this path
                    taxonomy_uuid = self.generate_uuid(partial_path)
                    
                    # Compute path hash
                    path_hash = self.compute_path_hash(partial_path)
                    
                    # Build partial levels dict
                    partial_levels = {}
                    for i, level_name in enumerate(level_names):
                        if i < len(path_parts):
                            partial_levels[level_name.lower().replace(' ', '_')] = path_parts[i]
                        else:
                            partial_levels[level_name.lower().replace(' ', '_')] = None
                    
                    # Get annotation only for full paths
                    annotation = ''
                    if len(path_parts) == len([v for v in [row.get(l) for l in level_names] if pd.notna(v) and str(v).strip()]):
                        annotation = row.get('Skill Subset Annotation', '')
                    
                    # Build entry
                    entry = {
                        'uuid': taxonomy_uuid,
                        'taxonomy_path': partial_path,
                        'path_hash': path_hash,
                        'levels': partial_levels,
                        'annotation': annotation
                    }
                    
                    entries.append(entry)
                    
                    # Add to forward and reverse maps
                    self.uuid_map[partial_path] = taxonomy_uuid
                    self.reverse_map[taxonomy_uuid] = partial_path
        
        print(f"Generated {len(entries)} unique UUID mappings (including all hierarchy levels)")
        
        return entries
    
    def save_mapping(self, output_path: Path, entries: List[Dict]):
        """Save UUID mapping to JSON file."""
        print(f"\nSaving UUID mapping to: {output_path}")
        
        # Build complete mapping structure
        mapping_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_file': str(self.csv_path),
                'total_entries': len(entries),
                'namespace_uuid': str(self.TAXONOMY_NAMESPACE),
                'version': '1.0'
            },
            'entries': entries,
            'forward_map': self.uuid_map,  # path -> uuid
            'reverse_map': self.reverse_map  # uuid -> path
        }
        
        # Save with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(entries)} entries")
        
    def generate_stats(self, entries: List[Dict]) -> Dict:
        """Generate statistics about the mapping."""
        stats = {
            'total_entries': len(entries),
            'by_level': {
                'strand': len(set(e['levels']['strand'] for e in entries if e['levels']['strand'])),
                'pillar': len(set(e['levels']['pillar'] for e in entries if e['levels']['pillar'])),
                'domain': len(set(e['levels']['domain'] for e in entries if e['levels']['domain'])),
                'skill_area': len(set(e['levels']['skill_area'] for e in entries if e['levels']['skill_area'])),
                'skill_set': len(set(e['levels']['skill_set'] for e in entries if e['levels']['skill_set'])),
                'skill_subset': len(set(e['levels']['skill_subset'] for e in entries if e['levels']['skill_subset'])),
            },
            'max_depth': max(
                sum(1 for v in e['levels'].values() if v is not None) 
                for e in entries
            ),
            'min_depth': min(
                sum(1 for v in e['levels'].values() if v is not None) 
                for e in entries
            )
        }
        
        return stats
    
    def print_stats(self, stats: Dict):
        """Print mapping statistics."""
        print("\nUUID MAPPING STATISTICS:")
        print("=" * 60)
        print(f"Total unique taxonomy paths: {stats['total_entries']}")
        print(f"Max taxonomy depth: {stats['max_depth']} levels")
        print(f"Min taxonomy depth: {stats['min_depth']} levels")
        print("\nUnique values by level:")
        for level, count in stats['by_level'].items():
            print(f"  {level.replace('_', ' ').title()}: {count}")
        print("=" * 60)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Generate UUID mapping for taxonomy')
    parser.add_argument(
        '--input',
        type=str,
        default='../POC_science_of_reading_literacy_skills_taxonomy.csv',
        help='Path to input taxonomy CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../taxonomy_uuid_map.json',
        help='Path to output UUID mapping JSON'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize generator
        generator = UUIDMapGenerator(args.input)
        
        # Load taxonomy
        generator.load()
        
        # Generate mappings
        entries = generator.generate_mapping()
        
        # Generate statistics
        stats = generator.generate_stats(entries)
        generator.print_stats(stats)
        
        # Save mapping
        output_path = Path(args.output)
        generator.save_mapping(output_path, entries)
        
        print("\nUUID mapping generation complete!")
        print(f"\nTo use this mapping in your code:")
        print(f"  import json")
        print(f"  with open('{output_path}', 'r') as f:")
        print(f"      uuid_map = json.load(f)")
        print(f"  # Access by path: uuid = uuid_map['forward_map'][taxonomy_path]")
        print(f"  # Access by UUID: path = uuid_map['reverse_map'][uuid]")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

