"""
Data Loader Module for ROCK Skills Bridge Explorer

Handles loading and indexing of ROCK schemas and taxonomy mappings.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import streamlit as st


class ROCKDataLoader:
    """Loads and indexes ROCK schema data and taxonomy mappings."""
    
    def __init__(self, schema_dir: Path, analysis_dir: Path):
        """
        Initialize data loader.
        
        Args:
            schema_dir: Path to rock_schemas directory
            analysis_dir: Path to analysis directory (with mappings)
        """
        self.schema_dir = Path(schema_dir)
        self.analysis_dir = Path(analysis_dir)
        self._cache = {}
    
    @st.cache_data
    def load_skills(_self) -> pd.DataFrame:
        """Load SKILLS.csv with caching."""
        if 'skills' not in _self._cache:
            skills_path = _self.schema_dir / 'SKILLS.csv'
            _self._cache['skills'] = pd.read_csv(skills_path)
        return _self._cache['skills']
    
    @st.cache_data
    def load_skill_taxonomy_mapping(_self) -> pd.DataFrame:
        """Load skill-to-taxonomy mapping."""
        if 'mapping' not in _self._cache:
            mapping_path = _self.analysis_dir / 'skill-taxonomy-mapping.csv'
            if mapping_path.exists():
                _self._cache['mapping'] = pd.read_csv(mapping_path)
            else:
                # Return empty DataFrame with expected columns
                _self._cache['mapping'] = pd.DataFrame(columns=[
                    'SKILL_ID', 'SKILL_NAME', 'SOR_STRAND', 'SOR_PILLAR',
                    'SOR_DOMAIN', 'SOR_SKILL_AREA', 'MASTER_CONCEPT_GROUP'
                ])
        return _self._cache['mapping']
    
    @st.cache_data
    def load_master_concepts(_self) -> pd.DataFrame:
        """Load master concepts groupings."""
        if 'concepts' not in _self._cache:
            concepts_path = _self.analysis_dir / 'master-concepts.csv'
            if concepts_path.exists():
                _self._cache['concepts'] = pd.read_csv(concepts_path)
            else:
                _self._cache['concepts'] = pd.DataFrame()
        return _self._cache['concepts']
    
    @st.cache_data
    def load_fragmentation_examples(_self) -> pd.DataFrame:
        """Load fragmentation examples."""
        if 'examples' not in _self._cache:
            examples_path = _self.analysis_dir / 'fragmentation-examples.csv'
            if examples_path.exists():
                _self._cache['examples'] = pd.read_csv(examples_path)
            else:
                _self._cache['examples'] = pd.DataFrame()
        return _self._cache['examples']
    
    @st.cache_data
    def load_sor_taxonomy(_self) -> pd.DataFrame:
        """Load Science of Reading taxonomy."""
        if 'taxonomy' not in _self._cache:
            taxonomy_path = _self.schema_dir.parent / 'POC_science_of_reading_literacy_skills_taxonomy.csv'
            if taxonomy_path.exists():
                _self._cache['taxonomy'] = pd.read_csv(taxonomy_path)
            else:
                _self._cache['taxonomy'] = pd.DataFrame()
        return _self._cache['taxonomy']
    
    @st.cache_data
    def load_standard_skills(_self, sample_size: int = 500000) -> pd.DataFrame:
        """Load STANDARD_SKILLS.csv (sampled for performance)."""
        if 'standard_skills' not in _self._cache:
            ss_path = _self.schema_dir / 'STANDARD_SKILLS.csv'
            try:
                # Load in chunks and sample
                chunks = []
                for i, chunk in enumerate(pd.read_csv(ss_path, chunksize=100000)):
                    chunks.append(chunk)
                    if len(pd.concat(chunks)) >= sample_size:
                        break
                _self._cache['standard_skills'] = pd.concat(chunks, ignore_index=True)
            except Exception as e:
                st.warning(f"Could not load STANDARD_SKILLS: {e}")
                _self._cache['standard_skills'] = pd.DataFrame()
        return _self._cache['standard_skills']
    
    def get_skills_by_master_concept(self, concept_id: str) -> pd.DataFrame:
        """Get all ROCK skills mapped to a master concept."""
        mapping = self.load_skill_taxonomy_mapping()
        skills = self.load_skills()
        
        # Filter mapping by concept
        concept_mappings = mapping[mapping['MASTER_CONCEPT_GROUP'] == concept_id]
        
        # Join with skills to get full details
        result = concept_mappings.merge(
            skills[['SKILL_ID', 'SKILL_AREA_NAME', 'GRADE_LEVEL_NAME', 'CONTENT_AREA_NAME']],
            on='SKILL_ID',
            how='left'
        )
        
        return result
    
    def get_skill_details(self, skill_id: str) -> Optional[Dict]:
        """Get full details for a specific skill."""
        skills = self.load_skills()
        skill_row = skills[skills['SKILL_ID'] == skill_id]
        
        if skill_row.empty:
            return None
        
        return skill_row.iloc[0].to_dict()
    
    def get_mapped_skills_count(self) -> int:
        """Count how many skills have taxonomy mappings."""
        mapping = self.load_skill_taxonomy_mapping()
        return len(mapping)
    
    def get_master_concepts_summary(self) -> pd.DataFrame:
        """Get summary statistics for master concepts."""
        concepts = self.load_master_concepts()
        mapping = self.load_skill_taxonomy_mapping()
        
        if concepts.empty or mapping.empty:
            return pd.DataFrame()
        
        # Count actual mapped skills per concept
        mapped_counts = mapping.groupby('MASTER_CONCEPT_GROUP').size().reset_index(name='Mapped_Skills')
        
        # Merge with concepts
        summary = concepts.merge(
            mapped_counts,
            left_on='MASTER_CONCEPT_ID',
            right_on='MASTER_CONCEPT_GROUP',
            how='left'
        )
        
        summary['Mapped_Skills'] = summary['Mapped_Skills'].fillna(0).astype(int)
        
        return summary
    
    def search_skills(self, query: str, content_area: Optional[str] = None) -> pd.DataFrame:
        """Search skills by name/description."""
        skills = self.load_skills()
        
        # Filter by content area if specified
        if content_area:
            skills = skills[skills['CONTENT_AREA_NAME'] == content_area]
        
        # Search in skill name
        mask = skills['SKILL_NAME'].str.contains(query, case=False, na=False)
        
        return skills[mask]
    
    def get_sor_hierarchy(self) -> Dict[str, Dict]:
        """Get Science of Reading taxonomy as hierarchical structure."""
        taxonomy = self.load_sor_taxonomy()
        
        if taxonomy.empty:
            return {}
        
        # Build hierarchy: Strand -> Pillar -> Domain -> Skill Area
        hierarchy = {}
        
        for _, row in taxonomy.iterrows():
            strand = row.get('Strand', 'Unknown')
            pillar = row.get('Pillar', 'Unknown')
            domain = row.get('Domain', 'Unknown')
            skill_area = row.get('Skill Area', 'Unknown')
            
            if strand not in hierarchy:
                hierarchy[strand] = {}
            if pillar not in hierarchy[strand]:
                hierarchy[strand][pillar] = {}
            if domain not in hierarchy[strand][pillar]:
                hierarchy[strand][pillar][domain] = set()
            
            hierarchy[strand][pillar][domain].add(skill_area)
        
        # Convert sets to lists for JSON serialization
        for strand in hierarchy:
            for pillar in hierarchy[strand]:
                for domain in hierarchy[strand][pillar]:
                    hierarchy[strand][pillar][domain] = sorted(list(hierarchy[strand][pillar][domain]))
        
        return hierarchy

