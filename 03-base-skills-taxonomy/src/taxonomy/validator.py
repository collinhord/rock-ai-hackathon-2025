"""
Taxonomy Validator Module

Performs comprehensive validation of taxonomy structure including:
- Hierarchy integrity
- Naming consistency
- Duplicate detection
- Coverage analysis
- Parent-child logical relationships
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
import json

from compatibility import TaxonomyAccess, TaxonomyNode


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'hierarchy', 'naming', 'duplicate', 'coverage', 'logic'
    message: str
    details: Dict = field(default_factory=dict)
    

@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: datetime
    total_nodes: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    issues: List[ValidationIssue]
    statistics: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_nodes': self.total_nodes,
            'total_issues': self.total_issues,
            'issues_by_severity': self.issues_by_severity,
            'issues_by_category': self.issues_by_category,
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'details': issue.details
                }
                for issue in self.issues
            ],
            'statistics': self.statistics
        }
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = []
        lines.append("# Taxonomy Validation Report")
        lines.append("")
        lines.append(f"**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Nodes:** {self.total_nodes}")
        lines.append(f"**Total Issues:** {self.total_issues}")
        lines.append("")
        
        # Summary by severity
        lines.append("## Issues by Severity")
        lines.append("")
        for severity, count in sorted(self.issues_by_severity.items()):
            lines.append(f"- **{severity.capitalize()}:** {count}")
        lines.append("")
        
        # Summary by category
        lines.append("## Issues by Category")
        lines.append("")
        for category, count in sorted(self.issues_by_category.items()):
            lines.append(f"- **{category.capitalize()}:** {count}")
        lines.append("")
        
        # Statistics
        lines.append("## Statistics")
        lines.append("")
        for key, value in self.statistics.items():
            if isinstance(value, dict):
                lines.append(f"### {key.replace('_', ' ').title()}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
                lines.append("")
            else:
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        lines.append("")
        
        # Detailed issues
        lines.append("## Detailed Issues")
        lines.append("")
        
        for severity in ['error', 'warning', 'info']:
            severity_issues = [i for i in self.issues if i.severity == severity]
            if severity_issues:
                lines.append(f"### {severity.capitalize()} ({len(severity_issues)})")
                lines.append("")
                
                for issue in severity_issues:
                    lines.append(f"#### {issue.category.capitalize()}: {issue.message}")
                    if issue.details:
                        lines.append("```")
                        lines.append(json.dumps(issue.details, indent=2))
                        lines.append("```")
                    lines.append("")
        
        return "\n".join(lines)


class TaxonomyValidator:
    """Validates taxonomy structure and content."""
    
    def __init__(self, taxonomy_access: TaxonomyAccess):
        """
        Initialize validator.
        
        Args:
            taxonomy_access: TaxonomyAccess instance
        """
        self.tax = taxonomy_access
        self.issues: List[ValidationIssue] = []
        
    def validate(self) -> ValidationReport:
        """
        Run complete validation.
        
        Returns:
            ValidationReport with all findings
        """
        print("Starting taxonomy validation...")
        self.issues = []
        
        # Run all validation checks
        print("  Validating hierarchy integrity...")
        self._validate_hierarchy()
        
        print("  Validating naming consistency...")
        self._validate_naming()
        
        print("  Detecting duplicates...")
        self._detect_duplicates()
        
        print("  Analyzing coverage...")
        self._analyze_coverage()
        
        print("  Validating logical relationships...")
        self._validate_logic()
        
        # Generate statistics
        stats = self._generate_statistics()
        
        # Count issues by severity and category
        issues_by_severity = {}
        issues_by_category = {}
        
        for issue in self.issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1
            issues_by_category[issue.category] = issues_by_category.get(issue.category, 0) + 1
        
        # Create report
        report = ValidationReport(
            timestamp=datetime.now(),
            total_nodes=stats['total_nodes'],
            total_issues=len(self.issues),
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            issues=self.issues,
            statistics=stats
        )
        
        print(f"\nValidation complete: {len(self.issues)} issues found")
        
        return report
    
    def _validate_hierarchy(self):
        """Validate hierarchy integrity."""
        # Check for orphaned nodes
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Find nodes with parent_uuid that doesn't exist
        cursor.execute('''
            SELECT n1.uuid, n1.name, n1.level, n1.parent_uuid
            FROM taxonomy_nodes n1
            WHERE n1.parent_uuid IS NOT NULL
            AND n1.parent_uuid NOT IN (SELECT uuid FROM taxonomy_nodes)
        ''')
        
        orphaned = cursor.fetchall()
        for row in orphaned:
            self.issues.append(ValidationIssue(
                severity='error',
                category='hierarchy',
                message=f"Orphaned node: {row['name']} has non-existent parent",
                details={
                    'uuid': row['uuid'],
                    'name': row['name'],
                    'level': row['level'],
                    'parent_uuid': row['parent_uuid']
                }
            ))
        
        # Check depth consistency
        levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        level_order = {level: i for i, level in enumerate(levels)}
        
        # Verify parent-child level relationships
        cursor.execute('''
            SELECT n1.uuid, n1.name, n1.level, n2.level as parent_level
            FROM taxonomy_nodes n1
            JOIN taxonomy_nodes n2 ON n1.parent_uuid = n2.uuid
        ''')
        
        for row in cursor.fetchall():
            child_level = row['level']
            parent_level = row['parent_level']
            
            if level_order[child_level] <= level_order[parent_level]:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='hierarchy',
                    message=f"Invalid parent-child level: {child_level} under {parent_level}",
                    details={
                        'uuid': row['uuid'],
                        'name': row['name'],
                        'child_level': child_level,
                        'parent_level': parent_level
                    }
                ))
    
    def _validate_naming(self):
        """Validate naming consistency."""
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Check for mixed capitalization patterns
        cursor.execute('SELECT uuid, name, level FROM taxonomy_nodes')
        
        nodes_by_level = {}
        for row in cursor.fetchall():
            level = row['level']
            if level not in nodes_by_level:
                nodes_by_level[level] = []
            nodes_by_level[level].append((row['uuid'], row['name']))
        
        # Check for case inconsistencies within each level
        for level, nodes in nodes_by_level.items():
            name_map = {}
            for uuid, name in nodes:
                lower_name = name.lower()
                if lower_name not in name_map:
                    name_map[lower_name] = []
                name_map[lower_name].append((uuid, name))
            
            # Find names with multiple capitalizations
            for lower_name, variants in name_map.items():
                if len(set(n for _, n in variants)) > 1:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='naming',
                        message=f"Inconsistent capitalization in {level}",
                        details={
                            'level': level,
                            'variants': [n for _, n in variants]
                        }
                    ))
        
        # Check for naming conventions
        cursor.execute('SELECT uuid, name, level FROM taxonomy_nodes')
        for row in cursor.fetchall():
            name = row['name']
            
            # Check for leading/trailing whitespace
            if name != name.strip():
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='naming',
                    message=f"Name has extra whitespace: '{name}'",
                    details={
                        'uuid': row['uuid'],
                        'name': name,
                        'level': row['level']
                    }
                ))
            
            # Check for double spaces
            if '  ' in name:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='naming',
                    message=f"Name has double spaces: '{name}'",
                    details={
                        'uuid': row['uuid'],
                        'name': name,
                        'level': row['level']
                    }
                ))
    
    def _detect_duplicates(self):
        """Detect exact and near-duplicates."""
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Exact duplicates (same name at same level)
        cursor.execute('''
            SELECT level, name, COUNT(*) as count
            FROM taxonomy_nodes
            GROUP BY level, name
            HAVING count > 1
        ''')
        
        for row in cursor.fetchall():
            self.issues.append(ValidationIssue(
                severity='error',
                category='duplicate',
                message=f"Exact duplicate found: '{row['name']}' at level {row['level']}",
                details={
                    'level': row['level'],
                    'name': row['name'],
                    'count': row['count']
                }
            ))
        
        # Near-duplicates (fuzzy matching within same level)
        cursor.execute('SELECT uuid, name, level FROM taxonomy_nodes ORDER BY level, name')
        
        nodes_by_level = {}
        for row in cursor.fetchall():
            level = row['level']
            if level not in nodes_by_level:
                nodes_by_level[level] = []
            nodes_by_level[level].append((row['uuid'], row['name']))
        
        for level, nodes in nodes_by_level.items():
            for i, (uuid1, name1) in enumerate(nodes):
                for uuid2, name2 in nodes[i+1:]:
                    if name1 == name2:
                        continue  # Already caught as exact duplicate
                    
                    similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                    
                    if 0.85 < similarity < 1.0 and len(name1) > 5:
                        self.issues.append(ValidationIssue(
                            severity='info',
                            category='duplicate',
                            message=f"Near-duplicate found in {level} ({similarity:.2f} similar)",
                            details={
                                'level': level,
                                'name1': name1,
                                'name2': name2,
                                'similarity': similarity
                            }
                        ))
    
    def _analyze_coverage(self):
        """Analyze taxonomy coverage."""
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Check for levels with very few nodes
        cursor.execute('''
            SELECT parent_uuid, COUNT(*) as child_count
            FROM taxonomy_nodes
            WHERE parent_uuid IS NOT NULL
            GROUP BY parent_uuid
            HAVING child_count < 2
        ''')
        
        for row in cursor.fetchall():
            parent = self.tax.get_node_by_uuid(row['parent_uuid'])
            if parent:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='coverage',
                    message=f"Node has only one child: {parent.name}",
                    details={
                        'uuid': parent.uuid,
                        'name': parent.name,
                        'level': parent.level,
                        'child_count': row['child_count']
                    }
                ))
        
        # Check for very deep paths
        cursor.execute('''
            SELECT n.uuid, n.name, n.level, MAX(h.depth) as max_depth
            FROM taxonomy_nodes n
            JOIN taxonomy_hierarchy h ON n.uuid = h.ancestor_uuid
            GROUP BY n.uuid
            HAVING max_depth > 5
        ''')
        
        for row in cursor.fetchall():
            self.issues.append(ValidationIssue(
                severity='info',
                category='coverage',
                message=f"Very deep hierarchy under: {row['name']}",
                details={
                    'uuid': row['uuid'],
                    'name': row['name'],
                    'level': row['level'],
                    'max_depth': row['max_depth']
                }
            ))
    
    def _validate_logic(self):
        """Validate logical parent-child relationships."""
        # This is a placeholder for more sophisticated semantic validation
        # that would use LLM or semantic similarity to ensure parent-child
        # relationships make logical sense
        
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Check for potentially misplaced nodes based on naming patterns
        cursor.execute('''
            SELECT n1.uuid, n1.name, n1.level, n2.name as parent_name
            FROM taxonomy_nodes n1
            JOIN taxonomy_nodes n2 ON n1.parent_uuid = n2.uuid
        ''')
        
        for row in cursor.fetchall():
            child_name = row['name'].lower()
            parent_name = row['parent_name'].lower()
            
            # Simple heuristic: if child name contains words not in parent context
            # This would be enhanced with LLM-based validation
            pass  # Placeholder for future logic validation
    
    def _generate_statistics(self) -> Dict:
        """Generate validation statistics."""
        conn = self.tax.get_db_connection()
        cursor = conn.cursor()
        
        # Total nodes
        cursor.execute('SELECT COUNT(*) FROM taxonomy_nodes')
        total_nodes = cursor.fetchone()[0]
        
        # Nodes by level
        cursor.execute('''
            SELECT level, COUNT(*) as count
            FROM taxonomy_nodes
            GROUP BY level
            ORDER BY count DESC
        ''')
        
        nodes_by_level = {row['level']: row['count'] for row in cursor.fetchall()}
        
        # Average children per node
        cursor.execute('''
            SELECT AVG(child_count) as avg_children
            FROM (
                SELECT parent_uuid, COUNT(*) as child_count
                FROM taxonomy_nodes
                WHERE parent_uuid IS NOT NULL
                GROUP BY parent_uuid
            )
        ''')
        
        avg_children = cursor.fetchone()['avg_children']
        
        # Max depth
        cursor.execute('''
            SELECT MAX(depth) as max_depth
            FROM taxonomy_hierarchy
        ''')
        
        max_depth = cursor.fetchone()['max_depth']
        
        return {
            'total_nodes': total_nodes,
            'nodes_by_level': nodes_by_level,
            'average_children_per_node': round(avg_children, 2) if avg_children else 0,
            'maximum_depth': max_depth
        }


# Example usage
if __name__ == '__main__':
    print("=== Taxonomy Validator Demo ===\n")
    
    with TaxonomyAccess() as tax:
        validator = TaxonomyValidator(tax)
        report = validator.validate()
        
        # Print summary
        print("\n" + "="*60)
        print(f"Total Issues: {report.total_issues}")
        print("\nBy Severity:")
        for severity, count in report.issues_by_severity.items():
            print(f"  {severity}: {count}")
        
        print("\nBy Category:")
        for category, count in report.issues_by_category.items():
            print(f"  {category}: {count}")
        
        # Save reports
        json_path = Path('../validation_report.json')
        with open(json_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nJSON report saved to: {json_path}")
        
        md_path = Path('../validation_report.md')
        with open(md_path, 'w') as f:
            f.write(report.to_markdown())
        print(f"Markdown report saved to: {md_path}")

