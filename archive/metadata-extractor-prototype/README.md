# Skills Data Viewer

A simple Streamlit app that loads and displays skills data from a CSV file.

## Features

- Automatically loads data from `./data/sample_data.csv`
- Displays only the Index (SKILL_ID) and Skill Name (SKILL_NAME) columns
- Shows data in an interactive table format
- Displays basic statistics about the data

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install the spaCy English model (required for spaCy tagging functionality):
```bash
python -m spacy download en_core_web_lg
```

## Usage

### Option 1: Run with pyenv virtual environment (Recommended)
```bash
python -m streamlit run streamlit_app.py
```


The app will be available at `http://localhost:8501` in your web browser.

## Data Format

The app expects a CSV file with the following columns:
- `SKILL_ID`: The unique identifier for each skill (used as index)
- `SKILL_NAME`: The name/description of the skill

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── data/
│   └── sample_data.csv      # Sample data file
└── README.md                # This file
```
