from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mapping OpenAI response to internal safe keys
CLASS_MAP = {
    "Lease": "lease",
    "Utility Bill": "utility_bill",
    "Bank Statement": "bank_statement",
    "Insurance Card": "insurance_card",
    "Driver License": "resident_verification",
    "State ID": "resident_verification",
    "Other": "other"
}

def classify_document(preview_text, filename="document"):
    prompt = f"""
You are a document classifier. Based on the filename and content preview below, identify the document type.

Filename: {filename}
Content Preview:
\"\"\"
{preview_text}
\"\"\"

Choose **only one** of the following categories:
- Lease
- Utility Bill
- Bank Statement
- Insurance Card
- Driver License
- State ID
- Other

Respond only with the category name.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You classify documents based on textual clues. Return only the type."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=10
    )

    raw_type = response.choices[0].message.content.strip()
    return CLASS_MAP.get(raw_type, "other")