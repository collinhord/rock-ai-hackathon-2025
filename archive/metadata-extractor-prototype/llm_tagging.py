from bed_rock_language_models import BedrockLanguageModels
import json
import pandas as pd
from prompts.prompt_1 import system_prompt_1, user_prompt_1


def generate_generirc_description_with_llm_for_freckle_lession(
        skill_name: str,
        system_prompt: str,
        user_prompt: str,
    ):

    # initialize the LLM
    bed_rock_model = BedrockLanguageModels('us-west-2')

    # create LLM messages with the skill name
    _messages = [
        {'role': 'user', 'content': "The sentence to analyze is: " + skill_name},
        {'role': 'user', 'content': user_prompt},
    ]

    # For simple_call, we add the prefill as an assistant message to start the response
    # Make API call
    response = bed_rock_model.simple_call(messages=_messages, system_prompt=system_prompt)

    try:            
        # Parse the response
        return response
    
    except Exception as e:
        # raise ValueError(f"LLM returned invalid JSON : {e}")
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response}")
        return None

# if __name__ == "__main__":
#     skill_name = "I want to learn how to cook a pizza"
#     system_prompt = system_prompt_1
#     user_prompt = user_prompt_1
#     result = generate_generirc_description_with_llm_for_freckle_lession(skill_name, system_prompt, user_prompt)
#     print(result)

def get_tagging_for_skill_name(skill_df: pd.DataFrame):
    skill_ids = []
    tagging = []
    for _, row in skill_df.iterrows():
        skill_name = row['SKILL_NAME']
        skill_id = row['SKILL_ID']
        result = generate_generirc_description_with_llm_for_freckle_lession(skill_name, system_prompt_1, user_prompt_1)
        skill_ids.append(skill_id)
        tagging.append(result)
    return pd.DataFrame({'SKILL_ID': skill_ids, 'LLM_TAGGING': tagging})