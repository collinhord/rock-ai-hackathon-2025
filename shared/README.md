# Shared Infrastructure

This directory contains shared code and utilities used across all three project domains.

## Structure

```
shared/
├── data_access/          # Snowflake and CSV data loading
│   ├── snowflake_connector.py
│   └── __init__.py
├── llm/                  # AWS Bedrock LLM interface
│   ├── bedrock_client.py
│   └── __init__.py
├── models/               # Common data models
│   ├── skill.py
│   └── __init__.py
├── utils/                # Common utilities
│   ├── logging_config.py
│   ├── validation.py
│   ├── export.py
│   └── __init__.py
└── schemas/              # JSON schemas
    ├── rock_skill_schema.json
    └── common_enums.json
```

## Usage

### Data Access

```python
from shared.data_access import SkillDataLoader

# Initialize loader
loader = SkillDataLoader()

# Load all skills
skills = loader.get_all_skills()

# Filter by content area
ela_skills = loader.get_all_skills(content_area='English Language Arts')

# Load with standards
skills_with_standards = loader.get_skills_with_standards([1, 2, 3])
```

### LLM Interface

```python
from shared.llm import BedrockLanguageModels

# Initialize client
llm = BedrockLanguageModels(
    region_name='us-west-2',
    profile_name='ai-poc'
)

# Make a simple call
response = llm.simple_call(
    messages=[{"role": "user", "content": "Analyze this skill"}],
    system_prompt="You are an expert in educational skills.",
    model="claude-3-5-v2"
)
```

### Data Models

```python
from shared.models import Skill
import pandas as pd

# Create from DataFrame row
skill = Skill.from_series(df.iloc[0])

# Create list from DataFrame
skills = Skill.from_dataframe(df)

# Convert to dictionary
skill_dict = skill.to_dict()
```

### Utilities

```python
from shared.utils import (
    setup_logging,
    validate_required_columns,
    export_to_csv,
    export_to_json
)

# Setup logging
logger = setup_logging('my_module', level=logging.INFO)

# Validate data
is_valid = validate_required_columns(df, ['SKILL_ID', 'SKILL_NAME'])

# Export data
export_to_csv(df, 'output/results.csv', add_timestamp=True)
export_to_json(data_dict, 'output/results.json')
```

## Design Principles

1. **DRY (Don't Repeat Yourself)**: Common code lives here, not in individual projects
2. **Single Responsibility**: Each module has a clear, focused purpose
3. **Dependency Injection**: Projects depend on interfaces, not implementations
4. **Configuration over Code**: Settings in config files, not hardcoded
5. **Fail Gracefully**: Provide fallbacks (e.g., local CSV if Snowflake unavailable)

## Adding New Shared Code

When adding new shared functionality:

1. **Consider**: Is this used by 2+ projects? If yes, it belongs here.
2. **Location**: Choose the appropriate subdirectory (data_access, llm, models, utils)
3. **Documentation**: Add docstrings and usage examples
4. **Testing**: Add tests in project-specific test suites
5. **Export**: Add to `__all__` in the module's `__init__.py`

## Dependencies

Shared infrastructure has minimal external dependencies:

- `pandas` - Data manipulation
- `pyyaml` - Configuration files
- `boto3` - AWS Bedrock access
- `snowflake-connector-python` - Optional Snowflake access

Individual projects may have additional dependencies.

