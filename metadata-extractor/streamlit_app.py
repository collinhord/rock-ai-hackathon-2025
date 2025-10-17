import streamlit as st
import pandas as pd
import time
from llm_tagging import get_tagging_for_skill_name
from spacy_tagging import get_tagging_for_skill_name_using_spacy
def main():
    st.set_page_config(
        page_title="Skills Data Viewer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Skills Data Viewer")
    st.markdown("---")
    
    try:
        # Load the CSV file
        csv_path = "./data/sample_data.csv"
        df = pd.read_csv(csv_path)
        
        # Select only the index column (SKILL_ID) and skill_name column (SKILL_NAME)
        selected_columns = ['SKILL_ID', 'SKILL_NAME']
        
        # Check if the required columns exist
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing columns in CSV: {missing_columns}")
            st.info("Available columns:")
            st.write(df.columns.tolist())
            return
        
        # Create a new dataframe with only the selected columns
        display_df = df[selected_columns].copy()
        
        # Rename columns for better display
        display_df = display_df.rename(columns={
            'SKILL_ID': 'Skill ID',
            'SKILL_NAME': 'Skill Name'
        })
        
        # Initialize session state for tracking tagging results and timing
        if 'tagging_results' not in st.session_state:
            st.session_state.tagging_results = None
        if 'llm_time' not in st.session_state:
            st.session_state.llm_time = None
        if 'spacy_time' not in st.session_state:
            st.session_state.spacy_time = None
        
        # Display the data based on whether tagging is complete
        if st.session_state.tagging_results is not None:
            # Display results with LLM and spaCy tagging
            st.subheader("📊 Skills Data with LLM + spaCy Tagging")
            
            # Create a styled dataframe to highlight differences
            def highlight_differences(row):
                llm_val = str(row['LLM Tagging']).strip().lower() if pd.notna(row['LLM Tagging']) else ''
                spacy_val = str(row['spaCy Tagging']).strip().lower() if pd.notna(row['spaCy Tagging']) else ''
                
                if llm_val != spacy_val:
                    return ['background-color: #fff3cd'] * len(row)  # Light amber highlight
                else:
                    return [''] * len(row)
            
            # Apply highlighting
            styled_df = st.session_state.tagging_results.style.apply(highlight_differences, axis=1)
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=False
            )
            
            # Count differences and show summary
            df_results = st.session_state.tagging_results
            differences = 0
            for _, row in df_results.iterrows():
                llm_val = str(row['LLM Tagging']).strip().lower() if pd.notna(row['LLM Tagging']) else ''
                spacy_val = str(row['spaCy Tagging']).strip().lower() if pd.notna(row['spaCy Tagging']) else ''
                if llm_val != spacy_val:
                    differences += 1
            
            st.success(f"🎉 Successfully processed {len(st.session_state.tagging_results)} skills!")
            if differences > 0:
                st.warning(f"⚠️ Found {differences} skills where LLM and spaCy tagging differ (highlighted in yellow)")
            else:
                st.info("✅ All LLM and spaCy tagging results match!")
            
            # Display timing information
            if st.session_state.llm_time is not None and st.session_state.spacy_time is not None:
                st.markdown("---")
                st.subheader("⏱️ Processing Times")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🤖 LLM Processing Time", f"{st.session_state.llm_time:.2f} seconds")
                with col2:
                    st.metric("🔤 spaCy Processing Time", f"{st.session_state.spacy_time:.2f} seconds")
                
                # Show which method was faster
                if st.session_state.llm_time < st.session_state.spacy_time:
                    st.info(f"🚀 LLM was {st.session_state.spacy_time - st.session_state.llm_time:.2f} seconds faster than spaCy")
                elif st.session_state.spacy_time < st.session_state.llm_time:
                    st.info(f"🚀 spaCy was {st.session_state.llm_time - st.session_state.spacy_time:.2f} seconds faster than LLM")
                else:
                    st.info("⚖️ Both methods took the same amount of time")
        else:
            # Display original data
            st.subheader("Skills Data")
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=False
            )
        
        # Add buttons at the bottom
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start LLM + spaCy Tagging", type="primary", use_container_width=True):
                # Show progress bar and status
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔄 Starting LLM + spaCy tagging process...")
                    progress_bar.progress(5)
                    
                    # Call the LLM tagging function with timing
                    status_text.text("🤖 Processing skills with LLM...")
                    progress_bar.progress(25)
                    
                    llm_start_time = time.time()
                    llm_results = get_tagging_for_skill_name(df[selected_columns])
                    llm_end_time = time.time()
                    llm_duration = llm_end_time - llm_start_time
                    st.session_state.llm_time = llm_duration
                    
                    progress_bar.progress(50)
                    
                    status_text.text("✅ LLM tagging completed! Now starting spaCy processing...")
                    progress_bar.progress(60)
                    
                    # Call the spaCy tagging function with timing
                    status_text.text("🔤 Processing skills with spaCy...")
                    progress_bar.progress(75)
                    
                    spacy_start_time = time.time()
                    spacy_results = get_tagging_for_skill_name_using_spacy(df[selected_columns])
                    spacy_end_time = time.time()
                    spacy_duration = spacy_end_time - spacy_start_time
                    st.session_state.spacy_time = spacy_duration
                    
                    progress_bar.progress(90)
                    
                    status_text.text("🔗 Merging results...")
                    # Left join with original df using SKILL_ID
                    final_df = df[selected_columns].merge(llm_results, on='SKILL_ID', how='left')
                    final_df = final_df.merge(spacy_results, on='SKILL_ID', how='left')
                    
                    # Rename columns for final display
                    final_display_df = final_df.rename(columns={
                        'SKILL_ID': 'Skill ID',
                        'SKILL_NAME': 'Skill Name',
                        'LLM_TAGGING': 'LLM Tagging',
                        'SPACY_TAGGING': 'spaCy Tagging'
                    })
                    
                    progress_bar.progress(100)
                    status_text.text("✅ LLM + spaCy tagging completed!")
                    
                    # Store results in session state
                    st.session_state.tagging_results = final_display_df
                    
                    # Force a rerun to update the display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error during LLM + spaCy tagging: {str(e)}")
                    status_text.text("❌ Process failed")
                    progress_bar.progress(0)
        
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                # Clear the tagging results and timing data
                st.session_state.tagging_results = None
                st.session_state.llm_time = None
                st.session_state.spacy_time = None
                st.rerun()
        
        
    except FileNotFoundError:
        st.error(f"CSV file not found at: {csv_path}")
        st.info("Please make sure the file exists at the specified path.")
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")

if __name__ == "__main__":
    main()
