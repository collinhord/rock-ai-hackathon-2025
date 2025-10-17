"""
Redundancy Grooming & Conflict Resolution Page

Interactive interface for reviewing and resolving:
- Base skill ambiguities/conflicts
- ROCK skill redundancies
- LLM-flagged issues

Users can:
- View flagged conflicts with LLM analysis
- Make decisions (merge, create spec, clarify, keep separate)
- Review similarity scores and example skills
- Export resolution actions
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px


def load_validation_data():
    """Load validation report and conflict data."""
    taxonomy_dir = Path(__file__).parent.parent.parent / "taxonomy"
    
    try:
        # Load validation report
        validation_file = taxonomy_dir / "validation_report.json"
        if validation_file.exists():
            with open(validation_file) as f:
                validation_report = json.load(f)
        else:
            validation_report = None
        
        # Load conflicts
        conflicts_file = taxonomy_dir / "conflicts.json"
        if conflicts_file.exists():
            with open(conflicts_file) as f:
                conflicts = json.load(f)
        else:
            conflicts = []
        
        # Load redundancies
        redundancies_file = taxonomy_dir / "redundancies.json"
        if redundancies_file.exists():
            with open(redundancies_file) as f:
                redundancies = json.load(f)
        else:
            redundancies = []
        
        return validation_report, conflicts, redundancies
    
    except Exception as e:
        st.error(f"Error loading validation data: {e}")
        return None, [], []


def display_mece_summary(validation_report):
    """Display MECE score and summary metrics."""
    if not validation_report:
        st.info("⚠️ No validation report available. Run MECE validator first.")
        return
    
    mece_score = validation_report.get('mece_score', 0)
    me_score = validation_report.get('mutual_exclusivity', {}).get('score', 0)
    ce_score = validation_report.get('collective_exhaustiveness', {}).get('score', 0)
    
    st.markdown("### 📊 MECE Quality Score")
    
    # Three-column metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_color = "green" if mece_score >= 0.9 else "orange" if mece_score >= 0.75 else "red"
        st.metric(
            "Overall MECE Score",
            f"{mece_score:.2f}",
            delta=None,
            help="Combined score of Mutually Exclusive + Collectively Exhaustive"
        )
    
    with col2:
        st.metric(
            "Mutually Exclusive",
            f"{me_score:.2f}",
            help="How well base skills avoid overlap"
        )
    
    with col3:
        st.metric(
            "Collectively Exhaustive",
            f"{ce_score:.2f}",
            help="How well base skills cover all ROCK skills"
        )
    
    # Grooming queue summary
    st.markdown("---")
    st.markdown("### 🧹 Grooming Queue Summary")
    
    grooming = validation_report.get('grooming_queue_summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conflicts", grooming.get('total_conflicts', 0))
    
    with col2:
        st.metric("High Confidence Merges", grooming.get('high_confidence_merges', 0))
    
    with col3:
        st.metric("Specs Needed", grooming.get('spec_needed', 0))
    
    with col4:
        st.metric("Human Review Required", grooming.get('human_review_required', 0))


def display_conflict(conflict, index, total):
    """Display a single base skill conflict for review."""
    st.markdown(f"### Conflict {index + 1} of {total}")
    st.markdown(f"**Conflict ID:** `{conflict.get('conflict_id')}`")
    
    # Two-column layout for skills
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Base Skill A")
        skill_a = conflict['skill_a']
        st.markdown(f"**ID:** {skill_a['id']}")
        st.markdown(f"**Name:** {skill_a['name']}")
        st.markdown(f"**Description:** {skill_a.get('description', 'N/A')}")
        st.info(f"📊 {skill_a.get('rock_skills_count', 0)} ROCK skills mapped")
    
    with col2:
        st.markdown("#### 🎯 Base Skill B")
        skill_b = conflict['skill_b']
        st.markdown(f"**ID:** {skill_b['id']}")
        st.markdown(f"**Name:** {skill_b['name']}")
        st.markdown(f"**Description:** {skill_b.get('description', 'N/A')}")
        st.info(f"📊 {skill_b.get('rock_skills_count', 0)} ROCK skills mapped")
    
    # Similarity score
    similarity = conflict.get('similarity', 0)
    st.markdown("---")
    st.markdown(f"**Semantic Similarity:** {similarity:.2%}")
    
    # Progress bar for similarity
    st.progress(similarity)
    
    # LLM Analysis
    llm_analysis = conflict.get('llm_analysis', {})
    
    if llm_analysis and llm_analysis.get('category') != 'AMBIGUOUS':
        st.markdown("---")
        st.markdown("#### 🤖 LLM Analysis")
        
        category = llm_analysis.get('category', 'UNKNOWN')
        confidence = llm_analysis.get('confidence', 'unknown')
        reasoning = llm_analysis.get('reasoning', '')
        
        # Color-code category
        category_colors = {
            'TRUE_DUPLICATE': '🔴',
            'SPECIFICATION_NEEDED': '🟡',
            'DISTINCT_SKILLS': '🟢',
            'AMBIGUOUS': '⚪'
        }
        category_icon = category_colors.get(category, '⚪')
        
        st.markdown(f"**Category:** {category_icon} {category}")
        st.markdown(f"**Confidence:** {confidence}")
        st.markdown(f"**Reasoning:** {reasoning}")
        
        # Show recommended action
        action = llm_analysis.get('action', {})
        action_type = action.get('type', 'REVIEW')
        
        st.markdown(f"**Recommended Action:** {action_type}")
        
        # Show action details
        if action_type == 'MERGE':
            merged_name = action.get('details', {}).get('merged_name', '')
            if merged_name:
                st.success(f"💡 Suggested merged name: **{merged_name}**")
        
        elif action_type == 'CREATE_SPEC':
            spec_details = action.get('details', {}).get('new_specification', {})
            if spec_details:
                st.warning("💡 Suggested new specification:")
                st.json(spec_details)
        
        elif action_type == 'CLARIFY':
            clarifications = action.get('details', {}).get('clarifications', {})
            if clarifications:
                st.info("💡 Suggested clarifications:")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Skill A:** {clarifications.get('skill_a', 'N/A')}")
                with col2:
                    st.markdown(f"**Skill B:** {clarifications.get('skill_b', 'N/A')}")
    
    # Decision interface
    st.markdown("---")
    st.markdown("#### ✅ Your Decision")
    
    decision = st.radio(
        "What action should be taken?",
        options=[
            "Merge into single base skill",
            "Create specification to differentiate",
            "Keep separate (clarify definitions)",
            "Flag for further review"
        ],
        key=f"decision_{conflict.get('conflict_id')}",
        horizontal=True
    )
    
    notes = st.text_area(
        "Notes (optional)",
        key=f"notes_{conflict.get('conflict_id')}",
        placeholder="Add any additional context or reasoning..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Confirm", key=f"confirm_{conflict.get('conflict_id')}", type="primary"):
            st.success("✓ Decision recorded!")
            # TODO: Save decision to database
    
    with col2:
        if st.button("⏭️ Skip", key=f"skip_{conflict.get('conflict_id')}"):
            st.info("Skipped to next conflict")
    
    st.markdown("---")


def display_redundancy(redundancy, index, total):
    """Display a single ROCK skill redundancy for review."""
    st.markdown(f"### Redundancy {index + 1} of {total}")
    st.markdown(f"**Redundancy ID:** `{redundancy.get('redundancy_id')}`")
    
    base_skill_id = redundancy.get('base_skill_id')
    st.markdown(f"**Base Skill:** {base_skill_id}")
    
    # Two-column layout for skills
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔗 ROCK Skill A")
        skill_a = redundancy['skill_a']
        st.markdown(f"**Name:** {skill_a['name']}")
        st.markdown(f"**Grade:** {skill_a.get('grade', 'Unknown')}")
        st.markdown(f"**State:** {skill_a.get('state', 'Unknown')}")
    
    with col2:
        st.markdown("#### 🔗 ROCK Skill B")
        skill_b = redundancy['skill_b']
        st.markdown(f"**Name:** {skill_b['name']}")
        st.markdown(f"**Grade:** {skill_b.get('grade', 'Unknown')}")
        st.markdown(f"**State:** {skill_b.get('state', 'Unknown')}")
    
    # Similarity and context
    similarity = redundancy.get('similarity', 0)
    same_context = redundancy.get('same_context', False)
    redundancy_type = redundancy.get('redundancy_type', 'unknown')
    
    st.markdown("---")
    st.markdown(f"**Similarity:** {similarity:.2%}")
    st.markdown(f"**Same Context (Grade/State):** {'✓ Yes' if same_context else '✗ No'}")
    st.markdown(f"**Type:** {redundancy_type}")
    
    st.progress(similarity)
    
    # Decision interface
    st.markdown("---")
    st.markdown("#### ✅ Your Decision")
    
    decision = st.radio(
        "What action should be taken?",
        options=[
            "Merge (true duplicate)",
            "Keep both (different specifications)",
            "Flag for review"
        ],
        key=f"red_decision_{redundancy.get('redundancy_id')}",
        horizontal=True
    )
    
    if decision == "Keep both (different specifications)":
        st.text_input(
            "What specification differentiates these skills?",
            key=f"spec_diff_{redundancy.get('redundancy_id')}",
            placeholder="e.g., support_level: 'with_support' vs 'with_prompting'"
        )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ Confirm", key=f"red_confirm_{redundancy.get('redundancy_id')}", type="primary"):
            st.success("✓ Decision recorded!")
            # TODO: Save decision
    
    with col2:
        if st.button("⏭️ Skip", key=f"red_skip_{redundancy.get('redundancy_id')}"):
            st.info("Skipped to next redundancy")
    
    st.markdown("---")


def main():
    st.set_page_config(
        page_title="Redundancy Grooming",
        page_icon="🧹",
        layout="wide"
    )
    
    st.title("🧹 Redundancy Grooming & Conflict Resolution")
    st.markdown("Review and resolve base skill ambiguities and ROCK skill redundancies")
    
    # Load data
    validation_report, conflicts, redundancies = load_validation_data()
    
    # Display MECE summary
    if validation_report:
        display_mece_summary(validation_report)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "🎯 Base Skill Conflicts",
        "🔗 ROCK Skill Redundancies",
        "📊 Analytics"
    ])
    
    with tab1:
        st.markdown("### Base Skill Conflicts")
        st.markdown("Review base skills that may be redundant or need specification refinement.")
        
        if not conflicts:
            st.info("✓ No conflicts found! All base skills are distinct.")
        else:
            # Filter controls
            col1, col2 = st.columns([2, 1])
            
            with col1:
                filter_category = st.selectbox(
                    "Filter by LLM category:",
                    options=["All", "TRUE_DUPLICATE", "SPECIFICATION_NEEDED", "DISTINCT_SKILLS", "AMBIGUOUS"],
                    key="conflict_filter"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    options=["Similarity (high to low)", "Alphabetical"],
                    key="conflict_sort"
                )
            
            # Apply filters
            filtered_conflicts = conflicts
            if filter_category != "All":
                filtered_conflicts = [
                    c for c in conflicts
                    if c.get('llm_analysis', {}).get('category') == filter_category
                ]
            
            # Sort
            if sort_by == "Similarity (high to low)":
                filtered_conflicts = sorted(filtered_conflicts, key=lambda x: x.get('similarity', 0), reverse=True)
            
            st.markdown(f"**Showing {len(filtered_conflicts)} of {len(conflicts)} conflicts**")
            
            # Pagination
            conflicts_per_page = 5
            total_pages = (len(filtered_conflicts) + conflicts_per_page - 1) // conflicts_per_page
            
            if 'conflict_page' not in st.session_state:
                st.session_state.conflict_page = 0
            
            # Display conflicts for current page
            start_idx = st.session_state.conflict_page * conflicts_per_page
            end_idx = min(start_idx + conflicts_per_page, len(filtered_conflicts))
            
            for i in range(start_idx, end_idx):
                display_conflict(filtered_conflicts[i], i, len(filtered_conflicts))
            
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.conflict_page == 0):
                    st.session_state.conflict_page -= 1
                    st.rerun()
            
            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.conflict_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.conflict_page >= total_pages - 1):
                    st.session_state.conflict_page += 1
                    st.rerun()
    
    with tab2:
        st.markdown("### ROCK Skill Redundancies")
        st.markdown("Review ROCK skills that may be duplicates within the same base skill.")
        
        if not redundancies:
            st.info("✓ No redundancies found!")
        else:
            st.markdown(f"**Found {len(redundancies)} potential redundancies**")
            
            # Pagination for redundancies
            redundancies_per_page = 5
            total_pages = (len(redundancies) + redundancies_per_page - 1) // redundancies_per_page
            
            if 'redundancy_page' not in st.session_state:
                st.session_state.redundancy_page = 0
            
            start_idx = st.session_state.redundancy_page * redundancies_per_page
            end_idx = min(start_idx + redundancies_per_page, len(redundancies))
            
            for i in range(start_idx, end_idx):
                display_redundancy(redundancies[i], i, len(redundancies))
            
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.redundancy_page == 0, key="red_prev"):
                    st.session_state.redundancy_page -= 1
                    st.rerun()
            
            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.redundancy_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.redundancy_page >= total_pages - 1, key="red_next"):
                    st.session_state.redundancy_page += 1
                    st.rerun()
    
    with tab3:
        st.markdown("### Redundancy Analytics")
        
        if conflicts:
            # Category distribution
            categories = [c.get('llm_analysis', {}).get('category', 'AMBIGUOUS') for c in conflicts]
            category_counts = pd.Series(categories).value_counts()
            
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Conflict Categories",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Similarity distribution
            similarities = [c.get('similarity', 0) for c in conflicts]
            fig = px.histogram(
                x=similarities,
                nbins=20,
                title="Similarity Score Distribution",
                labels={'x': 'Similarity Score', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No conflicts to analyze")


if __name__ == "__main__":
    main()

