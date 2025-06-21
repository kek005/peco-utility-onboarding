from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_verdict_from_checklist(checklist_summary):
    prompt = f"""
    You are a PECO utility account approval agent.

    Your job is to analyze the following checklist summary and return ONLY one decision:

    ✅ Proceed with account creation.
    ❌ Cannot proceed with account creation.

    Rules to decide:

    ✅ You MUST proceed if:
    - The lease document is signed.
    - The ID is valid (not expired).
    - The lease and ID show consistent names or confirm the same person — it's okay if the ID name is not explicitly extracted, as long as the explanation clearly shows a match.
    - The explanation confirms eligibility or says the user is verified.

    ❌ You MUST reject if:
    - The ID is expired.
    - The lease is unsigned.
    - The names clearly don’t match and explanation doesn't confirm a match.

    Ignore:
    - Missing photo
    - Partial name extraction
    - Minor formatting issues

    Checklist summary:
    {checklist_summary}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You decide if PECO can proceed with account creation."},
            {"role": "user", "content": f"Checklist Summary:\n{checklist_summary}\n\n{prompt}"}
        ],
        temperature=0,
        max_tokens=50
    )

    return response.choices[0].message.content.strip()