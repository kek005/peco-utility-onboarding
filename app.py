import streamlit as st
from vision_core.vision_runner import run_pipeline
from vision_core.document_classifier import classify_document
from vision_core.vision_utils import extract_preview_text
from vision_core.email_utils import send_verification_email
import json

st.set_page_config(page_title="VisionFlow AI – PECO Edition", layout="wide")
st.title("⚡ VisionFlow for PECO — Utility Document Validator")

st.markdown("Upload all required documents (e.g. lease + ID). VisionFlow will verify eligibility for PECO electricity account setup.")

uploaded_files = st.file_uploader(
    "📂 Upload documents (Lease, ID, etc.)",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

typed_files = []
if uploaded_files:
    st.subheader("🔍 Auto-Detecting Document Types...")
    for file in uploaded_files:
        with st.spinner(f"Classifying `{file.name}`..."):
            doc_preview_text = extract_preview_text(file, max_pages=2)
            doc_type = classify_document(doc_preview_text, file.name)

        st.markdown(f"✅ `{file.name}` classified as: **{doc_type}**")
        typed_files.append((file, doc_type))


use_case_intent = st.text_area(
    "📌 Use Case Intent",
    value="Verify lease and ID for PECO electricity utility account creation"
)
user_email = st.text_input("📧 Enter email to receive results", placeholder="example@domain.com")
send_email = st.checkbox("Send results to email")

if st.button("🚀 Run Verification") and typed_files and use_case_intent:
    with st.spinner("Analyzing documents using VisionFlow..."):
        print("I'm calling the run pipeline function from vision runner")
        results, checklist, page_evidence, final_verdict = run_pipeline(use_case_intent, typed_files)

    short_verdict = final_verdict.get("short_verdict")
    final_recommendation = final_verdict.get("final_recommendation")
    explanation = final_verdict.get("explanation")
    key_facts = final_verdict.get("key_facts", {})
    raw_output = final_verdict.get("raw_output")


    if short_verdict:
        if short_verdict.lower().startswith("✅"):
            st.markdown(f"<div style='background-color:#d1fae5;padding:1rem;border-radius:0.5rem;color:#065f46;font-size:1.2rem;'><b>{short_verdict}</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#fee2e2;padding:1rem;border-radius:0.5rem;color:#991b1b;font-size:1.2rem;'><b>{short_verdict}</b></div>", unsafe_allow_html=True)


    st.markdown("### 🧠 Explanation")
    if explanation:
        st.info(explanation)
    elif raw_output:
        st.info(f"🛠️ Raw GPT Output\n\n{raw_output}")
    else:
        st.warning("No explanation available.")

    # ✅ Final Recommendation
    st.markdown("## ✅ Recommendation")
    #st.success(final_verdict.get("final_recommendation", "❓ No recommendation returned."))
    st.success(final_recommendation or "❓ No recommendation returned.")

    # 📧 Email results
    if send_email and user_email:
        try:
            html = f"""
            <p style="font-size: 1.2em;"><strong>{final_verdict.get('short_verdict', '❓ No verdict returned.')}</strong></p>

            <h2>✅ Recommendation</h2>
            <p>{final_verdict.get('final_recommendation')}</p>

            <h3>📌 Key Facts</h3>
            <ul>
            {''.join([f"<li><b>{k.replace('_',' ').capitalize()}:</b> {v}</li>" for k, v in final_verdict.get('key_facts', {}).items()])}
            </ul>

            <h3>🧠 Explanation</h3>
            <p>{final_verdict.get('explanation')}</p>

            <h3>📋 Document Checklist</h3>
            <ul>
            {''.join([f"<li>{item}: {status}</li>" for item, status in checklist.items()])}
            </ul>
            """
            status = send_verification_email(user_email, "VisionFlow PECO Results", html)
            if status == 202:
                st.success("📧 Email sent successfully!")
            else:
                st.error(f"Email failed to send. Status: {status}")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")

    # 📌 Key Facts
    if "key_facts" in final_verdict:
        st.markdown("### 📌 Key Facts")
        for k, v in final_verdict["key_facts"].items():
            st.markdown(f"- **{k.replace('_', ' ').capitalize()}**: {v}")

    # ✅ Checklist
    st.subheader("📋 Document Checklist")
    for item, status in checklist.items():
        st.markdown(f"**{item}**: {status}")

    # 🖼️ Evidence
    st.subheader("📸 Visual Evidence")
    shown_pages = set(page_evidence.values())
    for res in results:
        if res["page"] in shown_pages and res.get("response"):
            st.markdown(f"### 📄 {res['source_file']} — Page {res['page']}")
            if "image" in res:
                st.image(res["image"], use_container_width=True)
            st.markdown(f"**Prompt:** {res['prompt']}")
            st.markdown(f"**Response:** {res['response']}")