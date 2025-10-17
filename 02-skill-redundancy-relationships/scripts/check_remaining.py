import pandas as pd

# Load all skills and existing mappings
skills = pd.read_csv('../rock_schemas/SKILLS.csv', usecols=['SKILL_ID', 'CONTENT_AREA_NAME'])
mappings = pd.read_csv('llm_skill_mappings.csv')

# Filter ELA skills
ela_skills = skills[skills['CONTENT_AREA_NAME'] == 'English Language Arts']
print(f'Total ELA skills in ROCK: {len(ela_skills):,}')
print(f'Already mapped: {len(mappings):,}')

# Calculate remaining
already_mapped = set(mappings['SKILL_ID'])
ela_remaining = ela_skills[~ela_skills['SKILL_ID'].isin(already_mapped)]
print(f'Remaining to map: {len(ela_remaining):,}')

# Estimate time and cost
avg_time_per_skill = 9.0  # seconds
total_time_minutes = (len(ela_remaining) * avg_time_per_skill) / 60
total_time_hours = total_time_minutes / 60

avg_tokens_per_skill = 1585  # from 110,954 / 70
total_tokens = len(ela_remaining) * avg_tokens_per_skill
input_tokens = total_tokens * 0.3  # ~30% input
output_tokens = total_tokens * 0.7  # ~70% output
estimated_cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)

print(f'\nEstimated completion time: {total_time_hours:.1f} hours ({total_time_minutes:.0f} minutes)')
print(f'Estimated tokens: {total_tokens:,.0f}')
print(f'Estimated cost: ${estimated_cost:.2f}')
print(f'\nRecommended batch size: 200 skills (~30 minutes per batch)')
print(f'Number of batches needed: {(len(ela_remaining) + 199) // 200}')

