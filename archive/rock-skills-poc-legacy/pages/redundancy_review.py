"""
Redundancy Review Interface

Interactive Streamlit page for reviewing and making decisions on
skill relationships and redundancies.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis.redundancy.relationship_classifier import RelationshipType


def load_latest_results(output_dir: Path) -> tuple:
    """Load the most recent analysis results."""
    relationships_dir = output_dir / "relationships"
    
    if not relationships_dir.exists():
        return None, None, None
    
    # Find most recent files
    rel_files = sorted(relationships_dir.glob("relationships_*.json"), reverse=True)
    rec_files = sorted(relationships_dir.glob("recommendations_*.json"), reverse=True)
    sum_files = sorted(relationships_dir.glob("summary_*.csv"), reverse=True)
    
    if not rel_files or not rec_files or not sum_files:
        return None, None, None
    
    # Load data
    with open(rel_files[0], 'r') as f:
        relationships = json.load(f)
    
    with open(rec_files[0], 'r') as f:
        recommendations = json.load(f)
    
    summary_df = pd.read_csv(sum_files[0])
    
    return relationships, recommendations, summary_df


def display_relationship_card(idx: int, rel: Dict, rec: Dict, metadata: Dict):
    """Display a relationship as an interactive card."""
    
    # Determine color based on priority
    priority_colors = {
        'P0': '🔴',
        'P1': '🟠',
        'P2': '🟡',
        'P3': '🟢'
    }
    priority_icon = priority_colors.get(rec['priority'], '⚪')
    
    # Create card
    with st.container():
        st.markdown(f"### {priority_icon} Relationship #{idx + 1} - {rec['priority']} Priority")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**Type:** {rel['relationship_type']}")
            st.markdown(f"**Confidence:** {rel['confidence']:.1%}")
        
        with col2:
            st.markdown(f"**Action:** {rec['action']}")
            st.markdown(f"**Priority Score:** {rec['priority_score']:.3f}")
        
        with col3:
            composite = rel['similarity_scores']['composite']
            st.metric("Composite Score", f"{composite:.3f}")
        
        # Skill comparison
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Skill A**")
            st.markdown(f"*{rel['skill_a_id']}*")
            st.markdown(f"> {rel['skill_a_name']}")
            
            if 'skill_a' in rel['metadata']:
                meta_a = rel['metadata']['skill_a']
                st.caption(f"Grade: {meta_a.get('grade', 'N/A')} | "
                          f"Cognitive: {meta_a.get('cognitive_demand', 'N/A')}")
        
        with col_b:
            st.markdown("**Skill B**")
            st.markdown(f"*{rel['skill_b_id']}*")
            st.markdown(f"> {rel['skill_b_name']}")
            
            if 'skill_b' in rel['metadata']:
                meta_b = rel['metadata']['skill_b']
                st.caption(f"Grade: {meta_b.get('grade', 'N/A')} | "
                          f"Cognitive: {meta_b.get('cognitive_demand', 'N/A')}")
        
        # Recommendation
        with st.expander("📋 Recommendation & Rationale"):
            st.markdown(f"**Rationale:** {rec['rationale']}")
            
            st.markdown("**Recommended Steps:**")
            for i, step in enumerate(rec['specific_steps'], 1):
                st.markdown(f"{i}. {step}")
            
            if rec.get('suggested_base_skill_name'):
                st.info(f"💡 Suggested Base Skill: **{rec['suggested_base_skill_name']}**")
        
        # Similarity breakdown
        with st.expander("📊 Similarity Breakdown"):
            scores = rel['similarity_scores']
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Structural", f"{scores['structural']:.3f}")
            col2.metric("Educational", f"{scores['educational']:.3f}")
            col3.metric("Semantic", f"{scores['semantic']:.3f}")
            col4.metric("Contextual", f"{scores['contextual']:.3f}")
            
            # Evidence
            if 'evidence' in rel['similarity_explanation']:
                st.markdown("**Key Evidence:**")
                for evidence in rel['similarity_explanation']['evidence']:
                    st.markdown(f"- {evidence}")
        
        # Decision buttons
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("✅ Merge", key=f"merge_{idx}"):
                record_decision(idx, rel['relationship_id'], "MERGE", "")
                st.success("Decision recorded: MERGE")
        
        with col2:
            if st.button("❌ Keep Separate", key=f"separate_{idx}"):
                record_decision(idx, rel['relationship_id'], "KEEP_SEPARATE", "")
                st.success("Decision recorded: KEEP SEPARATE")
        
        with col3:
            if st.button("🔄 Create Spec", key=f"spec_{idx}"):
                record_decision(idx, rel['relationship_id'], "CREATE_SPECIFICATION", "")
                st.success("Decision recorded: CREATE SPECIFICATION")
        
        with col4:
            if st.button("🚩 Flag for Review", key=f"flag_{idx}"):
                record_decision(idx, rel['relationship_id'], "FLAG", "")
                st.warning("Flagged for review")
        
        with col5:
            if st.button("ℹ️ More Info", key=f"info_{idx}"):
                st.session_state[f'show_detail_{idx}'] = True
        
        # Detailed view
        if st.session_state.get(f'show_detail_{idx}', False):
            with st.expander("🔍 Detailed Comparison (Expanded)", expanded=True):
                display_detailed_comparison(rel, metadata)
        
        st.markdown("---")


def display_detailed_comparison(rel: Dict, metadata: Dict):
    """Display detailed side-by-side comparison."""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Skill A Details")
        st.json(rel['similarity_explanation'].get('components', {}))
    
    with col_b:
        st.markdown("#### Skill B Details")
        # Would show skill B details from metadata
        st.info("Full metadata comparison coming soon")


def record_decision(idx: int, rel_id: str, decision: str, rationale: str):
    """Record user decision to decision log."""
    
    decision_log_path = Path(__file__).parent.parent.parent / "analysis" / "redundancy" / "outputs" / "decisions" / "decision_log.json"
    decision_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing log
    if decision_log_path.exists():
        with open(decision_log_path, 'r') as f:
            log = json.load(f)
    else:
        log = []
    
    # Add new decision
    log.append({
        'timestamp': datetime.now().isoformat(),
        'relationship_id': rel_id,
        'decision': decision,
        'rationale': rationale,
        'user': 'current_user'  # Would get from session
    })
    
    # Save
    with open(decision_log_path, 'w') as f:
        json.dump(log, f, indent=2)


def main():
    st.set_page_config(
        page_title="Skill Redundancy Review",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Skill Redundancy Review Dashboard")
    st.markdown("Review and make decisions on skill relationships and redundancies")
    
    # Load data
    output_dir = Path(__file__).parent.parent.parent / "analysis" / "redundancy" / "outputs"
    relationships, recommendations, summary_df = load_latest_results(output_dir)
    
    if relationships is None:
        st.warning("No analysis results found. Please run the redundancy analyzer first.")
        st.markdown("""
        To generate results:
        ```bash
        cd analysis/redundancy
        python redundancy_analyzer.py --metadata path/to/metadata.csv --output outputs/relationships
        ```
        """)
        return
    
    # Statistics overview
    st.markdown("## 📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Relationships", len(relationships))
    
    with col2:
        p0_count = len([r for r in recommendations if r['priority'] == 'P0'])
        st.metric("P0 (Critical)", p0_count)
    
    with col3:
        p1_count = len([r for r in recommendations if r['priority'] == 'P1'])
        st.metric("P1 (High)", p1_count)
    
    with col4:
        avg_confidence = sum(r['confidence'] for r in relationships) / len(relationships)
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    # Progress tracking
    decision_log_path = output_dir / "decisions" / "decision_log.json"
    reviewed_count = 0
    if decision_log_path.exists():
        with open(decision_log_path, 'r') as f:
            log = json.load(f)
            reviewed_count = len(set(d['relationship_id'] for d in log))
    
    progress = reviewed_count / len(relationships) if relationships else 0
    st.progress(progress)
    st.caption(f"Progress: {reviewed_count}/{len(relationships)} reviewed ({progress:.1%})")
    
    # Filters
    st.markdown("## 🔧 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        relationship_types = ['All'] + sorted(set(r['relationship_type'] for r in relationships))
        selected_type = st.selectbox("Relationship Type", relationship_types)
    
    with col2:
        priorities = ['All', 'P0', 'P1', 'P2', 'P3']
        selected_priority = st.selectbox("Priority", priorities)
    
    with col3:
        sort_options = ['Priority (High to Low)', 'Confidence (High to Low)', 'Composite Score (High to Low)']
        sort_by = st.selectbox("Sort By", sort_options)
    
    with col4:
        show_options = ['Unreviewed', 'All', 'Reviewed']
        show_filter = st.selectbox("Show", show_options)
    
    # Apply filters
    filtered_relationships = relationships
    filtered_recommendations = recommendations
    
    if selected_type != 'All':
        filtered_relationships = [r for r in relationships if r['relationship_type'] == selected_type]
        filtered_recommendations = [rec for rec in recommendations if 
                                   rec['relationship_id'] in [r['relationship_id'] for r in filtered_relationships]]
    
    if selected_priority != 'All':
        filtered_recommendations = [r for r in filtered_recommendations if r['priority'] == selected_priority]
        filtered_relationships = [rel for rel in filtered_relationships if 
                                 rel['relationship_id'] in [r['relationship_id'] for r in filtered_recommendations]]
    
    # Sort - keep both lists in sync
    if sort_by == 'Priority (High to Low)':
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        # Create combined list for sorting
        rel_dict = {r['relationship_id']: r for r in filtered_relationships}
        filtered_recommendations.sort(key=lambda r: priority_order.get(r['priority'], 99))
        # Reorder relationships to match
        filtered_relationships = [rel_dict[rec['relationship_id']] for rec in filtered_recommendations if rec['relationship_id'] in rel_dict]
    elif sort_by == 'Confidence (High to Low)':
        # Create combined list for sorting
        rec_dict = {r['relationship_id']: r for r in filtered_recommendations}
        filtered_relationships.sort(key=lambda r: r['confidence'], reverse=True)
        # Reorder recommendations to match
        filtered_recommendations = [rec_dict[rel['relationship_id']] for rel in filtered_relationships if rel['relationship_id'] in rec_dict]
    elif sort_by == 'Composite Score (High to Low)':
        # Create combined list for sorting
        rec_dict = {r['relationship_id']: r for r in filtered_recommendations}
        filtered_relationships.sort(key=lambda r: r['similarity_scores']['composite'], reverse=True)
        # Reorder recommendations to match
        filtered_recommendations = [rec_dict[rel['relationship_id']] for rel in filtered_relationships if rel['relationship_id'] in rec_dict]
    
    # Reviewed filter
    if show_filter == 'Unreviewed' and decision_log_path.exists():
        with open(decision_log_path, 'r') as f:
            log = json.load(f)
            reviewed_ids = set(d['relationship_id'] for d in log)
        filtered_relationships = [r for r in filtered_relationships if r['relationship_id'] not in reviewed_ids]
        filtered_recommendations = [rec for rec in filtered_recommendations if rec['relationship_id'] not in reviewed_ids]
    elif show_filter == 'Reviewed' and decision_log_path.exists():
        with open(decision_log_path, 'r') as f:
            log = json.load(f)
            reviewed_ids = set(d['relationship_id'] for d in log)
        filtered_relationships = [r for r in filtered_relationships if r['relationship_id'] in reviewed_ids]
        filtered_recommendations = [rec for rec in filtered_recommendations if rec['relationship_id'] in reviewed_ids]
    
    # Display relationships
    st.markdown(f"## 📋 Relationships ({len(filtered_relationships)})")
    
    if not filtered_relationships:
        st.info("No relationships match the current filters.")
        return
    
    # Pagination
    items_per_page = st.slider("Items per page", 5, 50, 10)
    total_pages = (len(filtered_relationships) + items_per_page - 1) // items_per_page
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀ Previous") and st.session_state.current_page > 0:
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<center>Page {st.session_state.current_page + 1} of {total_pages}</center>", 
                   unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ▶") and st.session_state.current_page < total_pages - 1:
            st.session_state.current_page += 1
            st.rerun()
    
    # Display current page
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_relationships))
    
    for i in range(start_idx, end_idx):
        rel = filtered_relationships[i]
        # Find matching recommendation
        matching_recs = [r for r in filtered_recommendations if r['relationship_id'] == rel['relationship_id']]
        if not matching_recs:
            # Skip this relationship if no matching recommendation found
            st.warning(f"⚠️ No recommendation found for relationship {rel['relationship_id']}")
            continue
        rec = matching_recs[0]
        display_relationship_card(i, rel, rec, {})
    
    # Export options
    st.markdown("## 💾 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Filtered to CSV"):
            filtered_df = pd.DataFrame([{
                'relationship_id': r['relationship_id'],
                'skill_a_id': r['skill_a_id'],
                'skill_b_id': r['skill_b_id'],
                'relationship_type': r['relationship_type'],
                'confidence': r['confidence'],
                'composite_score': r['similarity_scores']['composite']
            } for r in filtered_relationships])
            
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "filtered_relationships.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📊 Generate Report"):
            st.info("Report generation coming soon!")
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()


if __name__ == "__main__":
    main()

