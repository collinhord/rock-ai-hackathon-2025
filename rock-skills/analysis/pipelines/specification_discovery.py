#!/usr/bin/env python3
"""
Specification Discovery Module

Automatically discover specifications from skill variants by analyzing
metadata variance within base skill clusters.

Usage:
    from specification_discovery import SpecificationDiscoverer
    
    discoverer = SpecificationDiscoverer()
    specs = discoverer.discover_specifications(base_skill_clusters, metadata_df)
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Optional
from collections import Counter


class SpecificationDiscoverer:
    """Automatically discover specifications from skill variants."""
    
    def __init__(self):
        """Initialize the specification discoverer."""
        
        # Define known specification categories
        self.primary_specs = ['text_type', 'skill_domain', 'complexity_band']
        self.secondary_specs = ['cognitive_demand', 'support_level', 'text_mode', 'scope']
        self.tertiary_specs = ['text_genre', 'quantity', 'perspective_type']
        
        # Numeric range pattern for detection
        self.numeric_pattern = r'\b(?:within|up to|less than|greater than|between)\s+(\d+(?:,\d+)?)\b'
    
    def discover_specifications(self, base_skill_clusters: List[Dict], 
                                metadata_df: pd.DataFrame) -> List[Dict]:
        """
        Main discovery pipeline.
        
        Args:
            base_skill_clusters: List of base skill cluster definitions
            metadata_df: DataFrame with 23 enhanced metadata fields
            
        Returns:
            List of discovered specification definitions ranked by importance
        """
        print("\n=== SPECIFICATION DISCOVERY ===\n")
        
        discovered_specs = []
        
        for cluster in base_skill_clusters:
            if 'member_skill_ids' not in cluster:
                continue
            
            # Get member skills with metadata
            members = metadata_df[metadata_df['SKILL_ID'].isin(cluster['member_skill_ids'])]
            
            if len(members) < 2:
                continue  # Need at least 2 skills to discover specifications
            
            print(f"Analyzing cluster '{cluster.get('base_skill_name', 'Unknown')}' ({len(members)} skills)...")
            
            # Analyze variance across all metadata fields
            for field in metadata_df.columns:
                if field in ['SKILL_ID', 'SKILL_NAME']:
                    continue
                
                spec = self.analyze_field_as_specification(field, members, cluster)
                
                if spec and spec['discriminative_power'] > 0.3:
                    discovered_specs.append(spec)
            
            # Check for numeric range specifications
            numeric_spec = self.detect_numeric_range_specification(members)
            if numeric_spec:
                discovered_specs.append(numeric_spec)
        
        # Rank and deduplicate
        print(f"\n✓ Discovered {len(discovered_specs)} specification candidates")
        ranked_specs = self.rank_specifications(discovered_specs)
        
        # Deduplicate by spec_type (keep highest discriminative power)
        unique_specs = {}
        for spec in ranked_specs:
            spec_type = spec['spec_type']
            if spec_type not in unique_specs or spec['discriminative_power'] > unique_specs[spec_type]['discriminative_power']:
                unique_specs[spec_type] = spec
        
        final_specs = list(unique_specs.values())
        
        print(f"✓ After deduplication: {len(final_specs)} unique specification types")
        
        return final_specs
    
    def analyze_field_as_specification(self, field: str, members: pd.DataFrame, cluster: Dict) -> Optional[Dict]:
        """
        Analyze if a metadata field is a useful specification.
        
        Args:
            field: Metadata field name
            members: DataFrame of member skills
            cluster: Parent cluster definition
            
        Returns:
            Specification definition or None if not useful
        """
        # Calculate variance
        unique_values = members[field].nunique()
        total_values = len(members)
        
        # Skip if no variance (all same) or too much variance (unique per skill)
        if unique_values == 1 or unique_values == total_values:
            return None
        
        # Calculate discriminative power using entropy
        value_counts = members[field].value_counts()
        entropy = -sum((count/total_values) * np.log2(count/total_values) 
                       for count in value_counts if count > 0)
        max_entropy = np.log2(unique_values) if unique_values > 1 else 1
        discriminative_power = entropy / max_entropy if max_entropy > 0 else 0
        
        # Generate allowed values from data
        allowed_values = value_counts.index.tolist()
        
        # Determine specification level (primary, secondary, tertiary)
        level = self.determine_specification_level(field, discriminative_power)
        
        return {
            'spec_type': field,
            'unique_values': int(unique_values),
            'discriminative_power': float(discriminative_power),
            'allowed_values': allowed_values,
            'value_distribution': value_counts.to_dict(),
            'proposed_level': level,
            'discovery_method': 'automatic',
            'usage_count': int(total_values),
            'cluster_id': cluster.get('base_skill_id', cluster.get('cluster_id', 'unknown')),
            'cluster_name': cluster.get('base_skill_name', 'Unknown')
        }
    
    def determine_specification_level(self, field: str, discriminative_power: float) -> int:
        """
        Determine hierarchy level for specification.
        
        Args:
            field: Specification field name
            discriminative_power: Calculated discriminative power (0-1)
            
        Returns:
            Level: 1 (primary), 2 (secondary), or 3 (tertiary)
        """
        # Check predefined categories
        if field in self.primary_specs or discriminative_power > 0.7:
            return 1
        elif field in self.secondary_specs or discriminative_power > 0.5:
            return 2
        else:
            return 3
    
    def detect_numeric_range_specification(self, members: pd.DataFrame) -> Optional[Dict]:
        """
        Detect if skills differ by numeric ranges (e.g., "within 10" vs "within 20").
        
        Args:
            members: DataFrame of member skills
            
        Returns:
            Specification definition or None if not found
        """
        member_names = members['SKILL_NAME'].tolist()
        
        # Extract numeric patterns
        extracted_ranges = []
        matching_skills = 0
        
        for name in member_names:
            matches = re.findall(self.numeric_pattern, str(name), re.IGNORECASE)
            if matches:
                extracted_ranges.extend([int(m.replace(',', '')) for m in matches])
                matching_skills += 1
        
        # If at least 50% of skills have numeric ranges, it's a specification
        if matching_skills >= len(member_names) * 0.5 and len(set(extracted_ranges)) > 1:
            all_ranges = sorted(set(extracted_ranges))
            
            return {
                'spec_type': 'numeric_range',
                'unique_values': len(all_ranges),
                'discriminative_power': 0.8,  # High since it clearly differentiates
                'allowed_values': all_ranges,
                'value_distribution': Counter(extracted_ranges),
                'proposed_level': 2,  # Secondary
                'discovery_method': 'pattern_detection',
                'usage_count': matching_skills,
                'pattern': self.numeric_pattern,
                'example_values': [f"within_{r}" for r in all_ranges[:5]]  # Show up to 5 examples
            }
        
        return None
    
    def rank_specifications(self, specs: List[Dict]) -> List[Dict]:
        """
        Rank specifications by importance.
        
        Args:
            specs: List of specification definitions
            
        Returns:
            Specifications sorted by importance (highest first)
        """
        def spec_score(spec):
            """Calculate composite importance score."""
            return (
                spec['discriminative_power'] * 0.5 +
                min(1.0, spec['usage_count'] / 100) * 0.3 +
                (4 - spec['proposed_level']) / 3 * 0.2  # Favor primary specs
            )
        
        ranked = sorted(specs, key=spec_score, reverse=True)
        
        # Add rank to each spec
        for i, spec in enumerate(ranked):
            spec['rank'] = i + 1
            spec['importance_score'] = spec_score(spec)
        
        return ranked
    
    def generate_specification_report(self, discovered_specs: List[Dict]) -> Dict:
        """
        Generate a summary report of discovered specifications.
        
        Args:
            discovered_specs: List of discovered specifications
            
        Returns:
            Report dictionary with statistics and recommendations
        """
        report = {
            'total_specifications': len(discovered_specs),
            'by_level': {
                'primary': len([s for s in discovered_specs if s['proposed_level'] == 1]),
                'secondary': len([s for s in discovered_specs if s['proposed_level'] == 2]),
                'tertiary': len([s for s in discovered_specs if s['proposed_level'] == 3])
            },
            'top_10_by_discriminative_power': [
                {
                    'spec_type': s['spec_type'],
                    'discriminative_power': s['discriminative_power'],
                    'level': s['proposed_level'],
                    'unique_values': s['unique_values']
                }
                for s in sorted(discovered_specs, key=lambda x: x['discriminative_power'], reverse=True)[:10]
            ],
            'new_specifications': [
                {
                    'spec_type': s['spec_type'],
                    'discovery_method': s['discovery_method'],
                    'usage_count': s['usage_count']
                }
                for s in discovered_specs 
                if s['spec_type'] not in (self.primary_specs + self.secondary_specs + self.tertiary_specs)
            ]
        }
        
        return report
    
    def handle_multi_valued_specification(self, skill_name: str, spec_type: str) -> List[str]:
        """
        Handle specifications that can have multiple values.
        
        Args:
            skill_name: ROCK skill name
            spec_type: Specification type
            
        Returns:
            List of specification values
        """
        # Example: A skill might apply to both fictional AND informational text
        
        if spec_type == 'text_type':
            # Check if skill name is generic (applies to any text type)
            generic_indicators = ['any text', 'various texts', 'text of any type', 'all texts']
            if any(ind in skill_name.lower() for ind in generic_indicators):
                return ['fictional', 'informational', 'mixed']
        
        # Default: Single value (will be determined later)
        return []
    
    def determine_conditional_specifications(self, spec_type: str) -> Dict:
        """
        Define conditional specifications (apply only under certain conditions).
        
        Args:
            spec_type: Specification type
            
        Returns:
            Condition definition dictionary
        """
        # Example: text_genre only matters when text_type is not 'not_applicable'
        
        conditions = {
            'text_genre': {
                'condition_field': 'text_type',
                'condition_values': ['fictional', 'informational'],
                'else_value': 'not_applicable'
            },
            'perspective_type': {
                'condition_field': 'skill_domain',
                'condition_values': ['reading', 'comprehension'],
                'else_value': 'not_applicable'
            },
            'numeric_range': {
                'condition_field': 'skill_domain',
                'condition_values': ['mathematics', 'computation'],
                'else_value': None
            }
        }
        
        return conditions.get(spec_type, {})


def main():
    """Example usage of SpecificationDiscoverer."""
    import sys
    from pathlib import Path
    
    # Example: Load data and discover specifications
    print("Specification Discovery Module")
    print("=" * 50)
    print("\nThis module provides automatic specification discovery from skill metadata.")
    print("\nUsage:")
    print("  from specification_discovery import SpecificationDiscoverer")
    print("  discoverer = SpecificationDiscoverer()")
    print("  specs = discoverer.discover_specifications(clusters, metadata_df)")
    print("\nFor integration with pipelines, import the SpecificationDiscoverer class.")


if __name__ == '__main__':
    main()

