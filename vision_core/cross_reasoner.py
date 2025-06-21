import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_cross_document_consistency(vision_trace: list, checklist_summary: dict, intent: str) -> dict:
    """
    Synthesizes checklist and raw document responses to deliver a final verdict.
    Ensures output aligns with utility onboarding goals, using only structured summaries.
    """

    formatted = {
        "intent": intent,
        "checklist_summary": checklist_summary,
        "vision_responses": [
            {k: v for k, v in row.items() if k != "image"}
            for row in vision_trace
        ]
    }

    system_prompt = (
        "You're a document reasoning expert helping utility companies verify lease and identity documents.\n\n"
        "Your job is to:\n"
        "1. Analyze the checklist and vision responses.\n"
        "2. Make a final recommendation about whether the user is verified and eligible for service.\n\n"
        "When comparing names:\n"
        "- Accept partial matches if it is very likely to be the same person (e.g., 'KEKE Jesugnon' ≈ 'Keke Jesugnon Maxime')\n"
        "- It is OK if there are two names on the lease but only one ID, as long as one person matches.\n"
        "- Use human-level judgment. Do not be overly strict.\n\n"
        "Return a structured JSON object with:\n"
        " - 'final_recommendation': One strong sentence.\n"
        " - 'key_facts': Dictionary of the most relevant facts.\n"
        " - 'explanation': Paragraph summarizing your reasoning.\n\n"
        "Output must be valid JSON. Do not include long document quotes."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(formatted, indent=2)}
        ],
        temperature=0.3,
        max_tokens=1000
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {
            "final_recommendation": response.choices[0].message.content.strip(),
            "key_facts": {},
            "explanation": "❌ Failed to parse structured output. Raw reasoning shown instead."
        }