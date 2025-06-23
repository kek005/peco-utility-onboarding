⚡ VisionFlow AI — Utility Onboarding Agent
Turn document chaos into onboarding clarity.
VisionFlow AI is an intelligent agent that analyzes lease agreements and government-issued IDs to determine if a customer qualifies to open a utility account — all in seconds.

🚀 What It Does
This app uses GPT-4o to:

📄 Extract key facts from lease and ID documents (name, address, dates, signatures, etc.)

✅ Cross-validate consistency between lease and ID

🤖 Produce an instant decision: Approve, Flag, or Reject

🧠 Explain the decision with structured reasoning

📧 Email results to utility company staff or the customer

🛠️ Live Demo
Try the live version:
🔗 https://visionflow-ai.streamlit.app

📦 Use Cases
🏢 Utility Companies – Speed up account creation by automating document review.

🧾 Tenant Verification – Validate lease agreements at scale.

🛡️ Fraud Detection – Catch mismatches or forged documents.

🧑‍💼 BPOs & Customer Support – Reduce human review workload by 90%.

🧠 Powered By
🔍 GPT-4o – Handles deep reasoning and judgment

🐍 Python / Streamlit – Fast UI and back-end glue

📧 SendGrid – Emails detailed reports

📂 PDF Parsing + Prompt Engineering – Accurate and structured outputs

🧪 Example Output
json
Copy code
{
  "final_recommendation": "✅ The lease and ID are consistent. Approve account creation.",
  "key_facts": {
    "Lease name": "Jesugnon Keke",
    "Lease address": "750 Moore Road, Apartment 117",
    "Lease duration": "2024-2025",
    "ID expiration": "April 2029",
    "Signatures present": "True"
  },
  "explanation": "The lease name matches the ID. The address and dates are valid. All signatures are present. Documents support account approval."
}
📥 Installation (Local Dev)
bash
Copy code
git clone https://github.com/kek005/peco-utility-onboarding.git
cd peco-utility-onboarding
pip install -r requirements.txt
streamlit run app.py
Make sure to:

Add your OpenAI API key

Set your SendGrid email API key in .env

📫 Contact
Built by Jesugnon KEKE
🔗 LinkedIn
✉️ ancestreseul@gmail.com

⭐ Why This Matters
Utilities get thousands of onboarding requests. Most are delayed by slow manual review. VisionFlow AI removes the bottleneck — making onboarding fast, accurate, and scalable.

If you're a utility company or B2B service that deals with document onboarding, this project is your blueprint.