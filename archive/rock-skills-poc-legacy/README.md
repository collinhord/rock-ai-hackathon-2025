# ROCK Skills Bridge Explorer - POC

An interactive web application demonstrating how Science of Reading taxonomy can bridge fragmented ROCK skills to solve the horizontal fragmentation problem.

## Features

### 1. Master Concept Browser
- Browse Science of Reading master concepts
- See all ROCK skills mapped to each concept
- View skill variants across different states/authorities
- Filter by taxonomy strand

### 2. Skill Inspector
- Search ROCK skills by name
- View full skill details
- See taxonomy mappings (when available)
- Identify unmapped skills

### 3. Redundancy Visualizer
- Quantitative proof of fragmentation
- Bar charts showing skills per concept
- Distribution histograms of redundancy
- Summary statistics

### 4. Science of Reading Taxonomy Browser
- Explore the hierarchical taxonomy structure
- Browse: Strand → Pillar → Domain → Skill Area → Skill Subset
- View detailed descriptions and annotations

### 5. Technical Overview
- System architecture diagrams
- Data flow and performance metrics
- Production scaling strategy
- PostgreSQL schema design
- API endpoint specifications
- Technology stack breakdown

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Navigate to the POC directory:**
```bash
cd rock-skills/poc
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Streamlit app:
```bash
streamlit run skill_bridge_app.py
```

The app will open in your default browser at `http://localhost:8501`

### Alternative: Run from project root
```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/poc
streamlit run skill_bridge_app.py
```

## Data Requirements

The app expects the following data structure:

```
rock-ai-hackathon-2025/
├── rock-skills/
│   ├── rock_schemas/
│   │   ├── SKILLS.csv
│   │   ├── STANDARD_SKILLS.csv
│   │   └── STANDARD_SETS.csv
│   ├── analysis/
│   │   ├── skill-taxonomy-mapping.csv
│   │   ├── master-concepts.csv
│   │   └── fragmentation-examples.csv
│   ├── POC_science_of_reading_literacy_skills_taxonomy.csv
│   └── poc/
│       ├── skill_bridge_app.py
│       ├── data_loader.py
│       └── requirements.txt
```

## Key Files

- **`skill_bridge_app.py`** - Main Streamlit application
- **`data_loader.py`** - Data loading and caching module
- **`requirements.txt`** - Python dependencies

## Usage Tips

### Master Concept Browser
1. Use the search box to find concepts by keyword (e.g., "blend", "context")
2. Filter by Science of Reading Strand to narrow results
3. Expand concept cards to see all mapped ROCK skills
4. Notice how many skill variants exist for each concept

### Skill Inspector
1. Search for ROCK skills using keywords
2. View skills that match your query
3. Check taxonomy mapping status (✅ Mapped or ❌ Not Mapped)
4. See which master concept each skill belongs to

### Redundancy Visualizer
1. View summary statistics at the top
2. Examine bar chart showing most fragmented concepts
3. Study distribution histogram to see redundancy patterns
4. Scroll through detailed table for all concepts

### Science of Reading Taxonomy
1. Select Strand, Pillar, Domain, and Skill Area from dropdowns
2. View detailed skill subsets with annotations
3. Understand the hierarchical structure of the framework

## Demo Scenarios

### Scenario 1: Find All Phoneme Blending Skills
1. Go to **Master Concept Browser**
2. Search for "blend"
3. Click on "Phoneme Blending" concept
4. See 12 different ROCK skills teaching the same concept across states

**Value Demo:** Without taxonomy, you'd have to manually search and might miss variants.

### Scenario 2: Check If Skill Is Mapped
1. Go to **Skill Inspector**
2. Search for "context clues"
3. View individual skills
4. See which ones have taxonomy mappings

**Value Demo:** Shows coverage of current mapping effort.

### Scenario 3: Quantify Redundancy
1. Go to **Redundancy Visualizer**
2. View average redundancy ratio (6-8x)
3. See distribution across all concepts
4. Identify most fragmented areas

**Value Demo:** Provides quantitative proof of the problem.

## Troubleshooting

### App won't start
- Ensure you're in the `poc` directory
- Check that virtual environment is activated
- Verify all dependencies are installed: `pip list`

### Data not loading
- Confirm CSV files exist in expected locations
- Check file paths in `data_loader.py`
- Review Streamlit error messages in terminal

### Performance issues
- Large CSV files are sampled for performance
- Caching is enabled for data loading
- Consider reducing sample size in `data_loader.py`

## Future Enhancements

### Phase 2 Features (if time permits):
- [ ] Export skill mappings to CSV
- [ ] Side-by-side skill comparison
- [ ] Suggested mappings using AI embeddings
- [ ] Authority-specific filtering
- [ ] Grade level heatmaps

### Production Features:
- [ ] Database backend (PostgreSQL)
- [ ] RESTful API
- [ ] User authentication
- [ ] Collaborative mapping workflow
- [ ] Confidence scoring system
- [ ] Audit trail for mappings

## Technical Notes

### Performance
- CSVs are loaded with `@st.cache_data` for fast reloading
- STANDARD_SKILLS limited to 500K rows (from >2M) for performance
- Pandas used for efficient data manipulation

### Architecture
- **Frontend**: Streamlit (Python web framework)
- **Data Layer**: Pandas DataFrames with caching
- **Visualization**: Plotly for interactive charts
- **State Management**: Streamlit session state

## Contact

For questions or issues, contact the ROCK Skills Analysis team.

---

**Renaissance Learning Hackathon 2025**  
*Solving the Master Skill Fragmentation Problem*

