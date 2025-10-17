"""
Data Loader Module for ROCK Skills Bridge Explorer

Handles loading and indexing of ROCK schemas and taxonomy mappings.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import streamlit as st
import json
import glob


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
        """Load SKILLS.csv with caching (optimized columns)."""
        if 'skills' not in _self._cache:
            skills_path = _self.schema_dir / 'SKILLS.csv'
            # Load only essential columns for performance
            essential_columns = [
                'SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME',
                'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME', 'GRADE_LEVEL_SHORT_NAME'
            ]
            _self._cache['skills'] = pd.read_csv(skills_path, usecols=essential_columns)
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
        """Load master concepts groupings (generated from State A variant groups)."""
        if 'concepts' not in _self._cache:
            concepts_path = _self.analysis_dir / 'master-concepts.csv'
            if concepts_path.exists():
                _self._cache['concepts'] = pd.read_csv(concepts_path)
            else:
                _self._cache['concepts'] = pd.DataFrame()
        return _self._cache['concepts']
    
    @st.cache_data
    def load_skill_master_concept_mapping(_self) -> pd.DataFrame:
        """Load skill-to-master-concept bridge table with enriched columns."""
        if 'skill_concept_mapping' not in _self._cache:
            mapping_path = _self.analysis_dir / 'skill_master_concept_mapping.csv'
            if mapping_path.exists():
                mapping_df = pd.read_csv(mapping_path)
                
                # Enrich with additional columns from SKILLS, MASTER_CONCEPTS, STANDARD_SKILLS, and STANDARD_SETS
                try:
                    # Load SKILLS table to get GRADE_LEVEL_NAME
                    skills = _self.load_skills()
                    if not skills.empty:
                        # Join with SKILLS to get GRADE_LEVEL_NAME and other fields
                        mapping_df = mapping_df.merge(
                            skills[['SKILL_ID', 'GRADE_LEVEL_NAME', 'SKILL_AREA_NAME', 'CONTENT_AREA_NAME']],
                            on='SKILL_ID',
                            how='left',
                            suffixes=('', '_skill')
                        )
                    
                    # Load MASTER_CONCEPTS to get SOR taxonomy columns
                    master_concepts = _self.load_master_concepts()
                    if not master_concepts.empty:
                        # Join with MASTER_CONCEPTS to get SOR_STRAND, SOR_PILLAR, SOR_DOMAIN
                        concept_cols = ['MASTER_CONCEPT_ID', 'SOR_STRAND', 'SOR_PILLAR', 'SOR_DOMAIN']
                        available_cols = [col for col in concept_cols if col in master_concepts.columns]
                        if 'MASTER_CONCEPT_ID' in available_cols:
                            mapping_df = mapping_df.merge(
                                master_concepts[available_cols],
                                on='MASTER_CONCEPT_ID',
                                how='left',
                                suffixes=('', '_concept')
                            )
                    
                    # Load STANDARD_SKILLS and STANDARD_SETS to get EDUCATION_AUTHORITY
                    standard_skills = _self.load_standard_skills()
                    standard_sets = _self.load_standard_sets()
                    
                    if not standard_skills.empty and not standard_sets.empty:
                        # Join to get STANDARD_SET_ID for each SKILL_ID
                        skill_to_set = standard_skills[['SKILL_ID', 'STANDARD_SET_ID']].drop_duplicates()
                        
                        # Join with STANDARD_SETS to get EDUCATION_AUTHORITY
                        skill_to_authority = skill_to_set.merge(
                            standard_sets[['STANDARD_SET_ID', 'EDUCATION_AUTHORITY']],
                            on='STANDARD_SET_ID',
                            how='left'
                        ).drop_duplicates(subset=['SKILL_ID'])
                        
                        # Join with mapping
                        mapping_df = mapping_df.merge(
                            skill_to_authority[['SKILL_ID', 'EDUCATION_AUTHORITY']],
                            on='SKILL_ID',
                            how='left'
                        )
                except Exception as e:
                    st.warning(f"Could not enrich mapping data: {e}")
                
                _self._cache['skill_concept_mapping'] = mapping_df
            else:
                _self._cache['skill_concept_mapping'] = pd.DataFrame()
        return _self._cache['skill_concept_mapping']
    
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
        """Load STANDARD_SKILLS.csv (sampled for performance, optimized columns)."""
        if 'standard_skills' not in _self._cache:
            ss_path = _self.schema_dir / 'STANDARD_SKILLS.csv'
            try:
                # Load only essential columns
                essential_columns = ['SKILL_ID', 'STANDARD_SET_ID', 'STANDARD_ID']
                # Load in chunks and sample
                chunks = []
                for i, chunk in enumerate(pd.read_csv(ss_path, chunksize=100000, usecols=essential_columns)):
                    chunks.append(chunk)
                    if len(pd.concat(chunks)) >= sample_size:
                        break
                _self._cache['standard_skills'] = pd.concat(chunks, ignore_index=True)
            except Exception as e:
                st.warning(f"Could not load STANDARD_SKILLS: {e}")
                _self._cache['standard_skills'] = pd.DataFrame()
        return _self._cache['standard_skills']
    
    @st.cache_data
    def load_llm_skill_mappings(_self) -> pd.DataFrame:
        """Load LLM-assisted skill-to-taxonomy mappings."""
        if 'llm_mappings' not in _self._cache:
            mapping_path = _self.analysis_dir / 'llm_skill_mappings.csv'
            if mapping_path.exists():
                _self._cache['llm_mappings'] = pd.read_csv(mapping_path)
            else:
                # Return empty DataFrame with expected columns
                _self._cache['llm_mappings'] = pd.DataFrame(columns=[
                    'SKILL_ID', 'SKILL_NAME', 'TAXONOMY_PATH', 'CONFIDENCE',
                    'SEMANTIC_SIMILARITY', 'NEEDS_REVIEW', 'strand', 'pillar',
                    'domain', 'skill_area', 'skill_subset'
                ])
        return _self._cache['llm_mappings']
    
    @st.cache_data
    def load_variant_classification(_self) -> pd.DataFrame:
        """Load State A/B variant classification (reliably cached)."""
        if 'variants' not in _self._cache:
            variant_path = _self.analysis_dir / 'outputs/variant-classification-report.csv'
            if variant_path.exists():
                _self._cache['variants'] = pd.read_csv(variant_path)
            else:
                _self._cache['variants'] = pd.DataFrame()
        return _self._cache['variants']
    
    @st.cache_data
    def load_base_skills(_self) -> pd.DataFrame:
        """Load base skills summary from JSON files with taxonomy mappings."""
        if 'base_skills' not in _self._cache:
            # Load from base_skills_summary.json
            base_skills_dir = _self.schema_dir.parent / 'taxonomy' / 'base_skills'
            summary_path = base_skills_dir / 'base_skills_summary.json'
            
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    base_skills_list = json.load(f)
                base_skills_df = pd.DataFrame(base_skills_list)
            else:
                # Try loading individual files
                base_skills_data = []
                if base_skills_dir.exists():
                    for json_file in sorted(base_skills_dir.glob('BS-*.json')):
                        with open(json_file, 'r') as f:
                            base_skills_data.append(json.load(f))
                
                if base_skills_data:
                    base_skills_df = pd.DataFrame(base_skills_data)
                else:
                    base_skills_df = pd.DataFrame()
            
            # Load taxonomy mappings if available
            if not base_skills_df.empty:
                taxonomy_mapping_path = base_skills_dir / 'base_skills_taxonomy_mapping.csv'
                if taxonomy_mapping_path.exists():
                    taxonomy_mappings = pd.read_csv(taxonomy_mapping_path)
                    # Merge taxonomy mappings into base skills
                    base_skills_df = base_skills_df.merge(
                        taxonomy_mappings[['base_skill_id', 'taxonomy_strand', 'taxonomy_pillar', 
                                          'taxonomy_domain', 'taxonomy_notes']],
                        on='base_skill_id',
                        how='left'
                    )
                    # Add taxonomy source indicator
                    base_skills_df['taxonomy_source'] = base_skills_df['taxonomy_strand'].apply(
                        lambda x: 'Manually Mapped' if pd.notna(x) else None
                    )
            
            _self._cache['base_skills'] = base_skills_df
        
        return _self._cache['base_skills']
    
    @st.cache_data
    def load_skill_specifications(_self) -> pd.DataFrame:
        """Load enhanced metadata as skill specifications."""
        if 'specifications' not in _self._cache:
            # Try to load the most recent enhanced metadata file
            metadata_dir = _self.analysis_dir / 'outputs' / 'filtered_enhanced_metadata'
            
            if metadata_dir.exists():
                # Find the most recent skill_metadata_enhanced file
                metadata_files = sorted(metadata_dir.glob('skill_metadata_enhanced_*.csv'))
                
                if metadata_files:
                    # Load the most recent file
                    latest_file = metadata_files[-1]
                    _self._cache['specifications'] = pd.read_csv(latest_file)
                else:
                    _self._cache['specifications'] = pd.DataFrame()
            else:
                _self._cache['specifications'] = pd.DataFrame()
        
        return _self._cache['specifications']
    
    @st.cache_data
    def load_taxonomy_hierarchy(_self) -> pd.DataFrame:
        """Load Science of Reading taxonomy for hierarchical browsing."""
        # This is the same as load_sor_taxonomy, kept for consistency
        return _self.load_sor_taxonomy()
    
    @st.cache_data
    def load_standard_sets(_self) -> pd.DataFrame:
        """Load STANDARD_SETS.csv (optimized columns)."""
        if 'standard_sets' not in _self._cache:
            ss_path = _self.schema_dir / 'STANDARD_SETS.csv'
            try:
                essential_columns = [
                    'STANDARD_SET_ID',
                    'STANDARD_SET_NAME',
                    'EDUCATION_AUTHORITY',
                    'CONTENT_AREA_NAME'
                ]
                _self._cache['standard_sets'] = pd.read_csv(ss_path, usecols=essential_columns)
            except Exception as e:
                st.warning(f"Could not load STANDARD_SETS: {e}")
                _self._cache['standard_sets'] = pd.DataFrame()
        return _self._cache['standard_sets']
    
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
    
    def get_taxonomy_node_skills(self, taxonomy_path: str) -> pd.DataFrame:
        """Get all skills mapped to a specific taxonomy node."""
        mappings = self.load_llm_skill_mappings()
        # Filter by exact or partial taxonomy path match
        mask = mappings['TAXONOMY_PATH'].str.contains(taxonomy_path, case=False, na=False)
        return mappings[mask]
    
    def get_skill_by_id(self, skill_id: str) -> Optional[pd.Series]:
        """Get skill by SKILL_ID with mapping info."""
        skills = self.load_skills()
        mappings = self.load_llm_skill_mappings()
        
        skill = skills[skills['SKILL_ID'] == skill_id]
        if skill.empty:
            return None
        
        skill_data = skill.iloc[0].copy()
        mapping = mappings[mappings['SKILL_ID'] == skill_id]
        
        if not mapping.empty:
            mapping_data = mapping.iloc[0]
            skill_data['TAXONOMY_PATH'] = mapping_data.get('TAXONOMY_PATH')
            skill_data['CONFIDENCE'] = mapping_data.get('CONFIDENCE')
            skill_data['SEMANTIC_SIMILARITY'] = mapping_data.get('SEMANTIC_SIMILARITY')
            skill_data['strand'] = mapping_data.get('strand')
            skill_data['pillar'] = mapping_data.get('pillar')
            skill_data['domain'] = mapping_data.get('domain')
        
        return skill_data
    
    def search_skills_advanced(self, 
                              query: str = None,
                              skill_id: str = None,
                              content_area: str = None,
                              grade_level: str = None,
                              skill_area: str = None) -> pd.DataFrame:
        """Advanced skill search with multiple filters."""
        skills = self.load_skills()
        
        if skill_id:
            skills = skills[skills['SKILL_ID'] == skill_id]
        
        if query:
            mask = skills['SKILL_NAME'].str.contains(query, case=False, na=False)
            skills = skills[mask]
        
        if content_area and content_area != "All":
            skills = skills[skills['CONTENT_AREA_NAME'] == content_area]
        
        if grade_level and grade_level != "All":
            skills = skills[skills['GRADE_LEVEL_NAME'] == grade_level]
        
        if skill_area and skill_area != "All":
            skills = skills[skills['SKILL_AREA_NAME'] == skill_area]
        
        # Join with mappings
        mappings = self.load_llm_skill_mappings()
        if not mappings.empty:
            skills = skills.merge(
                mappings[['SKILL_ID', 'TAXONOMY_PATH', 'CONFIDENCE', 'SEMANTIC_SIMILARITY']],
                on='SKILL_ID',
                how='left'
            )
        
        return skills
    
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
    
    # ============================================================================
    # MASTER CONCEPTS METHODS (for bridging layer)
    # ============================================================================
    
    def get_master_concept_by_id(self, concept_id: str) -> Optional[pd.Series]:
        """Retrieve full master concept details by ID."""
        concepts = self.load_master_concepts()
        if concepts.empty:
            return None
        
        concept = concepts[concepts['MASTER_CONCEPT_ID'] == concept_id]
        if concept.empty:
            return None
        
        return concept.iloc[0]
    
    def get_skills_by_master_concept_id(self, concept_id: str) -> pd.DataFrame:
        """Get all ROCK skills mapped to a master concept using bridge table."""
        skill_mapping = self.load_skill_master_concept_mapping()
        
        if skill_mapping.empty:
            return pd.DataFrame()
        
        # Filter mapping by concept ID (mapping is already enriched with skill details)
        concept_skills = skill_mapping[skill_mapping['MASTER_CONCEPT_ID'] == concept_id]
        
        return concept_skills
    
    def get_master_concept_for_skill(self, skill_id: str) -> Optional[Dict]:
        """Reverse lookup: find master concept for a given skill."""
        skill_mapping = self.load_skill_master_concept_mapping()
        
        if skill_mapping.empty:
            return None
        
        mapping = skill_mapping[skill_mapping['SKILL_ID'] == skill_id]
        if mapping.empty or pd.isna(mapping.iloc[0]['MASTER_CONCEPT_ID']):
            return None
        
        # Get full concept details
        concept_id = mapping.iloc[0]['MASTER_CONCEPT_ID']
        concept = self.get_master_concept_by_id(concept_id)
        
        if concept is None:
            return None
        
        return {
            'concept_id': concept['MASTER_CONCEPT_ID'],
            'concept_name': concept['MASTER_CONCEPT_NAME'],
            'strand': concept['SOR_STRAND'],
            'pillar': concept['SOR_PILLAR'],
            'domain': concept['SOR_DOMAIN'],
            'skill_count': concept['SKILL_COUNT'],
            'grade_range': concept['GRADE_RANGE']
        }
    
    def get_state_a_groups_summary(self) -> pd.DataFrame:
        """Aggregate State A variant groups with metrics."""
        variants = self.load_variant_classification()
        concepts = self.load_master_concepts()
        
        if variants.empty:
            return pd.DataFrame()
        
        # Filter to State A skills
        state_a = variants[variants['EQUIVALENCE_TYPE'] == 'state-variant']
        
        # Group by equivalence group
        group_stats = state_a.groupby('EQUIVALENCE_GROUP_ID').agg({
            'SKILL_ID': 'count',
            'SKILL_NAME': 'first',
            'AUTHORITY': 'nunique',
            'GRADE_LEVEL_SHORT_NAME': lambda x: ', '.join(sorted(set(str(g) for g in x if pd.notna(g))))
        }).reset_index()
        
        group_stats.columns = ['EQUIVALENCE_GROUP_ID', 'SKILL_COUNT', 'EXAMPLE_SKILL', 'AUTHORITY_COUNT', 'GRADES']
        
        # Join with master concepts if available
        if not concepts.empty:
            group_stats = group_stats.merge(
                concepts[['EQUIVALENCE_GROUP_ID', 'MASTER_CONCEPT_ID', 'MASTER_CONCEPT_NAME']],
                on='EQUIVALENCE_GROUP_ID',
                how='left'
            )
        
        return group_stats.sort_values('SKILL_COUNT', ascending=False)
    
    def get_equivalence_group_details(self, group_id: str) -> pd.DataFrame:
        """Get all skills in a specific equivalence group (variant group)."""
        variants = self.load_variant_classification()
        skills = self.load_skills()
        
        if variants.empty:
            return pd.DataFrame()
        
        # Filter to group
        group_skills = variants[variants['EQUIVALENCE_GROUP_ID'] == group_id]
        
        # Join with full skill details
        result = group_skills.merge(
            skills,
            on='SKILL_ID',
            how='left',
            suffixes=('_variant', '_skill')
        )
        
        return result
    
    # ============================================================================
    # CONTENT SCALING METHODS (for demo pages)
    # ============================================================================
    
    @st.cache_data
    def load_content_library(_self) -> pd.DataFrame:
        """Load mock content items for scaling demos."""
        if 'content_library' not in _self._cache:
            content_path = Path(_self.schema_dir).parent / 'poc' / 'mock_data' / 'content_library.csv'
            if content_path.exists():
                _self._cache['content_library'] = pd.read_csv(content_path)
            else:
                _self._cache['content_library'] = pd.DataFrame(columns=[
                    'CONTENT_ID', 'CONTENT_TITLE', 'CONTENT_TYPE', 'DESCRIPTION',
                    'GRANULARITY_LEVEL', 'MASTER_CONCEPT', 'TAGGED_SKILL_IDS',
                    'TARGET_GRADE', 'CREATED_DATE', 'DURATION_MINUTES', 'AUTHOR'
                ])
        return _self._cache['content_library']
    
    @st.cache_data
    def load_tagging_scenarios(_self) -> pd.DataFrame:
        """Load tagging scenarios showing skill variants."""
        if 'tagging_scenarios' not in _self._cache:
            scenarios_path = Path(_self.schema_dir).parent / 'poc' / 'mock_data' / 'tagging_scenarios.csv'
            if scenarios_path.exists():
                _self._cache['tagging_scenarios'] = pd.read_csv(scenarios_path)
            else:
                _self._cache['tagging_scenarios'] = pd.DataFrame(columns=[
                    'SCENARIO_ID', 'SCENARIO_NAME', 'CONTENT_ITEM', 'MASTER_CONCEPT',
                    'MATCHING_ROCK_SKILLS_COUNT', 'STATES_WITH_SKILLS', 'DESCRIPTION'
                ])
        return _self._cache['tagging_scenarios']
    
    def get_skills_by_concept(self, concept_name: str) -> pd.DataFrame:
        """
        Get all ROCK skills for a master concept across states.
        
        Uses existing llm_skill_mappings filtered by concept name.
        
        Args:
            concept_name: Name of master concept (e.g., "Phoneme Blending")
            
        Returns:
            DataFrame with skills matching the concept
        """
        mappings = self.load_llm_skill_mappings()
        skills = self.load_skills()
        
        if mappings.empty:
            return pd.DataFrame()
        
        # Search in taxonomy path for concept name
        mask = mappings['TAXONOMY_PATH'].str.contains(concept_name, case=False, na=False)
        concept_mappings = mappings[mask]
        
        # Join with skills for full details
        result = concept_mappings.merge(
            skills,
            on='SKILL_ID',
            how='left',
            suffixes=('_mapping', '_skill')
        )
        
        return result
    
    def calculate_state_coverage(self, content_id: str, with_bridge: bool = False) -> Dict:
        """
        Calculate which states can discover a content item.
        
        Args:
            content_id: Content item identifier
            with_bridge: If True, calculate coverage via master skill bridge
            
        Returns:
            Dict with coverage metrics and details
        """
        content = self.load_content_library()
        scenarios = self.load_tagging_scenarios()
        
        # Get content item
        content_item = content[content['CONTENT_ID'] == content_id]
        if content_item.empty:
            return {'error': 'Content not found'}
        
        content_item = content_item.iloc[0]
        
        # Get corresponding scenario
        scenario = scenarios[scenarios['CONTENT_ITEM'] == content_id]
        if scenario.empty:
            return {'error': 'Scenario not found'}
        
        scenario = scenario.iloc[0]
        
        if not with_bridge:
            # WITHOUT BRIDGE: Only one state can discover (the one it's tagged to)
            # Content is tagged to ONE state-specific skill
            states_covered = 1
            total_states_with_skills = len(scenario['STATES_WITH_SKILLS'].split(','))
            coverage_pct = (states_covered / total_states_with_skills) * 100
            
            return {
                'content_id': content_id,
                'content_title': content_item['CONTENT_TITLE'],
                'master_concept': content_item['MASTER_CONCEPT'],
                'tagged_skill_count': 1,
                'states_covered': states_covered,
                'total_states_available': total_states_with_skills,
                'coverage_percentage': coverage_pct,
                'states_list': scenario['STATES_WITH_SKILLS'].split(',')[:1],  # Only first state
                'missing_states': scenario['STATES_WITH_SKILLS'].split(',')[1:],
                'mode': 'without_bridge'
            }
        else:
            # WITH BRIDGE: All states with equivalent skills can discover
            # Content is tagged to MASTER SKILL → inherits all state mappings
            total_states_with_skills = len(scenario['STATES_WITH_SKILLS'].split(','))
            states_covered = total_states_with_skills
            coverage_pct = 100.0
            
            return {
                'content_id': content_id,
                'content_title': content_item['CONTENT_TITLE'],
                'master_concept': content_item['MASTER_CONCEPT'],
                'tagged_skill_count': 1,  # Still tag once, but to master skill
                'states_covered': states_covered,
                'total_states_available': total_states_with_skills,
                'coverage_percentage': coverage_pct,
                'states_list': scenario['STATES_WITH_SKILLS'].split(','),
                'missing_states': [],
                'mode': 'with_bridge'
            }
    
    def get_equivalent_skills_across_states(self, skill_id: str = None, master_concept: str = None) -> pd.DataFrame:
        """
        Find conceptually equivalent skills in other states.
        
        Uses taxonomy mappings to find variants.
        
        Args:
            skill_id: Optional ROCK skill ID to find equivalents for
            master_concept: Optional master concept name to find all skills for
            
        Returns:
            DataFrame with equivalent skills grouped by state
        """
        mappings = self.load_llm_skill_mappings()
        skills = self.load_skills()
        standard_skills = self.load_standard_skills()
        
        if mappings.empty:
            return pd.DataFrame()
        
        if skill_id:
            # Find taxonomy path for this skill
            skill_mapping = mappings[mappings['SKILL_ID'] == skill_id]
            if skill_mapping.empty:
                return pd.DataFrame()
            
            taxonomy_path = skill_mapping.iloc[0]['TAXONOMY_PATH']
            # Find other skills with same/similar taxonomy path
            mask = mappings['TAXONOMY_PATH'].str.contains(taxonomy_path, case=False, na=False)
            equivalent_mappings = mappings[mask]
        
        elif master_concept:
            # Find all skills for this master concept
            mask = mappings['TAXONOMY_PATH'].str.contains(master_concept, case=False, na=False)
            equivalent_mappings = mappings[mask]
        
        else:
            return pd.DataFrame()
        
        # Join with skills for details
        result = equivalent_mappings.merge(
            skills,
            on='SKILL_ID',
            how='left',
            suffixes=('_mapping', '_skill')
        )
        
        # Try to join with standard_skills to get education authority info
        if not standard_skills.empty:
            # Get unique education authorities per skill (may be multiple)
            # For demo purposes, we'll use mock state data from scenarios
            pass
        
        return result
    
    def get_content_by_concept(self, master_concept: str) -> pd.DataFrame:
        """
        Get all content items for a master concept.
        
        Args:
            master_concept: Name of master concept
            
        Returns:
            DataFrame with content items
        """
        content = self.load_content_library()
        mask = content['MASTER_CONCEPT'].str.contains(master_concept, case=False, na=False)
        return content[mask]
    
    def calculate_tagging_burden(self, content_id: str, with_bridge: bool = False) -> Dict:
        """
        Calculate tagging and maintenance burden for content.
        
        Args:
            content_id: Content item identifier
            with_bridge: If True, calculate with bridge layer
            
        Returns:
            Dict with time estimates and burden metrics
        """
        scenarios = self.load_tagging_scenarios()
        
        # Get scenario for this content
        scenario = scenarios[scenarios['CONTENT_ITEM'] == content_id]
        if scenario.empty:
            return {'error': 'Scenario not found'}
        
        scenario = scenario.iloc[0]
        matching_skills = scenario['MATCHING_ROCK_SKILLS_COUNT']
        
        # Time estimates (in minutes)
        time_per_tag = 5  # minutes to research and tag one skill
        
        if not with_bridge:
            # Option A: Tag only 1 state (fast but 2% coverage)
            option_a_time = time_per_tag
            option_a_coverage = 1
            
            # Option B: Tag all states (comprehensive but unsustainable)
            option_b_time = matching_skills * time_per_tag
            option_b_coverage = matching_skills
            
            return {
                'content_id': content_id,
                'matching_skills_count': matching_skills,
                'option_a': {
                    'description': 'Tag 1 state only',
                    'time_minutes': option_a_time,
                    'time_hours': option_a_time / 60,
                    'states_covered': option_a_coverage,
                    'coverage_pct': (option_a_coverage / matching_skills) * 100,
                    'maintenance_burden': 'Low (but coverage terrible)'
                },
                'option_b': {
                    'description': f'Tag all {matching_skills} states',
                    'time_minutes': option_b_time,
                    'time_hours': option_b_time / 60,
                    'states_covered': option_b_coverage,
                    'coverage_pct': 100.0,
                    'maintenance_burden': f'Extreme ({matching_skills} tags to maintain)'
                },
                'option_c': {
                    'description': 'Bypass ROCK entirely',
                    'time_minutes': 2,
                    'consequence': 'Lost: standards alignment, ROCK metadata, Star integration'
                },
                'mode': 'without_bridge'
            }
        else:
            # WITH BRIDGE: Tag once to master skill, inherit all state mappings
            bridge_time = time_per_tag  # Same initial time, but only once
            
            return {
                'content_id': content_id,
                'matching_skills_count': matching_skills,
                'bridge_solution': {
                    'description': 'Tag to master skill (1 tag)',
                    'time_minutes': bridge_time,
                    'time_hours': bridge_time / 60,
                    'states_covered': matching_skills,
                    'coverage_pct': 100.0,
                    'maintenance_burden': 'Minimal (1 master skill tag)',
                    'automatic_inheritance': f'Inherits {matching_skills} state skill mappings'
                },
                'time_savings_vs_option_b': {
                    'minutes_saved': (matching_skills * time_per_tag) - bridge_time,
                    'hours_saved': ((matching_skills * time_per_tag) - bridge_time) / 60,
                    'efficiency_gain_pct': ((matching_skills - 1) / matching_skills) * 100
                },
                'mode': 'with_bridge'
            }
    
    # ============================================================================
    # BASE SKILLS METHODS (for demo)
    # ============================================================================
    
    def get_base_skill_by_id(self, base_skill_id: str) -> Optional[pd.Series]:
        """Get base skill details by ID."""
        base_skills = self.load_base_skills()
        if base_skills.empty:
            return None
        
        skill = base_skills[base_skills['base_skill_id'] == base_skill_id]
        if skill.empty:
            return None
        
        return skill.iloc[0]
    
    def get_rock_skills_for_base_skill(self, base_skill_name: str) -> pd.DataFrame:
        """
        Get all ROCK skills that map to a specific base skill.
        Uses the enhanced metadata to find matching skills.
        """
        specifications = self.load_skill_specifications()
        
        if specifications.empty:
            return pd.DataFrame()
        
        # For now, we'll match on similar skill names since we don't have explicit mapping
        # In production, this would use a proper base_skill_id mapping table
        mask = specifications['SKILL_NAME'].str.contains(base_skill_name.split()[0], case=False, na=False)
        
        return specifications[mask]

