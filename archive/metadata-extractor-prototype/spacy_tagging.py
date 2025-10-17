import spacy
import pandas as pd
nlp = spacy.load("en_core_web_lg")

def find_first_verb(skill_name: str):
    doc = nlp(skill_name)
    for token in doc:
        if token.pos_ == "VERB":
            return token.text
    return None

def get_tagging_for_skill_name_using_spacy(skill_df: pd.DataFrame):
    skill_ids = []
    tagging = []
    for _, row in skill_df.iterrows():
        skill_name = row['SKILL_NAME']
        skill_id = row['SKILL_ID']
        result = find_first_verb(skill_name)
        skill_ids.append(skill_id)
        tagging.append(result)
    return pd.DataFrame({'SKILL_ID': skill_ids, 'SPACY_TAGGING': tagging})