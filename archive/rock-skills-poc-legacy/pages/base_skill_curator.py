#!/usr/bin/env python3
"""
Base Skill Curator UI

Streamlit page for managing base skills with the enhanced taxonomy system.
Provides interface for reviewing, merging, splitting, and managing base skills.

Run from rock-skills/poc/:
    streamlit run skill_bridge_app.py

Then navigate to "Base Skill Curator" in the sidebar.
"""

import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path

# Add analysis/pipelines to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'analysis' / 'pipelines'))

try:
    from quality_metrics import QualityMetricsCalculator
    from granularity_criteria import GranularityAnalyzer
    from validate_mece import MECEValidator
    from feedback_loop import FeedbackLogger
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


def load_base_skills():
    """Load base skills from taxonomy directory."""
    base_skills_dir = Path(__file__).parent.parent.parent / 'taxonomy' / 'base_skills'
    
    if not base_skills_dir.exists():
        return []
    
    base_skills = []
    for json_file in base_skills_dir.glob('BS-*.json'):
        try:
            with open(json_file) as f:
                base_skill = json.load(f)
                base_skills.append(base_skill)
        except Exception as e:
            st.warning(f"Error loading {json_file.name}: {e}")
    
    return base_skills


def load_mece_issues():
    """Load MECE validation issues."""
    issues_file = Path(__file__).parent.parent.parent / 'taxonomy' / 'validation_report.json'
    
    if not issues_file.exists():
        return {'overlaps': [], 'gaps': []}
    
    try:
        with open(issues_file) as f:
            report = json.load(f)
            return {
                'overlaps': report.get('ambiguities', []),
                'gaps': report.get('unmapped_skills', [])
            }
    except Exception as e:
        st.warning(f"Error loading MECE issues: {e}")
        return {'overlaps': [], 'gaps': []}


def display_base_skill_card(base_skill, index):
    """Display a base skill as a card."""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"🎯 {base_skill.get('base_skill_name', 'Unknown')}")
            st.caption(f"ID: {base_skill.get('base_skill_id', 'N/A')}")
        
        with col2:
            quality = base_skill.get('quality_metrics', {}).get('overall_quality', 0)
            grade = base_skill.get('quality_metrics', {}).get('grade', 'N/A')
            
            if grade == 'A':
                st.success(f"Quality: {grade} ({quality:.2f})")
            elif grade == 'B':
                st.info(f"Quality: {grade} ({quality:.2f})")
            else:
                st.warning(f"Quality: {grade} ({quality:.2f})")
        
        # Details
        st.write(f"**Members:** {len(base_skill.get('member_skill_ids', []))} skills")
        
        if 'skill_family' in base_skill:
            st.write(f"**Family:** {base_skill['skill_family']}")
        
        if 'specifications' in base_skill:
            specs = base_skill['specifications']
            if specs:
                st.write(f"**Specifications:** {', '.join(specs.keys())}")
        
        # Actions
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("👁️ View Details", key=f"view_{index}"):
                st.session_state[f'viewing_{index}'] = True
        
        with col_b:
            if st.button("✏️ Edit", key=f"edit_{index}"):
                st.session_state[f'editing_{index}'] = True
        
        with col_c:
            if st.button("🔀 Merge", key=f"merge_{index}"):
                st.session_state[f'merging_{index}'] = True
        
        with col_d:
            if st.button("✂️ Split", key=f"split_{index}"):
                st.session_state[f'splitting_{index}'] = True
        
        # Show details if expanded
        if st.session_state.get(f'viewing_{index}', False):
            with st.expander("📋 Full Details", expanded=True):
                st.json(base_skill)
                if st.button("Close", key=f"close_view_{index}"):
                    st.session_state[f'viewing_{index}'] = False
        
        st.divider()


def display_mece_issue_card(issue, index):
    """Display a MECE issue as a card."""
    with st.container():
        issue_type = issue.get('type', 'overlap')
        
        if issue_type == 'overlap':
            st.warning(f"⚠️ **Overlap Detected**")
            st.write(f"**Skill A:** {issue.get('skill_a_name', 'Unknown')}")
            st.write(f"**Skill B:** {issue.get('skill_b_name', 'Unknown')}")
            st.write(f"**Overlap Score:** {issue.get('overlap_score', 0):.3f}")
            
            if 'signals' in issue:
                signals = issue['signals']
                st.write("**Signals:**")
                for signal, value in signals.items():
                    if isinstance(value, float):
                        st.write(f"  - {signal}: {value:.3f}")
                    else:
                        st.write(f"  - {signal}: {value}")
        
        else:  # gap
            st.info(f"ℹ️ **Unmapped Skill**")
            st.write(f"**Skill:** {issue.get('SKILL_NAME', 'Unknown')}")
            st.write(f"**ID:** {issue.get('SKILL_ID', 'N/A')}")
        
        # Resolution actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve", key=f"approve_{index}"):
                st.success("Resolution approved!")
                if MODULES_AVAILABLE:
                    logger = FeedbackLogger()
                    logger.log_decision('approve', issue, None, 'User approved resolution')
        
        with col2:
            if st.button("❌ Reject", key=f"reject_{index}"):
                st.error("Resolution rejected!")
                if MODULES_AVAILABLE:
                    logger = FeedbackLogger()
                    logger.log_decision('reject', issue, None, 'User rejected resolution')
        
        with col3:
            if st.button("✏️ Custom", key=f"custom_{index}"):
                st.info("Opening custom resolution dialog...")
        
        st.divider()


