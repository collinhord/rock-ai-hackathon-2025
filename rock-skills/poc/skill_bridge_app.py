"""
ROCK Skills Bridge Explorer v2.0 - Optimized for Stakeholder Presentations

A streamlined Streamlit app demonstrating the value of bridging ROCK skills to 
Science of Reading taxonomy with a clear narrative-driven hierarchy.

Architecture:
- Executive View: Problem → Solution narrative (5-minute stakeholder overview)
- Three-Level Deep Dive: MACRO/MID/MICRO organized exploration
- Interactive Explorer: Hands-on search and discovery tools
- Validation Dashboard: Quality metrics and validation suite integration
- Technical Reference: Implementation details for developers

Run with: streamlit run skill_bridge_app.py
Updated: 2025-10-17 - Full taxonomy mapping (59/59 base skills)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import re
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from data_loader import ROCKDataLoader

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="ROCK Skills Bridge Explorer v2.0",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved visual hierarchy
st.markdown("""
<style>
    /* Main headers with level-specific styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Level-specific colors */
    .macro-header { color: #1f77b4; border-color: #1f77b4; }
    .mid-header { color: #ff7f0e; border-color: #ff7f0e; }
    .micro-header { color: #2ca02c; border-color: #2ca02c; }
    
    /* Metric cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    .metric-card-problem {
        border-left-color: #d62728;
    }
    
    .metric-card-solution {
        border-left-color: #2ca02c;
    }
    
    /* Highlights and callouts */
    .highlight {
        background-color: #ffffcc;
        padding: 0.2rem 0.4rem;
        border-radius: 0.3rem;
    }
    
    .callout-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .callout-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    
    .callout-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    
    .callout-success {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Export button styling */
    .export-button {
        float: right;
        margin-top: -3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def natural_sort_key(text):
    """Generate a key for natural (alphanumeric) sorting."""
    if pd.isna(text):
        return [0]
    def atoi(text_part):
        return int(text_part) if text_part.isdigit() else text_part.lower()
    return [atoi(c) for c in re.split(r'(\d+)', str(text))]

def natural_sort(items):
    """Sort a list of items using natural (alphanumeric) sorting."""
    return sorted(items, key=natural_sort_key)

def format_grade_display(grade_level_name):
    """Format grade level for display."""
    if pd.isna(grade_level_name):
        return "Unknown"
    grade_str = str(grade_level_name).strip()
    if grade_str.startswith("Grade"):
        return grade_str
    if grade_str.isdigit() or (grade_str and grade_str[0].isdigit()):
        return f"Grade {grade_str}"
    return grade_str

# Initialize data loader
@st.cache_resource
def get_data_loader():
    """Initialize and cache the data loader."""
    base_dir = Path(__file__).resolve().parent.parent
    schema_dir = base_dir / 'rock_data'
    analysis_dir = base_dir / 'analysis'
    
    if not schema_dir.exists():
        st.error(f"Schema directory not found: {schema_dir}")
        st.stop()
    
    return ROCKDataLoader(schema_dir, analysis_dir)

loader = get_data_loader()

# Load validation results (cached)
@st.cache_data
def load_validation_results():
    """Load all validation suite outputs."""
    base_path = Path(__file__).parent.parent / 'frameworks' / 'validation_outputs'
    
    results = {}
    
    # Check if validation outputs exist
    if not base_path.exists():
        return None
    
    try:
        # Load CSVs
        if (base_path / 'potential_duplicates.csv').exists():
            results['duplicates'] = pd.read_csv(base_path / 'potential_duplicates.csv')
        
        if (base_path / 'sibling_conflicts.csv').exists():
            results['sibling_conflicts'] = pd.read_csv(base_path / 'sibling_conflicts.csv')
        
        if (base_path / 'concept_confidence.csv').exists():
            results['concept_confidence'] = pd.read_csv(base_path / 'concept_confidence.csv')
        
        if (base_path / 'recommendations_priority.csv').exists():
            results['recommendations'] = pd.read_csv(base_path / 'recommendations_priority.csv')
        
        # Load markdown reports
        if (base_path / 'semantic_validation_report.md').exists():
            results['semantic_report'] = (base_path / 'semantic_validation_report.md').read_text()
        
        if (base_path / 'framework_convergence_summary.md').exists():
            results['convergence_report'] = (base_path / 'framework_convergence_summary.md').read_text()
        
        if (base_path / 'validation_master_report.md').exists():
            results['master_report'] = (base_path / 'validation_master_report.md').read_text()
        
        return results if results else None
    
    except Exception as e:
        st.warning(f"Could not load validation results: {e}")
        return None

# ============================================================================
# NAVIGATION & SIDEBAR
# ============================================================================

st.sidebar.title("🔗 Skills Bridge Explorer v2.0")
st.sidebar.markdown("**Narrative-Driven Taxonomy Analysis**")
st.sidebar.markdown("---")

# Simplified navigation - enhanced sections
page = st.sidebar.radio(
    "Navigation",
    [
        "🎯 Executive View",
        "🔬 Three-Level Deep Dive",
        "⚡ Base Skills Explorer",
        "📖 Demo Scenarios",
        "🧭 Interactive Explorer",
        "📊 Validation Dashboard",
        "🔧 Technical Reference"
    ],
    help="Navigate through different views of the Skills Bridge solution"
)

st.sidebar.markdown("---")

# Quick stats in sidebar
try:
    concepts_df = loader.load_master_concepts()
    skill_mapping = loader.load_skill_master_concept_mapping()
    
    if not concepts_df.empty and not skill_mapping.empty:
        st.sidebar.markdown("### 📈 Quick Stats")
        total_skills = len(skill_mapping)
        total_concepts = len(concepts_df)
        
        if total_concepts > 0:
            redundancy_ratio = total_skills / total_concepts
            st.sidebar.metric("Total ROCK Skills", f"{total_skills:,}")
            st.sidebar.metric("Master Concepts", f"{total_concepts:,}")
            st.sidebar.metric("Redundancy Ratio", f"{redundancy_ratio:.1f}x")
except Exception as e:
    pass  # Silently handle if data not available

st.sidebar.markdown("---")
st.sidebar.markdown("### About v2.0")
st.sidebar.info(
    "**New in v2.0:**\n\n"
    "✨ Narrative-driven organization\n\n"
    "🎯 Executive-friendly overview\n\n"
    "🔬 Clear MACRO/MID/MICRO levels\n\n"
    "📊 Integrated validation suite\n\n"
    "🚀 Streamlined for stakeholders"
)

# ============================================================================
# PAGE 1: EXECUTIVE VIEW
# ============================================================================

if page == "🎯 Executive View":
    st.markdown('<div class="main-header">Executive View: Problem → Solution</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">A 5-minute overview of the master skill fragmentation problem and our three-level solution</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # SECTION A: THE PROBLEM
    # ========================================================================
    
    st.markdown("## 🚨 The Problem: Skill Fragmentation")
    
    col1, col2, col3 = st.columns(3)
    
    # Load data for metrics
    try:
        concepts_df = loader.load_master_concepts()
        skill_mapping = loader.load_skill_master_concept_mapping()
        
        if not concepts_df.empty and not skill_mapping.empty:
            total_skills = len(skill_mapping)
            total_concepts = len(concepts_df)
            redundancy_ratio = total_skills / total_concepts if total_concepts > 0 else 0
            overlap_pct = ((redundancy_ratio - 1) / redundancy_ratio * 100) if redundancy_ratio > 1 else 0
            
            with col1:
                st.markdown('<div class="metric-card metric-card-problem">', unsafe_allow_html=True)
                st.metric("Total ROCK Skills", f"{total_skills:,}", 
                         help="Total number of skills in ROCK database")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card metric-card-problem">', unsafe_allow_html=True)
                st.metric("Redundancy Ratio", f"~{redundancy_ratio:.1f}x",
                         delta=f"+{redundancy_ratio-1:.1f}x redundant",
                         delta_color="inverse",
                         help="Average number of skills per unique master concept")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card metric-card-problem">', unsafe_allow_html=True)
                st.metric("Conceptual Overlap", f"{overlap_pct:.0f}%",
                         help="Percentage of skills that are redundant variants")
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ Data not yet loaded. Please run the data pipeline first.")
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
    
    st.markdown("""
    <div class="callout-box callout-warning">
    <strong>The Core Problem:</strong> ROCK skills derive from 50+ state standards with no master taxonomy 
    to connect conceptually equivalent skills. The same learning concept appears 6-8 times 
    across states using different terminology, grade assignments, and scope qualifiers—with 
    <strong>zero metadata linking them</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    # Concrete example visualization
    st.markdown("### Concrete Example: Phoneme Blending Fragmentation")
    
    # Create example data for visualization
    example_skills = pd.DataFrame({
        'State': ['CCSS', 'Texas', 'California', 'Virginia', 'Ohio', 'Florida', 'New York', 'Illinois'],
        'Skill Name': [
            'Blend phonemes to form words',
            'Blend spoken phonemes into one-syllable words',
            'Orally blend 2-3 phonemes into recognizable words',
            'Blend sounds to make one-syllable words',
            'Orally produce words by blending sounds',
            'Blend phonemes in spoken words',
            'Blend sounds (phonemes) to make words',
            'Orally blend individual sounds in words'
        ],
        'Grade': ['K', 'K', 'K', 'K-1', 'K', 'K', 'K', 'K'],
        'Skill Count': [1, 1, 1, 1, 1, 1, 1, 1]  # For bar chart
    })
    
    fig = px.bar(example_skills, x='State', y='Skill Count',
                 hover_data={'Skill Name': True, 'Grade': True, 'Skill Count': False},
                 color_discrete_sequence=['#d62728'],
                 title="One Concept → 8 State-Specific Skills (No Linking Metadata)")
    fig.update_layout(showlegend=False, yaxis_title="Redundant Skills", xaxis_title="State Standard")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 View all 8 skill variants"):
        st.dataframe(example_skills[['State', 'Skill Name', 'Grade']], use_container_width=True, hide_index=True)
    
    st.markdown("""
    **Business Impact:**
    - 🔍 **Discovery**: 3 hours to manually find all variants
    - 💰 **Cost**: Duplicate content development for each state
    - 📊 **Research**: Cannot aggregate data across state variants  
    - 👥 **Educators**: Unclear which skills are redundant vs. progressive
    """)
    
    # ========================================================================
    # SECTION B: THE SOLUTION
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## ✅ The Solution: Three-Level Taxonomy Bridge")
    
    st.markdown("""
    <div class="callout-box callout-success">
    <strong>Our Approach:</strong> Build a scientifically-grounded taxonomy bridge that connects ROCK skills 
    to evidence-based frameworks (Science of Reading) without modifying ROCK—enabling discovery, 
    deduplication, and enrichment across three integrated levels.
    </div>
    """, unsafe_allow_html=True)
    
    # Three-level architecture visualization
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 MACRO Level")
        st.markdown("""
        **Master Taxonomy & Frameworks**
        
        Connect skills to Science of Reading framework
        
        - Framework convergence analysis
        - Taxonomy hierarchy mapping
        - Learning progression tracking
        
        <div class="metric-card">
        <strong>Value:</strong> Scientific grounding + cross-state bridging
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔍 MID Level")
        st.markdown("""
        **Redundancy & Variant Analysis**
        
        Identify and group conceptually equivalent skills
        
        - Semantic similarity detection
        - State variant clustering
        - MECE validation
        
        <div class="metric-card">
        <strong>Value:</strong> 60-75% redundancy elimination
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🔬 MICRO Level")
        st.markdown("""
        **Metadata & Skill Quality**
        
        Extract fine-grained metadata from skills
        
        - NLP-based concept parsing
        - Metadata enrichment
        - Quality scoring
        
        <div class="metric-card">
        <strong>Value:</strong> Concept-aware analysis
        </div>
        """, unsafe_allow_html=True)
    
    # Before/After comparison
    st.markdown("### Before vs. After Comparison")
    
    before_after = pd.DataFrame({
        'Metric': ['Search Time', 'Skills Found', 'Relationships', 'Framework Support', 'Content Reuse'],
        'Without Bridge': ['3 hours', '5 of 12', 'None', 'Unknown', '0% (isolated)'],
        'With Bridge': ['30 seconds', '12 of 12', 'Automatic', 'Validated', '100% (connected)'],
        'Improvement': ['99% faster', '140% more', '∞', 'Grounded', '∞']
    })
    
    st.dataframe(before_after, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # SECTION C: IMPACT & NEXT STEPS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 🎯 Stakeholder Impact")
    
    impact_matrix = pd.DataFrame({
        'Stakeholder': [
            'Curriculum Developers',
            'Product Teams',
            'Data Scientists',
            'Educators',
            'Researchers'
        ],
        'Current Pain Point': [
            'Cannot discover all relevant skills',
            'Cannot build adaptive features',
            'Cannot aggregate across states',
            'Unclear skill relationships',
            'Manual skill coding required'
        ],
        'With Taxonomy Bridge': [
            'Find all 12 variants in 30 seconds',
            'Build evidence-based progressions',
            'Aggregate by master concepts',
            'See clear learning paths',
            'Research-grade data export'
        ],
        'Efficiency Gain': [
            '70-80%',
            '∞ (previously blocked)',
            '90%',
            '60%',
            '85%'
        ]
    })
    
    st.dataframe(impact_matrix, use_container_width=True, hide_index=True)
    
    # Success metrics
    st.markdown("### 📊 POC Success Metrics")
    
    metrics_col1, metrics_col2 = st.columns(2)
    
    with metrics_col1:
        st.markdown("""
        **Analysis Results:**
        - ✅ 6.8x redundancy ratio confirmed
        - ✅ 15 concrete skill clusters documented
        - ✅ 50+ skills mapped to SoR taxonomy
        """)
    
    with metrics_col2:
        st.markdown("""
        **Validation Results:**
        - ✅ Semantic similarity validator operational
        - ✅ Framework convergence tracker active
        - ✅ MECE quality scores calculated
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("### 🚀 Explore the Prototype")
    
    cta_col1, cta_col2, cta_col3 = st.columns(3)
    
    with cta_col1:
        if st.button("🔬 Explore Three Levels", use_container_width=True):
            st.info("Navigate to 'Three-Level Deep Dive' in the sidebar →")
    
    with cta_col2:
        if st.button("🧭 Try Interactive Tools", use_container_width=True):
            st.info("Navigate to 'Interactive Explorer' in the sidebar →")
    
    with cta_col3:
        if st.button("📊 View Validation Results", use_container_width=True):
            st.info("Navigate to 'Validation Dashboard' in the sidebar →")

# ============================================================================
# PAGE 2: THREE-LEVEL DEEP DIVE
# ============================================================================

elif page == "🔬 Three-Level Deep Dive":
    st.markdown('<div class="main-header">Three-Level Deep Dive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore the problem-solution space organized by conceptual level</div>', unsafe_allow_html=True)
    
    # Tab interface for three levels
    tab1, tab2, tab3 = st.tabs(["🎯 MACRO Level", "🔍 MID Level", "🔬 MICRO Level"])
    
    # ========================================================================
    # TAB 1: MACRO LEVEL
    # ========================================================================
    with tab1:
        st.markdown('<div class="macro-header" style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">MACRO Level: Master Taxonomy & Framework Convergence</div>', unsafe_allow_html=True)
        
        st.markdown("""
        **Focus:** Connect ROCK skills to evidence-based frameworks and master taxonomies.
        
        **Key Questions:**
        - Which concepts have strong multi-framework support?
        - How do ROCK skills map to Science of Reading hierarchy?
        - Where are potential duplicates at the concept level?
        """)
        
        # Component A: Framework Convergence Dashboard
        st.markdown("### 📊 Framework Convergence Dashboard")
        
        validation_results = load_validation_results()
        
        if validation_results and 'concept_confidence' in validation_results:
            confidence_df = validation_results['concept_confidence']
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            strong = len(confidence_df[confidence_df['Evidence_Strength'] == 'strong'])
            moderate = len(confidence_df[confidence_df['Evidence_Strength'] == 'moderate'])
            weak = len(confidence_df[confidence_df['Evidence_Strength'] == 'weak'])
            unvalidated = len(confidence_df[confidence_df['Evidence_Strength'] == 'unvalidated'])
            
            with col1:
                st.metric("Strong Evidence (3+ frameworks)", strong)
            with col2:
                st.metric("Moderate Evidence (2 frameworks)", moderate)
            with col3:
                st.metric("Weak Evidence (1 framework)", weak)
            with col4:
                st.metric("Unvalidated (0 frameworks)", unvalidated)
            
            # Convergence distribution
            evidence_dist = confidence_df['Evidence_Strength'].value_counts()
            fig = px.pie(values=evidence_dist.values, names=evidence_dist.index,
                        title="Evidence Strength Distribution",
                        color_discrete_map={
                            'strong': '#2ca02c',
                            'moderate': '#ff7f0e',
                            'weak': '#ffcc00',
                            'unvalidated': '#d62728'
                        })
            st.plotly_chart(fig, use_container_width=True)
            
            # Top validated concepts
            with st.expander("📋 View top validated concepts"):
                top_concepts = confidence_df[confidence_df['Convergence_Score'] > 0].sort_values('Convergence_Score', ascending=False).head(20)
                st.dataframe(top_concepts[['Concept_Name', 'Convergence_Score', 'Frameworks', 'Evidence_Strength']], 
                           use_container_width=True, hide_index=True)
        
        else:
            st.info("⚠️ Framework convergence data not yet generated. Run the validation suite first.")
            if st.button("📖 Learn how to run validation suite"):
                st.code("cd frameworks\npython3 run_full_validation.py")
        
        st.markdown("---")
        
        # Component B: Taxonomy Browser
        st.markdown("### 🌳 Science of Reading Taxonomy Browser")
        
        try:
            taxonomy_path = Path(__file__).parent.parent / 'POC_science_of_reading_literacy_skills_taxonomy.csv'
            if taxonomy_path.exists():
                taxonomy_df = pd.read_csv(taxonomy_path)
                
                # Show hierarchy overview
                st.markdown("**6-Level Hierarchy:**")
                hierarchy_levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
                
                level_counts = {}
                for level in hierarchy_levels:
                    if level in taxonomy_df.columns:
                        level_counts[level] = taxonomy_df[level].nunique()
                
                counts_df = pd.DataFrame(list(level_counts.items()), columns=['Level', 'Unique Concepts'])
                st.dataframe(counts_df, use_container_width=True, hide_index=True)
                
                # Interactive exploration
                selected_strand = st.selectbox("Explore Strand:", 
                                              options=['All'] + sorted(taxonomy_df['Strand'].dropna().unique().tolist()))
                
                if selected_strand != 'All':
                    strand_data = taxonomy_df[taxonomy_df['Strand'] == selected_strand]
                    
                    # Show pillars in this strand
                    pillars = sorted(strand_data['Pillar'].dropna().unique().tolist())
                    st.markdown(f"**Pillars in {selected_strand}:** {', '.join(pillars)}")
                    
                    with st.expander(f"📋 View all concepts in {selected_strand}"):
                        display_cols = [col for col in hierarchy_levels if col in strand_data.columns]
                        st.dataframe(strand_data[display_cols].drop_duplicates(), use_container_width=True, hide_index=True)
            
            else:
                st.warning("Taxonomy file not found")
        
        except Exception as e:
            st.error(f"Error loading taxonomy: {e}")
        
        st.markdown("---")
        
        # Component C: Semantic Similarity Network
        st.markdown("### 🕸️ Semantic Similarity Network")
        
        if validation_results and 'duplicates' in validation_results:
            duplicates_df = validation_results['duplicates']
            
            # High similarity pairs
            high_sim = duplicates_df[duplicates_df['similarity'] >= 0.90]
            
            st.metric("High-Similarity Concept Pairs (>0.90)", len(high_sim))
            
            if len(high_sim) > 0:
                st.markdown("**Top 10 Most Similar Concept Pairs:**")
                
                top_pairs = high_sim.nlargest(10, 'similarity')[['concept1_name', 'concept2_name', 'similarity', 'same_level', 'same_strand']]
                st.dataframe(top_pairs, use_container_width=True, hide_index=True)
                
                with st.expander("📊 View similarity distribution"):
                    fig = px.histogram(duplicates_df, x='similarity', nbins=50,
                                     title="Distribution of Semantic Similarity Scores",
                                     labels={'similarity': 'Cosine Similarity', 'count': 'Frequency'})
                    fig.add_vline(x=0.85, line_dash="dash", line_color="orange", annotation_text="Medium threshold")
                    fig.add_vline(x=0.90, line_dash="dash", line_color="red", annotation_text="High threshold")
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("⚠️ Semantic similarity data not yet generated. Run the validation suite first.")
    
    # ========================================================================
    # TAB 2: MID LEVEL
    # ========================================================================
    with tab2:
        st.markdown('<div class="mid-header" style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">MID Level: Redundancy & Variant Analysis</div>', unsafe_allow_html=True)
        
        st.markdown("""
        **Focus:** Identify and resolve redundant or highly similar skills.
        
        **Key Questions:**
        - Which skills are conceptual duplicates across states?
        - Where do we have sibling conflicts (similar concepts at same level)?
        - What is our MECE quality score?
        """)
        
        # Component A: Redundancy Overview
        st.markdown("### 📊 Redundancy Overview")
        
        validation_results = load_validation_results()
        
        if validation_results:
            col1, col2, col3 = st.columns(3)
            
            if 'duplicates' in validation_results:
                duplicates_df = validation_results['duplicates']
                high_pri = len(duplicates_df[duplicates_df['similarity'] >= 0.90])
                med_pri = len(duplicates_df[(duplicates_df['similarity'] >= 0.85) & (duplicates_df['similarity'] < 0.90)])
                
                with col1:
                    st.metric("High-Priority Duplicates (>0.90)", high_pri, 
                             delta=f"{'Critical' if high_pri > 50 else 'Moderate' if high_pri > 10 else 'Good'}")
                with col2:
                    st.metric("Medium-Priority Overlaps (0.85-0.90)", med_pri)
            
            if 'sibling_conflicts' in validation_results:
                siblings_df = validation_results['sibling_conflicts']
                with col3:
                    st.metric("Sibling Conflicts", len(siblings_df))
        
        else:
            st.info("⚠️ Run validation suite to see redundancy metrics")
        
        # Component B: Interactive Grooming Interface
        st.markdown("---")
        st.markdown("### 🧹 Redundancy Grooming Interface")
        
        if validation_results and 'recommendations' in validation_results:
            rec_df = validation_results['recommendations']
            
            # Filter controls
            priority_filter = st.multiselect("Filter by Priority:", 
                                            options=[1, 2, 3],
                                            default=[1],
                                            help="1 = High priority, 2 = Medium, 3 = Low")
            
            filtered_recs = rec_df[rec_df['Priority'].isin(priority_filter)]
            
            st.markdown(f"**Showing {len(filtered_recs)} recommendations**")
            
            # Display recommendations
            st.dataframe(filtered_recs, use_container_width=True, hide_index=True)
            
            # Export option
            csv = filtered_recs.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Recommendations CSV", 
                             data=csv,
                             file_name="redundancy_recommendations.csv",
                             mime="text/csv")
        
        else:
            st.info("⚠️ Recommendations not yet generated. Run validation suite first.")
        
        # Component C: Variant Cluster Explorer
        st.markdown("---")
        st.markdown("### 🗺️ State Variant Cluster Explorer")
        
        try:
            variants_df = loader.load_variant_classification()
            
            if not variants_df.empty:
                # Filter to skills with equivalence groups only
                grouped_skills = variants_df[variants_df['EQUIVALENCE_GROUP_ID'].notna()]
                
                if not grouped_skills.empty:
                    # Show variant summary using EQUIVALENCE_GROUP_ID
                    variant_counts = grouped_skills.groupby('EQUIVALENCE_GROUP_ID').agg({
                        'SKILL_ID': 'count',
                        'SKILL_NAME': 'first',
                        'EQUIVALENCE_TYPE': 'first'
                    }).reset_index()
                    variant_counts.columns = ['EQUIVALENCE_GROUP_ID', 'variant_count', 'example_skill', 'type']
                    high_redundancy = variant_counts[variant_counts['variant_count'] >= 5]
                    
                    st.metric("Equivalence Groups with 5+ Variants", len(high_redundancy))
                    
                    with st.expander("📋 View high-redundancy equivalence groups"):
                        display_df = high_redundancy[['example_skill', 'variant_count', 'type']].sort_values('variant_count', ascending=False).head(20)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info("⚠️ No equivalence groups found in variant data")
            
            else:
                st.info("⚠️ Variant classification data not yet loaded")
        
        except Exception as e:
            st.warning(f"Could not load variant data: {e}")
    
    # ========================================================================
    # TAB 3: MICRO LEVEL
    # ========================================================================
    with tab3:
        st.markdown('<div class="micro-header" style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">MICRO Level: Skill Metadata & Quality</div>', unsafe_allow_html=True)
        
        st.markdown("""
        **Focus:** Extract and analyze fine-grained metadata from individual skills.
        
        **Key Questions:**
        - How complete is our metadata coverage?
        - What metadata fields have been extracted?
        - Which skills have quality issues?
        """)
        
        # Component A: Metadata Dashboard
        st.markdown("### 📊 Skill Metadata Dashboard")
        
        try:
            concepts_df = loader.load_master_concepts()
            
            if not concepts_df.empty:
                # Metadata coverage metrics
                total_concepts = len(concepts_df)
                
                # Check which fields are populated
                metadata_fields = ['DESCRIPTION', 'SOR_STRAND', 'SOR_PILLAR', 'SOR_DOMAIN', 
                                 'TEXT_TYPE', 'TEXT_MODE', 'SKILL_DOMAIN']
                
                coverage_data = []
                for field in metadata_fields:
                    if field in concepts_df.columns:
                        populated = concepts_df[field].notna().sum()
                        coverage_pct = (populated / total_concepts * 100) if total_concepts > 0 else 0
                        coverage_data.append({
                            'Field': field,
                            'Populated': populated,
                            'Coverage %': f"{coverage_pct:.1f}%"
                        })
                
                coverage_df = pd.DataFrame(coverage_data)
                st.dataframe(coverage_df, use_container_width=True, hide_index=True)
                
                # Visualize coverage
                fig = px.bar(coverage_df, x='Field', y='Populated',
                           title="Metadata Field Population",
                           labels={'Populated': 'Number of Concepts'})
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.warning("⚠️ Master concepts not yet loaded")
        
        except Exception as e:
            st.error(f"Error loading metadata: {e}")
        
        st.markdown("---")
        
        # Component B: Metadata Enrichment Status
        st.markdown("### ⚙️ Metadata Enrichment Pipeline")
        
        st.info("""
        **Pipeline Status:** Ready for execution
        
        The metadata enrichment pipeline uses NLP and LLM techniques to extract:
        - Action verbs and targets
        - Text types and modes
        - Complexity indicators
        - Pedagogical metadata
        
        Run pipeline from command line: `cd analysis && python3 scripts/batch_map_skills_enhanced.py`
        """)
        
        # Component C: Skill Quality Inspector
        st.markdown("---")
        st.markdown("### 🔍 Skill Quality Inspector")
        
        st.markdown("Quick search for specific skills:")
        
        search_term = st.text_input("Search skills:", placeholder="Enter skill name or concept...")
        
        if search_term:
            try:
                skill_mapping = loader.load_skill_master_concept_mapping()
                
                # Search in skill names
                matches = skill_mapping[skill_mapping['SKILL_NAME'].str.contains(search_term, case=False, na=False)]
                
                if not matches.empty:
                    st.markdown(f"**Found {len(matches)} matching skills:**")
                    st.dataframe(matches[['SKILL_NAME', 'MASTER_CONCEPT_NAME', 'SOR_STRAND', 'SOR_PILLAR']].head(20),
                               use_container_width=True, hide_index=True)
                else:
                    st.warning("No skills found matching your search.")
            
            except Exception as e:
                st.error(f"Error searching skills: {e}")

# ============================================================================
# PAGE 3: BASE SKILLS EXPLORER
# ============================================================================

elif page == "⚡ Base Skills Explorer":
    st.markdown('<div class="main-header">Base Skills Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Discover how base skills reduce redundancy and enable taxonomy-powered organization</div>', unsafe_allow_html=True)
    
    # Load base skills data (now includes taxonomy mappings)
    try:
        base_skills = loader.load_base_skills()
        specifications = loader.load_skill_specifications()
        
        if base_skills.empty:
            st.warning("⚠️ Base skills data not loaded. Please ensure base_skills_summary.json exists in /taxonomy/base_skills/")
        else:
            # ========================================================================
            # SECTION A: Overview Metrics
            # ========================================================================
            st.markdown("## 📊 Base Skills Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_base_skills = len(base_skills)
            total_rock_skills = base_skills['rock_skills_count'].sum()
            avg_redundancy = total_rock_skills / total_base_skills if total_base_skills > 0 else 0
            
            with col1:
                st.metric("Total Base Skills", f"{total_base_skills:,}")
            
            with col2:
                st.metric("Total ROCK Skills Collapsed", f"{total_rock_skills:,}")
            
            with col3:
                st.metric("Average Redundancy Ratio", f"{avg_redundancy:.1f}x")
            
            with col4:
                # Calculate how many have taxonomy mappings (from master concepts)
                if 'taxonomy_strand' in base_skills.columns:
                    mapped = base_skills['taxonomy_strand'].notna().sum()
                    coverage_pct = (mapped / total_base_skills * 100) if total_base_skills > 0 else 0
                    st.metric("Taxonomy Linked", f"{mapped}/{total_base_skills}")
                else:
                    st.metric("Taxonomy Status", "Pending Mapping")
            
            st.markdown("""
            <div class="callout-box callout-info">
            <strong>What are Base Skills?</strong> Base skills are the fundamental learning competencies that 
            multiple ROCK skills teach. By identifying base skills through specification extraction, we reduce 
            redundancy by <strong>{:.1f}x</strong> and enable precise taxonomy-based discovery.
            </div>
            """.format(avg_redundancy), unsafe_allow_html=True)
            
            # ========================================================================
            # SECTION B: Base Skills Distribution
            # ========================================================================
            st.markdown("---")
            st.markdown("## 📊 Redundancy Reduction Visualization")
            
            # Sort base skills by ROCK skill count
            top_base_skills = base_skills.sort_values('rock_skills_count', ascending=False).head(15)
            
            fig = px.bar(
                top_base_skills,
                x='base_skill_name',
                y='rock_skills_count',
                title="Top 15 Base Skills by ROCK Skill Count (Redundancy)",
                labels={'base_skill_name': 'Base Skill', 'rock_skills_count': 'ROCK Skills Collapsed'},
                color='rock_skills_count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Cognitive category distribution and taxonomy status
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### By Cognitive Category")
                cognitive_dist = base_skills['cognitive_category'].value_counts()
                fig2 = px.pie(
                    values=cognitive_dist.values,
                    names=cognitive_dist.index,
                    title="Base Skills by Cognitive Category"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                st.markdown("### Taxonomy Mapping Status")
                if 'taxonomy_strand' in base_skills.columns:
                    mapped_count = base_skills['taxonomy_strand'].notna().sum()
                    unmapped_count = base_skills['taxonomy_strand'].isna().sum()
                    fig_tax = px.pie(
                        values=[mapped_count, unmapped_count],
                        names=['Linked to Taxonomy', 'Pending Mapping'],
                        title="Taxonomy Linkage Status",
                        color_discrete_map={'Linked to Taxonomy': '#2ca02c', 'Pending Mapping': '#ff7f0e'}
                    )
                    st.plotly_chart(fig_tax, use_container_width=True)
                else:
                    st.info("Taxonomy mapping in progress")
            
            with col3:
                st.markdown("### Redundancy Distribution")
                fig3 = px.histogram(
                    base_skills,
                    x='rock_skills_count',
                    nbins=20,
                    title="ROCK Skills per Base Skill",
                    labels={'rock_skills_count': 'ROCK Skills Count', 'count': 'Frequency'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            # ========================================================================
            # SECTION C: Interactive Base Skills Browser
            # ========================================================================
            st.markdown("---")
            st.markdown("## 🔍 Interactive Base Skills Browser")
            
            # Search and filters
            search_col1, search_col2, search_col3, search_col4 = st.columns([2, 1, 1, 1])
            
            with search_col1:
                search_term = st.text_input("Search base skills:", placeholder="Enter skill name or description...")
            
            with search_col2:
                cognitive_filter = st.selectbox(
                    "Cognitive Category:",
                    options=['All'] + sorted(base_skills['cognitive_category'].dropna().unique().tolist())
                )
            
            with search_col3:
                taxonomy_filter = st.selectbox(
                    "Taxonomy Status:",
                    options=['All', 'Linked to Taxonomy', 'Pending Mapping']
                )
            
            with search_col4:
                min_skills = st.number_input("Min ROCK Skills:", min_value=0, value=0, step=1)
            
            # Apply filters
            filtered_base_skills = base_skills.copy()
            
            if search_term:
                mask = filtered_base_skills['base_skill_name'].str.contains(search_term, case=False, na=False) | \
                       filtered_base_skills['base_skill_description'].str.contains(search_term, case=False, na=False)
                filtered_base_skills = filtered_base_skills[mask]
            
            if cognitive_filter != 'All':
                filtered_base_skills = filtered_base_skills[filtered_base_skills['cognitive_category'] == cognitive_filter]
            
            if taxonomy_filter != 'All':
                if 'taxonomy_strand' in filtered_base_skills.columns:
                    if taxonomy_filter == 'Linked to Taxonomy':
                        filtered_base_skills = filtered_base_skills[filtered_base_skills['taxonomy_strand'].notna()]
                    elif taxonomy_filter == 'Pending Mapping':
                        filtered_base_skills = filtered_base_skills[filtered_base_skills['taxonomy_strand'].isna()]
            
            if min_skills > 0:
                filtered_base_skills = filtered_base_skills[filtered_base_skills['rock_skills_count'] >= min_skills]
            
            st.markdown(f"**Found {len(filtered_base_skills)} base skills:**")
            
            # Display base skills with drill-down
            if not filtered_base_skills.empty:
                for _, base_skill in filtered_base_skills.head(20).iterrows():
                    with st.expander(
                        f"⚡ {base_skill['base_skill_name']} "
                        f"({base_skill['rock_skills_count']} ROCK skills)"
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Description:** {base_skill['base_skill_description']}")
                            st.markdown(f"**Cognitive Category:** {base_skill['cognitive_category']}")
                            
                            # Show taxonomy information if available
                            if 'taxonomy_strand' in base_skill.index and pd.notna(base_skill.get('taxonomy_strand')):
                                st.markdown("**Taxonomy Classification:**")
                                st.markdown(f"- 🌳 Strand: {base_skill['taxonomy_strand']}")
                                st.markdown(f"- 📚 Pillar: {base_skill.get('taxonomy_pillar', 'N/A')}")
                                st.markdown(f"- 📖 Domain: {base_skill.get('taxonomy_domain', 'N/A')}")
                                st.caption(f"_{base_skill.get('taxonomy_source', 'Source: Master Concepts')}_")
                            else:
                                st.info("🔄 Taxonomy mapping pending - Link this base skill to Science of Reading framework")
                        
                        with col2:
                            st.metric("ROCK Skills", base_skill['rock_skills_count'])
                            st.markdown(f"**Confidence:** {base_skill.get('confidence', 'N/A')}")
                            st.markdown(f"**Created By:** {base_skill.get('created_by', 'N/A')}")
                            st.markdown(f"**Cluster ID:** {base_skill.get('cluster_id', 'N/A')}")
                        
                        # Try to show related ROCK skills from specifications
                        if not specifications.empty:
                            # Simple matching on first few words of base skill name
                            key_words = base_skill['base_skill_name'].split()[:3]
                            pattern = '|'.join(key_words)
                            
                            matching_specs = specifications[
                                specifications['SKILL_NAME'].str.contains(pattern, case=False, na=False)
                            ].head(5)
                            
                            if not matching_specs.empty:
                                st.markdown("**Sample ROCK Skills:**")
                                for _, spec in matching_specs.iterrows():
                                    st.markdown(
                                        f"- {spec['SKILL_NAME']} "
                                        f"(Grade {spec.get('GRADE_LEVEL_SHORT_NAME', 'N/A')}, "
                                        f"{spec.get('cognitive_demand', 'N/A')})"
                                    )
            else:
                st.info("No base skills match your search criteria. Try adjusting your filters.")
            
            # ========================================================================
            # SECTION D: Specifications Showcase
            # ========================================================================
            st.markdown("---")
            st.markdown("## 🔬 How Specifications Reveal Base Skills")
            
            st.markdown("""
            Specifications are structured metadata extracted from ROCK skill descriptions that reveal 
            what skills actually teach. By comparing specifications across skills, we can identify 
            which skills teach the same base concept.
            """)
            
            # Show example if specifications are available
            if not specifications.empty:
                st.markdown("### Example: Specifications Comparison")
                
                # Pick 2-3 skills from the same base skill category
                # For demonstration, let's pick skills about "identify" + "plot"
                example_skills = specifications[
                    specifications['SKILL_NAME'].str.contains('plot|character|story', case=False, na=False)
                ].head(3)
                
                if not example_skills.empty:
                    st.markdown("**Example Skills from the Filtered Dataset:**")
                    
                    for idx, (_, skill) in enumerate(example_skills.iterrows(), 1):
                        with st.expander(f"Skill {idx}: {skill['SKILL_NAME'][:80]}..."):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Structural Specifications:**")
                                st.markdown(f"- **Actions:** {skill.get('actions', 'N/A')}")
                                st.markdown(f"- **Targets:** {skill.get('targets', 'N/A')}")
                                st.markdown(f"- **Qualifiers:** {skill.get('qualifiers', 'N/A')}")
                                st.markdown(f"- **Root Verb:** {skill.get('root_verb', 'N/A')}")
                            
                            with col2:
                                st.markdown("**Educational Specifications:**")
                                st.markdown(f"- **Text Type:** {skill.get('text_type', 'N/A')}")
                                st.markdown(f"- **Text Mode:** {skill.get('text_mode', 'N/A')}")
                                st.markdown(f"- **Cognitive Demand:** {skill.get('cognitive_demand', 'N/A')}")
                                st.markdown(f"- **Task Complexity:** {skill.get('task_complexity', 'N/A')}")
                                st.markdown(f"- **Grade Band:** {skill.get('complexity_band', 'N/A')}")
                    
                    st.markdown("""
                    <div class="callout-box callout-success">
                    <strong>Key Insight:</strong> By comparing these specifications, we can see that these skills 
                    share similar actions, targets, and educational attributes, suggesting they teach related 
                    base competencies. This metadata-driven approach enables automatic grouping into base skills.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show specification statistics
                    st.markdown("### Specification Coverage Statistics")
                    
                    spec_fields = ['text_type', 'text_mode', 'cognitive_demand', 'task_complexity', 'skill_domain']
                    coverage_data = []
                    
                    for field in spec_fields:
                        if field in specifications.columns:
                            populated = specifications[field].notna().sum()
                            total = len(specifications)
                            coverage_pct = (populated / total * 100) if total > 0 else 0
                            coverage_data.append({
                                'Specification Field': field.replace('_', ' ').title(),
                                'Populated': populated,
                                'Total Skills': total,
                                'Coverage %': f"{coverage_pct:.1f}%"
                            })
                    
                    if coverage_data:
                        coverage_df = pd.DataFrame(coverage_data)
                        st.dataframe(coverage_df, use_container_width=True, hide_index=True)
                        
                        st.info(f"""
                        **Specification Extraction Summary:**
                        - Total skills with specifications: {len(specifications):,}
                        - Average specification coverage: {coverage_df['Coverage %'].str.rstrip('%').astype(float).mean():.1f}%
                        - Extraction method: Hybrid (spaCy NLP + LLM)
                        """)
            else:
                st.info("""
                ⚠️ **Specifications not available yet.**
                
                To generate specifications, run the metadata extraction pipeline:
                ```bash
                cd analysis/scripts
                python3 enhanced_metadata_extractor.py
                ```
                
                This will extract 23 metadata fields from each skill, including:
                - Structural: actions, targets, qualifiers
                - Educational: text type, cognitive demand, task complexity
                - Pedagogical: support level, complexity band
                """)
    
    except Exception as e:
        st.error(f"Error loading base skills: {e}")
        st.info("Make sure base skills have been extracted using the analysis pipeline.")

# ============================================================================
# PAGE 4: DEMO SCENARIOS
# ============================================================================

elif page == "📖 Demo Scenarios":
    st.markdown('<div class="main-header">Demo Scenarios</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pre-built scenarios demonstrating the power of taxonomy-enabled discovery</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to Interactive Demo Scenarios
    
    These scenarios demonstrate how combining **Base Skills** + **Specifications** + **Taxonomy** 
    enables dramatically better skill discovery and organization compared to traditional text search.
    """)
    
    # Scenario selector
    scenario = st.selectbox(
        "Choose a Demo Scenario:",
        [
            "Scenario A: Find All Phonological Awareness Skills for K-2",
            "Scenario B: Discover Analysis-Level Comprehension Skills for Fiction",
            "Scenario C: Cross-State Discovery - Find Equivalent Skills"
        ]
    )
    
    st.markdown("---")
    
    # ========================================================================
    # SCENARIO A: Phonological Awareness K-2
    # ========================================================================
    if scenario == "Scenario A: Find All Phonological Awareness Skills for K-2":
        st.markdown("## 🎯 Scenario A: Find All Phonological Awareness Skills for K-2")
        
        st.markdown("""
        **Use Case:** A curriculum developer needs to find all phonological awareness skills 
        appropriate for K-2 students to build a foundational literacy unit.
        
        **Without Taxonomy:** Simple text search for "phoneme" or "sound" returns 200+ results 
        across all grades, many irrelevant.
        
        **With Taxonomy:** Filter by Strand + Pillar + Grade Band → Precise results.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ❌ Without Taxonomy")
            st.code("""
Search: "phoneme" OR "sound"
Results: 200+ skills
Grade levels: K-12 (mixed)
Relevance: ~40%
Time to filter: 45 minutes
            """)
            st.markdown("**Problems:**")
            st.markdown("- Too many irrelevant results")
            st.markdown("- No grade-level precision")
            st.markdown("- Misses alternative terminology")
            st.markdown("- Manual filtering required")
        
        with col2:
            st.markdown("### ✅ With Taxonomy")
            st.code("""
Filters:
- Strand: Word Recognition
- Pillar: Phonological Awareness  
- Grade Band: K-2
Results: 15 precise skills
Relevance: ~95%
Time to filter: 30 seconds
            """)
            st.markdown("**Benefits:**")
            st.markdown("- Precise, grade-appropriate results")
            st.markdown("- Scientifically organized")
            st.markdown("- Finds skills regardless of wording")
            st.markdown("- Immediate, no manual work")
        
        st.markdown("---")
        st.markdown("### 🚀 Try It Live")
        
        if st.button("🎬 Run Scenario A", type="primary"):
            try:
                specifications = loader.load_skill_specifications()
                
                if not specifications.empty:
                    # Apply filters
                    filtered = specifications[
                        (specifications['complexity_band'] == 'K-2') &
                        (specifications['skill_domain'] == 'reading')
                    ]
                    
                    # Look for phonological awareness indicators
                    phon_terms = ['phoneme', 'sound', 'blend', 'segment', 'isolate', 'manipulate']
                    pattern = '|'.join(phon_terms)
                    filtered = filtered[filtered['SKILL_NAME'].str.contains(pattern, case=False, na=False)]
                    
                    st.success(f"✅ Found {len(filtered)} phonological awareness skills for K-2!")
                    
                    if not filtered.empty:
                        display_cols = ['SKILL_NAME', 'GRADE_LEVEL_SHORT_NAME', 'cognitive_demand', 'task_complexity']
                        available_cols = [col for col in display_cols if col in filtered.columns]
                        st.dataframe(filtered[available_cols].head(15), use_container_width=True, hide_index=True)
                else:
                    st.info("⚠️ Specifications data not available. Run the metadata extraction pipeline first.")
            
            except Exception as e:
                st.error(f"Error running scenario: {e}")
    
    # ========================================================================
    # SCENARIO B: Analysis-Level Comprehension for Fiction
    # ========================================================================
    elif scenario == "Scenario B: Discover Analysis-Level Comprehension Skills for Fiction":
        st.markdown("## 🎯 Scenario B: Discover Analysis-Level Comprehension Skills for Fiction")
        
        st.markdown("""
        **Use Case:** A teacher wants to find high-level analytical reading skills for a fiction 
        unit in grades 6-8.
        
        **Without Taxonomy:** Search "analyze fiction" returns many skills, but mix of complexity 
        levels and text types.
        
        **With Taxonomy:** Multi-dimensional filter for exact requirements.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ❌ Without Taxonomy")
            st.code("""
Search: "analyze fiction"
Results: 80+ mixed skills
Complexity: All levels
Text types: Mixed
Time to filter: 30 minutes
            """)
        
        with col2:
            st.markdown("### ✅ With Taxonomy")
            st.code("""
Filters:
- Cognitive Demand: analysis
- Text Type: fictional
- Domain: Comprehension
- Grade Band: 6-8
Results: 12 precise skills
Time to filter: 15 seconds
            """)
        
        st.markdown("---")
        st.markdown("### 🚀 Try It Live")
        
        if st.button("🎬 Run Scenario B", type="primary"):
            try:
                specifications = loader.load_skill_specifications()
                
                if not specifications.empty:
                    filtered = specifications[
                        (specifications['cognitive_demand'] == 'analysis') &
                        (specifications['text_type'] == 'fictional') &
                        (specifications['skill_domain'] == 'reading') &
                        (specifications['complexity_band'].isin(['6-8', '9-12']))
                    ]
                    
                    st.success(f"✅ Found {len(filtered)} analysis-level fiction comprehension skills!")
                    
                    if not filtered.empty:
                        display_cols = ['SKILL_NAME', 'GRADE_LEVEL_SHORT_NAME', 'text_type', 'text_mode', 'cognitive_demand']
                        available_cols = [col for col in display_cols if col in filtered.columns]
                        st.dataframe(filtered[available_cols].head(12), use_container_width=True, hide_index=True)
                else:
                    st.info("⚠️ Specifications data not available.")
            
            except Exception as e:
                st.error(f"Error running scenario: {e}")
    
    # ========================================================================
    # SCENARIO C: Cross-State Discovery
    # ========================================================================
    elif scenario == "Scenario C: Cross-State Discovery - Find Equivalent Skills":
        st.markdown("## 🎯 Scenario C: Cross-State Discovery - Find Equivalent Skills")
        
        st.markdown("""
        **Use Case:** A content creator wants to find all state-specific variations of a skill 
        to ensure their content is discoverable across states.
        
        **The Problem:** Without base skills, the same learning concept appears as 8+ different 
        skills across states with no linking metadata.
        
        **The Solution:** Base skills group equivalent skills, enabling cross-state discovery.
        """)
        
        # Example: Show base skill with multiple ROCK skill variants
        try:
            base_skills = loader.load_base_skills()
            
            if not base_skills.empty:
                # Pick a base skill with high ROCK skill count
                example_base_skill = base_skills.sort_values('rock_skills_count', ascending=False).iloc[0]
                
                st.markdown("### Example: Base Skill with Multiple State Variants")
                
                st.info(f"""
                **Base Skill:** {example_base_skill['base_skill_name']}
                
                **Description:** {example_base_skill['base_skill_description']}
                
                **ROCK Skill Variants:** {example_base_skill['rock_skills_count']} equivalent skills across states
                """)
                
                st.markdown("**Impact:**")
                st.markdown(f"- ✅ **With Base Skills:** Tag content once → Discoverable by all {example_base_skill['rock_skills_count']} state variants")
                st.markdown(f"- ❌ **Without Base Skills:** Tag {example_base_skill['rock_skills_count']} times → Maintenance nightmare")
                
                efficiency_gain = ((example_base_skill['rock_skills_count'] - 1) / example_base_skill['rock_skills_count']) * 100
                st.metric("Efficiency Gain", f"{efficiency_gain:.0f}%")
        
        except Exception as e:
            st.error(f"Error loading base skills: {e}")

# ============================================================================
# PAGE 5: INTERACTIVE EXPLORER
# ============================================================================

elif page == "🧭 Interactive Explorer":
    st.markdown('<div class="main-header">Interactive Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Hands-on discovery tools for exploring skills, concepts, and taxonomy</div>', unsafe_allow_html=True)
    
    # Sub-navigation for explorer tools
    explorer_tab = st.radio(
        "Choose Explorer Tool:",
        ["🔍 Concept Browser", "🎯 Skill Search & Inspector", "🌳 Taxonomy Navigator"],
        horizontal=True
    )
    
    # ========================================================================
    # EXPLORER A: CONCEPT BROWSER
    # ========================================================================
    if explorer_tab == "🔍 Concept Browser":
        st.markdown("### Master Concept Browser")
        st.markdown("Search and explore master concepts with all their ROCK skill mappings.")
        
        # Search interface
        search_concept = st.text_input("🔎 Search for a concept:", 
                                      placeholder="e.g., phoneme blending, context clues, main idea...")
        
        try:
            concepts_df = loader.load_master_concepts()
            skill_mapping = loader.load_skill_master_concept_mapping()
            
            if search_concept:
                # Find matching concepts
                matches = concepts_df[concepts_df['MASTER_CONCEPT_NAME'].str.contains(search_concept, case=False, na=False)]
                
                if not matches.empty:
                    st.markdown(f"**Found {len(matches)} matching concepts:**")
                    
                    for _, concept_row in matches.iterrows():
                        with st.expander(f"📘 {concept_row['MASTER_CONCEPT_NAME']}"):
                            # Concept details
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"**Description:** {concept_row.get('DESCRIPTION', 'N/A')}")
                                st.markdown(f"**Taxonomy Location:**")
                                st.markdown(f"- Strand: {concept_row.get('SOR_STRAND', 'N/A')}")
                                st.markdown(f"- Pillar: {concept_row.get('SOR_PILLAR', 'N/A')}")
                                st.markdown(f"- Domain: {concept_row.get('SOR_DOMAIN', 'N/A')}")
                            
                            with col2:
                                # Count skills
                                concept_skills = skill_mapping[
                                    skill_mapping['MASTER_CONCEPT_NAME'] == concept_row['MASTER_CONCEPT_NAME']
                                ]
                                st.metric("Mapped ROCK Skills", len(concept_skills))
                            
                            # Show mapped skills
                            if not concept_skills.empty:
                                st.markdown("**Mapped ROCK Skills:**")
                                st.dataframe(concept_skills[['SKILL_NAME', 'EDUCATION_AUTHORITY', 'GRADE_LEVEL_NAME']].head(20),
                                           use_container_width=True, hide_index=True)
                else:
                    st.warning("No concepts found matching your search.")
            
            else:
                # Show popular concepts
                st.markdown("**Popular Concepts:**")
                concept_counts = skill_mapping['MASTER_CONCEPT_NAME'].value_counts().head(15)
                popular_df = pd.DataFrame({
                    'Concept': concept_counts.index,
                    'Skill Count': concept_counts.values
                })
                st.dataframe(popular_df, use_container_width=True, hide_index=True)
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    # ========================================================================
    # EXPLORER B: SKILL SEARCH & INSPECTOR (Enhanced with Taxonomy Filtering)
    # ========================================================================
    elif explorer_tab == "🎯 Skill Search & Inspector":
        st.markdown("### Taxonomy-Powered Skill Discovery")
        st.markdown("Use multi-dimensional filtering to find exactly the skills you need.")
        
        # Show before/after comparison
        with st.expander("💡 Why Taxonomy-Powered Discovery?"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**❌ Traditional Text Search**")
                st.markdown("""
                - Returns 100s of irrelevant results
                - No grade-level precision
                - Misses alternative terminology
                - Requires manual filtering
                - Time-consuming and imprecise
                """)
            
            with col2:
                st.markdown("**✅ Taxonomy-Powered Discovery**")
                st.markdown("""
                - Filter by taxonomy hierarchy
                - Precise grade-level targeting
                - Filter by cognitive demand
                - Filter by text type & complexity
                - Instant, precise results
                """)
        
        # Multi-dimensional filters
        st.markdown("### 🔍 Apply Filters")
        
        try:
            specifications = loader.load_skill_specifications()
            skill_mapping = loader.load_skill_master_concept_mapping()
            
            # Use specifications if available, otherwise fall back to skill_mapping
            if not specifications.empty:
                filter_source = specifications
                st.success(f"✅ Filtering {len(specifications):,} skills with full specifications")
            elif not skill_mapping.empty:
                filter_source = skill_mapping
                st.info(f"ℹ️ Filtering {len(skill_mapping):,} skills (limited metadata)")
            else:
                filter_source = pd.DataFrame()
                st.warning("⚠️ No skill data available")
            
            if not filter_source.empty:
                # Row 1: Text search + Taxonomy
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    skill_search = st.text_input("🔎 Search by skill name:", placeholder="Enter keywords...")
                
                with col2:
                    if 'SOR_STRAND' in filter_source.columns:
                        strands = ['All'] + sorted([s for s in filter_source['SOR_STRAND'].dropna().unique() if pd.notna(s)])
                        strand_filter = st.selectbox("Taxonomy Strand:", options=strands)
                    else:
                        strand_filter = 'All'
                
                with col3:
                    if 'SOR_PILLAR' in filter_source.columns:
                        pillars = ['All'] + sorted([p for p in filter_source['SOR_PILLAR'].dropna().unique() if pd.notna(p)])
                        pillar_filter = st.selectbox("Taxonomy Pillar:", options=pillars)
                    else:
                        pillar_filter = 'All'
                
                # Row 2: Specifications (if available)
                if 'text_type' in filter_source.columns or 'cognitive_demand' in filter_source.columns:
                    st.markdown("**Specification Filters:**")
                    col4, col5, col6, col7 = st.columns(4)
                    
                    with col4:
                        if 'text_type' in filter_source.columns:
                            text_types = ['All'] + sorted([t for t in filter_source['text_type'].dropna().unique() if pd.notna(t)])
                            text_type_filter = st.selectbox("Text Type:", options=text_types)
                        else:
                            text_type_filter = 'All'
                    
                    with col5:
                        if 'cognitive_demand' in filter_source.columns:
                            cognitive_levels = ['All'] + sorted([c for c in filter_source['cognitive_demand'].dropna().unique() if pd.notna(c)])
                            cognitive_filter = st.selectbox("Cognitive Demand:", options=cognitive_levels)
                        else:
                            cognitive_filter = 'All'
                    
                    with col6:
                        if 'task_complexity' in filter_source.columns:
                            complexities = ['All'] + sorted([c for c in filter_source['task_complexity'].dropna().unique() if pd.notna(c)])
                            complexity_filter = st.selectbox("Task Complexity:", options=complexities)
                        else:
                            complexity_filter = 'All'
                    
                    with col7:
                        if 'complexity_band' in filter_source.columns:
                            grade_bands = ['All'] + sorted([g for g in filter_source['complexity_band'].dropna().unique() if pd.notna(g)])
                            grade_band_filter = st.selectbox("Grade Band:", options=grade_bands)
                        else:
                            grade_band_filter = 'All'
                else:
                    text_type_filter = 'All'
                    cognitive_filter = 'All'
                    complexity_filter = 'All'
                    grade_band_filter = 'All'
                
                # Row 3: Traditional filters
                st.markdown("**Additional Filters:**")
                col8, col9 = st.columns(2)
                
                with col8:
                    if 'EDUCATION_AUTHORITY' in filter_source.columns:
                        states = ['All'] + sorted([s for s in filter_source['EDUCATION_AUTHORITY'].dropna().unique() if pd.notna(s)])
                        state_filter = st.selectbox("State/Authority:", options=states)
                    else:
                        state_filter = 'All'
                
                with col9:
                    if 'GRADE_LEVEL_NAME' in filter_source.columns:
                        grades = ['All'] + natural_sort([g for g in filter_source['GRADE_LEVEL_NAME'].dropna().unique() if pd.notna(g)])
                        grade_filter = st.selectbox("Specific Grade:", options=grades)
                    else:
                        grade_filter = 'All'
                
                # Apply all filters
                filtered_skills = filter_source.copy()
                
                if skill_search:
                    filtered_skills = filtered_skills[
                        filtered_skills['SKILL_NAME'].str.contains(skill_search, case=False, na=False)
                    ]
                
                if strand_filter != 'All' and 'SOR_STRAND' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['SOR_STRAND'] == strand_filter]
                
                if pillar_filter != 'All' and 'SOR_PILLAR' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['SOR_PILLAR'] == pillar_filter]
                
                if text_type_filter != 'All' and 'text_type' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['text_type'] == text_type_filter]
                
                if cognitive_filter != 'All' and 'cognitive_demand' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['cognitive_demand'] == cognitive_filter]
                
                if complexity_filter != 'All' and 'task_complexity' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['task_complexity'] == complexity_filter]
                
                if grade_band_filter != 'All' and 'complexity_band' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['complexity_band'] == grade_band_filter]
                
                if state_filter != 'All' and 'EDUCATION_AUTHORITY' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['EDUCATION_AUTHORITY'] == state_filter]
                
                if grade_filter != 'All' and 'GRADE_LEVEL_NAME' in filtered_skills.columns:
                    filtered_skills = filtered_skills[filtered_skills['GRADE_LEVEL_NAME'] == grade_filter]
                
                # Display results
                st.markdown("---")
                st.markdown(f"### 📊 Results: {len(filtered_skills):,} skills found")
                
                if len(filtered_skills) > 0:
                    # Show efficiency metrics
                    original_count = len(filter_source)
                    filtered_count = len(filtered_skills)
                    precision = (filtered_count / original_count * 100) if original_count > 0 else 0
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Filtered Results", f"{filtered_count:,}")
                    with metric_col2:
                        st.metric("From Total", f"{original_count:,}")
                    with metric_col3:
                        reduction = 100 - precision
                        st.metric("Noise Reduction", f"{reduction:.1f}%")
                    
                    # Display filtered skills
                    display_cols = ['SKILL_NAME']
                    optional_cols = ['GRADE_LEVEL_SHORT_NAME', 'cognitive_demand', 'text_type', 
                                   'task_complexity', 'SOR_STRAND', 'SOR_PILLAR', 'EDUCATION_AUTHORITY']
                    
                    for col in optional_cols:
                        if col in filtered_skills.columns:
                            display_cols.append(col)
                    
                    st.dataframe(filtered_skills[display_cols].head(100), use_container_width=True, hide_index=True)
                    
                    # Export option
                    csv = filtered_skills.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Results CSV",
                                     data=csv,
                                     file_name="taxonomy_filtered_skills.csv",
                                     mime="text/csv")
                else:
                    st.info("🔍 No skills match your filter criteria. Try adjusting your filters.")
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    # ========================================================================
    # EXPLORER C: TAXONOMY NAVIGATOR
    # ========================================================================
    elif explorer_tab == "🌳 Taxonomy Navigator":
        st.markdown("### Science of Reading Taxonomy Navigator")
        st.markdown("Navigate the 6-level hierarchy of the Science of Reading framework.")
        
        try:
            taxonomy_path = Path(__file__).parent.parent / 'POC_science_of_reading_literacy_skills_taxonomy.csv'
            
            if taxonomy_path.exists():
                taxonomy_df = pd.read_csv(taxonomy_path)
                
                # Hierarchical navigation
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    selected_strand = st.selectbox("Select Strand:", 
                                                  options=sorted(taxonomy_df['Strand'].dropna().unique().tolist()))
                
                if selected_strand:
                    strand_data = taxonomy_df[taxonomy_df['Strand'] == selected_strand]
                    
                    with col2:
                        pillars = sorted(strand_data['Pillar'].dropna().unique().tolist())
                        selected_pillar = st.selectbox("Select Pillar:", options=['All'] + pillars)
                    
                    if selected_pillar != 'All':
                        pillar_data = strand_data[strand_data['Pillar'] == selected_pillar]
                        
                        with col3:
                            domains = sorted(pillar_data['Domain'].dropna().unique().tolist())
                            selected_domain = st.selectbox("Select Domain:", options=['All'] + domains)
                        
                        if selected_domain != 'All':
                            domain_data = pillar_data[pillar_data['Domain'] == selected_domain]
                            
                            # Show skill areas in this domain
                            skill_areas = domain_data['Skill Area'].dropna().unique()
                            st.markdown(f"**Skill Areas ({len(skill_areas)}):** {', '.join(sorted(skill_areas))}")
                            
                            # Show detailed view
                            with st.expander("📋 View all taxonomy entries"):
                                st.dataframe(domain_data, use_container_width=True, hide_index=True)
                    
                    else:
                        # Show all pillars in strand
                        pillar_counts = strand_data.groupby('Pillar').size().reset_index(name='Entry Count')
                        st.dataframe(pillar_counts, use_container_width=True, hide_index=True)
            
            else:
                st.warning("Taxonomy file not found")
        
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================================================
# PAGE 4: VALIDATION DASHBOARD
# ============================================================================

elif page == "📊 Validation Dashboard":
    st.markdown('<div class="main-header">Validation Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Quality metrics and validation suite integration</div>', unsafe_allow_html=True)
    
    validation_results = load_validation_results()
    
    if validation_results is None:
        st.warning("""
        ⚠️ **Validation results not found.**
        
        The validation suite has not been run yet, or results are not in the expected location.
        
        **To generate validation results:**
        
        1. Navigate to the frameworks directory:
        ```
        cd rock-skills/frameworks
        ```
        
        2. Run the full validation suite:
        ```
        python3 run_full_validation.py
        ```
        
        3. Results will be saved to `validation_outputs/`
        
        4. Refresh this page to view results
        """)
        
        if st.button("📖 View Validation Suite Documentation"):
            st.info("See `rock-skills/frameworks/VALIDATION_SUITE_README.md` for detailed instructions")
    
    else:
        # Master validation report
        if 'master_report' in validation_results:
            st.markdown("### 📋 Master Validation Report")
            st.markdown(validation_results['master_report'])
        
        st.markdown("---")
        
        # Create tabs for different validation aspects
        val_tab1, val_tab2, val_tab3 = st.tabs([
            "🔍 Semantic Validation",
            "🌐 Framework Convergence",
            "📊 Summary Metrics"
        ])
        
        with val_tab1:
            st.markdown("### Semantic Similarity Validation")
            
            if 'duplicates' in validation_results:
                duplicates_df = validation_results['duplicates']
                
                # Key metrics
                col1, col2, col3 = st.columns(3)
                
                high_pri = len(duplicates_df[duplicates_df['similarity'] >= 0.90])
                med_pri = len(duplicates_df[(duplicates_df['similarity'] >= 0.85) & (duplicates_df['similarity'] < 0.90)])
                
                with col1:
                    st.metric("Total Pairs Analyzed", len(duplicates_df))
                with col2:
                    st.metric("High-Priority (>0.90)", high_pri,
                             delta="Critical" if high_pri > 50 else "Good",
                             delta_color="inverse" if high_pri > 50 else "normal")
                with col3:
                    st.metric("Medium-Priority (0.85-0.90)", med_pri)
                
                # Top duplicates
                st.markdown("#### Top 20 Most Similar Pairs")
                top_dups = duplicates_df.nlargest(20, 'similarity')
                st.dataframe(top_dups[['concept1_name', 'concept2_name', 'similarity', 'same_level', 'same_strand']],
                           use_container_width=True, hide_index=True)
                
                # Download options
                csv = duplicates_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download All Duplicates CSV",
                                 data=csv,
                                 file_name="potential_duplicates.csv",
                                 mime="text/csv")
            
            # Link to full report
            if 'semantic_report' in validation_results:
                with st.expander("📄 View Full Semantic Validation Report"):
                    st.markdown(validation_results['semantic_report'])
        
        with val_tab2:
            st.markdown("### Framework Convergence Analysis")
            
            if 'concept_confidence' in validation_results:
                confidence_df = validation_results['concept_confidence']
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                strong = len(confidence_df[confidence_df['Evidence_Strength'] == 'strong'])
                moderate = len(confidence_df[confidence_df['Evidence_Strength'] == 'moderate'])
                weak = len(confidence_df[confidence_df['Evidence_Strength'] == 'weak'])
                unvalidated = len(confidence_df[confidence_df['Evidence_Strength'] == 'unvalidated'])
                
                total = len(confidence_df)
                validated_pct = ((total - unvalidated) / total * 100) if total > 0 else 0
                
                with col1:
                    st.metric("Total Concepts", total)
                with col2:
                    st.metric("Validated %", f"{validated_pct:.1f}%")
                with col3:
                    st.metric("Strong Evidence", strong)
                with col4:
                    st.metric("Unvalidated", unvalidated)
                
                # Distribution chart
                evidence_counts = confidence_df['Evidence_Strength'].value_counts()
                fig = px.bar(x=evidence_counts.index, y=evidence_counts.values,
                           title="Evidence Strength Distribution",
                           labels={'x': 'Evidence Strength', 'y': 'Number of Concepts'},
                           color=evidence_counts.index,
                           color_discrete_map={
                               'strong': '#2ca02c',
                               'moderate': '#ff7f0e',
                               'weak': '#ffcc00',
                               'unvalidated': '#d62728'
                           })
                st.plotly_chart(fig, use_container_width=True)
                
                # Top validated concepts
                st.markdown("#### Top Validated Concepts")
                top_validated = confidence_df[confidence_df['Convergence_Score'] > 0].nlargest(15, 'Convergence_Score')
                st.dataframe(top_validated[['Concept_Name', 'Convergence_Score', 'Frameworks', 'Evidence_Strength']],
                           use_container_width=True, hide_index=True)
            
            # Link to full report
            if 'convergence_report' in validation_results:
                with st.expander("📄 View Full Convergence Report"):
                    st.markdown(validation_results['convergence_report'])
        
        with val_tab3:
            st.markdown("### Summary Metrics & Recommendations")
            
            if 'recommendations' in validation_results:
                rec_df = validation_results['recommendations']
                
                # Priority breakdown
                st.markdown("#### Prioritized Action Items")
                
                priority_counts = rec_df['Priority'].value_counts().sort_index()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Priority 1 (Critical)", priority_counts.get(1, 0))
                with col2:
                    st.metric("Priority 2 (Important)", priority_counts.get(2, 0))
                with col3:
                    st.metric("Priority 3 (Nice-to-have)", priority_counts.get(3, 0))
                
                # Show recommendations
                st.markdown("#### Top Recommendations")
                st.dataframe(rec_df.head(20), use_container_width=True, hide_index=True)
                
                # Export
                csv = rec_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download All Recommendations",
                                 data=csv,
                                 file_name="recommendations_priority.csv",
                                 mime="text/csv")

# ============================================================================
# PAGE 5: TECHNICAL REFERENCE
# ============================================================================

elif page == "🔧 Technical Reference":
    st.markdown('<div class="main-header">Technical Reference</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Implementation details, schemas, and documentation for developers</div>', unsafe_allow_html=True)
    
    # Sub-sections
    ref_section = st.selectbox(
        "Select Documentation Section:",
        ["Overview", "Schema Reference", "Script Reference", "Validation Suite", "API Examples", "Contributing"]
    )
    
    if ref_section == "Overview":
        st.markdown("""
        ## System Overview
        
        The Skills Bridge Explorer is built on a three-level architecture that connects ROCK skills 
        to Science of Reading taxonomy while maintaining data integrity and enabling cross-state discovery.
        
        ### Architecture Components
        
        **Data Layer:**
        - ROCK Schemas (skills, standards, standard-skills, etc.)
        - Science of Reading Taxonomy CSV (1,139 rows, 6-level hierarchy)
        - Master Concepts CSV (bridge layer connecting ROCK to SoR)
        - Skill-Concept Mappings CSV
        
        **Analysis Layer:**
        - Semantic similarity analysis (sentence-transformers)
        - Framework convergence tracking
        - Redundancy detection and variant classification
        - MECE quality validation
        
        **Presentation Layer:**
        - Streamlit web application (this app)
        - Interactive visualizations (plotly)
        - Export capabilities (CSV, reports)
        
        ### Technology Stack
        
        - **Python 3.9+**
        - **Streamlit** - Web framework
        - **Pandas** - Data manipulation
        - **Plotly** - Visualizations
        - **sentence-transformers** - Semantic similarity
        - **scikit-learn** - ML utilities
        - **spaCy** (optional) - NLP processing
        
        ### File Structure
        
        ```
        rock-skills/
        ├── poc/                    # This Streamlit app
        │   ├── skill_bridge_app.py
        │   ├── data_loader.py
        │   └── pages/
        ├── rock_data/              # ROCK data files
        ├── analysis/               # Analysis scripts & outputs
        │   ├── master-concepts.csv
        │   ├── skill_master_concept_mapping.csv
        │   └── scripts/
        ├── frameworks/             # Framework processing & validation
        │   ├── validation_outputs/
        │   └── input/
        ├── docs/                   # Documentation
        └── POC_science_of_reading_literacy_skills_taxonomy.csv
        ```
        """)
    
    elif ref_section == "Schema Reference":
        st.markdown("""
        ## Data Schema Reference
        
        ### ROCK Schemas
        
        **skills.csv:**
        - SKILL_ID (PK)
        - SKILL_NAME
        - SKILL_AREA_NAME
        - CONTENT_AREA_NAME
        - GRADE_LEVEL_NAME
        - DOK_LEVEL
        
        **standard_skills.csv:**
        - SKILL_ID → STANDARD_ID
        - EDUCATION_AUTHORITY (TX, CA, CCSS, etc.)
        - STANDARD_SET_NAME
        
        ### Bridge Layer (Generated)
        
        **master-concepts.csv:**
        - MASTER_CONCEPT_ID (PK)
        - MASTER_CONCEPT_NAME
        - DESCRIPTION
        - SOR_STRAND, SOR_PILLAR, SOR_DOMAIN
        - COMPLEXITY_BAND
        - GRADE_RANGE
        
        **skill_master_concept_mapping.csv:**
        - SKILL_ID → MASTER_CONCEPT_ID
        - SKILL_NAME
        - MASTER_CONCEPT_NAME
        - Plus all metadata fields
        
        ### Science of Reading Taxonomy
        
        **POC_science_of_reading_literacy_skills_taxonomy.csv:**
        - Strand (Level 1)
        - Pillar (Level 2)
        - Domain (Level 3)
        - Skill Area (Level 4)
        - Skill Set (Level 5)
        - Skill Subset (Level 6)
        - Skill Subset Annotation
        """)
    
    elif ref_section == "Script Reference":
        st.markdown("""
        ## Key Scripts & Commands
        
        ### Data Pipeline
        
        **Generate Master Concepts:**
        ```bash
        cd analysis/scripts
        python3 generate_master_concepts.py
        ```
        
        **Map Skills to Concepts:**
        ```bash
        python3 batch_map_skills_enhanced.py --content-area "English Language Arts"
        ```
        
        ### Validation Suite
        
        **Run Full Validation:**
        ```bash
        cd frameworks
        python3 run_full_validation.py
        ```
        
        **Run Individual Validators:**
        ```bash
        python3 semantic_validator.py --threshold 0.85
        python3 framework_tracker.py
        python3 semantic_similarity_heatmap.py
        ```
        
        ### Framework Processing
        
        **Process New Framework PDF:**
        ```bash
        cd frameworks
        python3 process_framework_pdfs.py \\
            --input input/ela/framework.pdf \\
            --subject ela \\
            --mode full \\
            --output output/framework_analysis
        ```
        
        ### Running the App
        
        **Start Streamlit:**
        ```bash
        cd poc
        streamlit run skill_bridge_app.py
        ```
        """)
    
    elif ref_section == "Validation Suite":
        st.markdown("""
        ## Validation Suite Documentation
        
        The validation suite provides automated quality assurance for the taxonomy.
        
        ### Components
        
        **1. Semantic Similarity Validator**
        - Detects duplicate or highly similar concepts
        - Uses sentence-transformers (all-MiniLM-L6-v2)
        - Generates similarity matrix for all concept pairs
        - Flags high-similarity pairs (>0.85, >0.90)
        
        **2. Framework Convergence Tracker**
        - Tracks which concepts appear in multiple frameworks
        - Calculates convergence scores
        - Classifies evidence strength (strong/moderate/weak/unvalidated)
        
        **3. MECE Quality Validator** (planned)
        - Mutual Exclusivity: Checks for overlaps
        - Collective Exhaustiveness: Checks for gaps
        
        ### Usage
        
        See `frameworks/VALIDATION_SUITE_README.md` for detailed documentation.
        
        **Quick Start:**
        ```bash
        cd frameworks
        python3 run_full_validation.py
        ```
        
        **Outputs:**
        - validation_master_report.md
        - semantic_validation_report.md
        - framework_convergence_summary.md
        - potential_duplicates.csv
        - concept_confidence.csv
        - recommendations_priority.csv
        - visualizations/
        """)
    
    elif ref_section == "API Examples":
        st.markdown("""
        ## API Examples & Code Snippets
        
        ### Loading Data
        
        ```python
        from data_loader import ROCKDataLoader
        from pathlib import Path
        
        # Initialize loader
        base_dir = Path.cwd().parent
        loader = ROCKDataLoader(
            schema_dir=base_dir / 'rock_data',
            analysis_dir=base_dir / 'analysis'
        )
        
        # Load data
        concepts_df = loader.load_master_concepts()
        skill_mapping = loader.load_skill_master_concept_mapping()
        variants_df = loader.load_variant_classification()
        ```
        
        ### Searching Concepts
        
        ```python
        # Find concept by name
        concept = concepts_df[
            concepts_df['MASTER_CONCEPT_NAME'].str.contains('phoneme', case=False)
        ]
        
        # Get all skills for a concept
        concept_skills = skill_mapping[
            skill_mapping['MASTER_CONCEPT_NAME'] == 'Phoneme Blending'
        ]
        
        # Group by state
        by_state = concept_skills.groupby('EDUCATION_AUTHORITY').size()
        ```
        
        ### Semantic Similarity
        
        ```python
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings
        texts = concepts_df['MASTER_CONCEPT_NAME'].tolist()
        embeddings = model.encode(texts)
        
        # Calculate similarity
        similarity_matrix = cosine_similarity(embeddings)
        ```
        """)
    
    elif ref_section == "Contributing":
        st.markdown("""
        ## Contributing to the Project
        
        ### Development Workflow
        
        1. **Clone Repository**
        2. **Install Dependencies:**
           ```bash
           pip install -r requirements.txt
           ```
        3. **Make Changes**
        4. **Test Locally:**
           ```bash
           streamlit run skill_bridge_app.py
           ```
        5. **Submit Pull Request**
        
        ### Coding Standards
        
        - Follow PEP 8 style guide
        - Use type hints where appropriate
        - Add docstrings to functions
        - Comment complex logic
        - Keep functions focused and small
        
        ### Adding New Features
        
        **New Page/View:**
        1. Add to navigation radio buttons
        2. Create new `elif page == "..."` block
        3. Implement view logic
        4. Update documentation
        
        **New Data Source:**
        1. Update `data_loader.py`
        2. Add caching with `@st.cache_data`
        3. Handle errors gracefully
        4. Document schema
        
        **New Validation:**
        1. Create script in `frameworks/`
        2. Follow validation suite patterns
        3. Output to `validation_outputs/`
        4. Update dashboard integration
        
        ### Contact
        
        For questions or suggestions, contact the ROCK Skills Analysis Team.
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <strong>ROCK Skills Bridge Explorer v2.0</strong><br>
    Renaissance Learning AI Hackathon 2025<br>
    <em>Narrative-Driven Taxonomy Analysis</em>
</div>
""", unsafe_allow_html=True)

