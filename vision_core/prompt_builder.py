from use_case_config import PROMPTS

def generate_questions_from_intent(intent, doc_type):
    return PROMPTS.get(doc_type, [])