def main():
    """Main curator interface."""
    st.set_page_config(
        page_title="Base Skill Curator",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Base Skill Curator")
    st.caption("Manage and refine base skills in the taxonomy")
    
    if not MODULES_AVAILABLE:
        st.error("⚠️ Analysis modules not available. Please ensure pipelines are installed.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        
        view_mode = st.radio(
            "View",
            ["Base Skills", "MECE Issues", "Analytics"],
            index=0
        )
        
        st.divider()
        
        if view_mode == "Base Skills":
            quality_filter = st.multiselect(
                "Quality Grade",
                ['A', 'B', 'C', 'D', 'F'],
                default=['A', 'B', 'C', 'D', 'F']
            )
            
            family_filter = st.multiselect(
                "Skill Family",
                ['Comprehension', 'Phonics', 'Writing', 'Vocabulary', 'Fluency'],
                default=[]
            )
            
            sort_by = st.selectbox(
                "Sort By",
                ["Name", "Quality (High to Low)", "Quality (Low to High)", "Member Count"],
                index=0
            )
        
        elif view_mode == "MECE Issues":
            issue_type = st.radio(
                "Issue Type",
                ["All", "Overlaps", "Gaps"],
                index=0
            )
            
            confidence_filter = st.multiselect(
                "Confidence",
                ['high', 'medium', 'low'],
                default=['high', 'medium', 'low']
            )
        
        st.divider()
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Main content
    if view_mode == "Base Skills":
        st.header("📚 Base Skills Library")
        
        # Load base skills
        base_skills = load_base_skills()
        
        if not base_skills:
            st.warning("No base skills found. Run the extraction pipeline first.")
            st.code("cd rock-skills/analysis/pipelines\n"
                   "python3 extract_base_skills.py --input ../../rock_data/skill_list_filtered_data_set.csv")
            return
        
        # Apply filters
        filtered_skills = base_skills
        
        if quality_filter:
            filtered_skills = [bs for bs in filtered_skills 
                             if bs.get('quality_metrics', {}).get('grade', 'F') in quality_filter]
        
        if family_filter:
            filtered_skills = [bs for bs in filtered_skills 
                             if bs.get('skill_family') in family_filter]
        
        # Apply sorting
        if sort_by == "Name":
            filtered_skills.sort(key=lambda x: x.get('base_skill_name', ''))
        elif sort_by == "Quality (High to Low)":
            filtered_skills.sort(key=lambda x: x.get('quality_metrics', {}).get('overall_quality', 0), reverse=True)
        elif sort_by == "Quality (Low to High)":
            filtered_skills.sort(key=lambda x: x.get('quality_metrics', {}).get('overall_quality', 0))
        elif sort_by == "Member Count":
            filtered_skills.sort(key=lambda x: len(x.get('member_skill_ids', [])), reverse=True)
        
        # Display summary
        st.metric("Total Base Skills", len(filtered_skills))
        
        if filtered_skills != base_skills:
            st.info(f"Showing {len(filtered_skills)} of {len(base_skills)} base skills")
        
        # Display base skills
        for i, base_skill in enumerate(filtered_skills):
            display_base_skill_card(base_skill, i)
    
    elif view_mode == "MECE Issues":
        st.header("⚠️ MECE Issues")
        
        # Load issues
        issues = load_mece_issues()
        
        overlaps = issues.get('overlaps', [])
        gaps = issues.get('gaps', [])
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Issues", len(overlaps) + len(gaps))
        col2.metric("Overlaps", len(overlaps))
        col3.metric("Gaps", len(gaps))
        
        # Filter by type
        if issue_type == "All":
            display_issues = [{'type': 'overlap', **issue} for issue in overlaps] + \
                           [{'type': 'gap', **issue} for issue in gaps]
        elif issue_type == "Overlaps":
            display_issues = [{'type': 'overlap', **issue} for issue in overlaps]
        else:  # Gaps
            display_issues = [{'type': 'gap', **issue} for issue in gaps]
        
        # Filter by confidence (for overlaps)
        if confidence_filter:
            display_issues = [issue for issue in display_issues 
                            if issue.get('confidence', 'medium') in confidence_filter]
        
        if not display_issues:
            st.success("✅ No MECE issues found! Taxonomy is in good shape.")
            return
        
        st.info(f"Showing {len(display_issues)} issues")
        
        # Display issues
        for i, issue in enumerate(display_issues):
            display_mece_issue_card(issue, i)
    
    else:  # Analytics
        st.header("📊 Taxonomy Analytics")
        
        base_skills = load_base_skills()
        
        if not base_skills:
            st.warning("No base skills found for analytics.")
            return
        
        # Quality distribution
        st.subheader("Quality Grade Distribution")
        
        grades = [bs.get('quality_metrics', {}).get('grade', 'F') for bs in base_skills]
        grade_counts = pd.Series(grades).value_counts().sort_index()
        
        st.bar_chart(grade_counts)
        
        # Size distribution
        st.subheader("Member Count Distribution")
        
        member_counts = [len(bs.get('member_skill_ids', [])) for bs in base_skills]
        st.write(f"**Mean:** {np.mean(member_counts):.1f}")
        st.write(f"**Median:** {np.median(member_counts):.1f}")
        st.write(f"**Min:** {min(member_counts)}")
        st.write(f"**Max:** {max(member_counts)}")
        
        st.line_chart(pd.Series(member_counts).value_counts().sort_index())
        
        # Specifications coverage
        st.subheader("Specification Coverage")
        
        all_specs = []
        for bs in base_skills:
            all_specs.extend(bs.get('specifications', {}).keys())
        
        if all_specs:
            spec_counts = pd.Series(all_specs).value_counts()
            st.bar_chart(spec_counts)
        else:
            st.info("No specifications found yet.")


if __name__ == "__main__":
    # Import numpy for analytics
    import numpy as np
    main()

