import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_results(full_trace, checklist_items):
    final_results = {}
    page_evidence = {}

    for item in checklist_items:
        final_results[item] = "❌ Not Found"
        page_evidence[item] = None

    for item in checklist_items:
        for row in full_trace:
            gpt_eval = run_gpt_requirement_check(item, row["response"])

            if gpt_eval.lower().startswith("yes"):
                final_results[item] = f"✅ Found on Page {row['page']}"
                page_evidence[item] = row["page"]
                break

    return final_results, page_evidence

def run_gpt_requirement_check(requirement, response):
    prompt = f"""
You are a document analyst verifying whether a response from an AI vision model satisfies a given requirement.

Requirement:
"{requirement}"

Vision Response:
"{response}"

Evaluate whether the requirement is satisfied even if the response uses different wording, synonyms, or appears indirectly.

Your answer should begin with YES or NO, followed by a short explanation.
"""

    result = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You evaluate whether each document response meets the requirement."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
    )

    return result.choices[0].message.content.strip()