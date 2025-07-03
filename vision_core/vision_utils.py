import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import fitz  # PyMuPDF
import json
import io

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_image_from_pdf(pdf_path, page_number, output_path=None):
    """
    Extract a specific page from a PDF and save it as an image.
    """
    doc = fitz.open(pdf_path)
    if page_number < 1 or page_number > len(doc):
        raise ValueError("Invalid page number")
    
    page = doc.load_page(page_number - 1)
    pix = page.get_pixmap(dpi=300)
    if not output_path:
        output_path = f"outputs/page_{page_number}.png"
    pix.save(output_path)
    return output_path


def extract_preview_text(uploaded_file, max_pages=2):
    """
    Extracts preview text from a PDF for classification.
    Falls back to raw binary text if parsing fails.
    """
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        preview = ""
        for i in range(min(max_pages, len(doc))):
            preview += doc[i].get_text()
        uploaded_file.seek(0)  # Reset stream for reuse
        return preview.strip()
    except Exception:
        uploaded_file.seek(0)
        return uploaded_file.read(1500).decode(errors="ignore").strip()
    
def ask_batch_vision(pil_image, questions: list[str]) -> dict[str,str]:
    """
    Send one OpenAI chat request for all remaining questions on a single page.
    Returns a map from each question to its answer.
    """
    # 1) Down-sample & recompress as JPEG to reduce token‐cost:
    #    • max size ~800×600
    #    • JPEG quality ~30
    pil_image = pil_image.convert("RGB")
    pil_image.thumbnail((800, 600), Image.LANCZOS)

    print("I'm in the ask batch vision function in the vision utils file")

    print("I'm about to run buffered = io.BytesIO()")
    buffered = io.BytesIO()
    print("Done")

    print("I'm about to run pil_image.save(buffered, format='JPEG')")
    pil_image.save(buffered, format="JPEG", quality=30)
    print("Done")

    print("I'm about to run img_b64 = base64.b64encode(buffered.getvalue()).decode()")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    print("Done")

    # Build a single prompt that enumerates all questions
    print("I will now Build a single prompt that enumerates all questions")
    q_block = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    system = {
        "role": "system",
        "content": (
            "You are a document–vision assistant. You will be shown a page image "
            "encoded in base64 JPEG format, followed by a list of numbered questions.  "
            "For each question:\n"
            "  • If you see clear, affirmative evidence in the image that answers the question, return exactly that information.\n"
            "  • If you do *not* see such evidence, return an empty string (\"\").\n"
            "Do not include any negative phrasing.  "
            "Always output exactly one JSON object mapping each question number (as a string) to its answer.  "
            "For example: {\"1\": \"Alice Smith\", \"2\": \"\"}."
        )
    }
    user = {
        "role": "user",
        "content": (
            f"Here is a page image (base64 JPEG):\n{img_b64}\n\n"
            "Please answer the following questions about it:\n"
            f"{q_block}"
        )
    }

    print("I'm calling chat completion to send the image and questions to gpt NOW")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[system, user],
        temperature=0.0,
        max_tokens=5000,
    )
    print("Did it")

    # parse the JSON blob in the assistant’s reply
    print("I'm passing the response that I got from GPT vision AI")
    text = resp.choices[0].message.content.strip()
    print("I'm printing what comes from GPT VisionAI")
    print(text)

    try:
        mapping = json.loads(text)
        print("I'm printing the mapped version")
        print(mapping)
    except json.JSONDecodeError:
        # fallback: split by lines “1. answer”
        mapping = {}
        for line in text.splitlines():
            if "." in line:
                idx, ans = line.split(".", 1)
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(questions):
                    mapping[idx] = ans.strip()
                    print("This is the mapping that the script did after spliting the line")
                    print(mapping)
        # no early return here

    # remap numeric keys back to question text
    results: dict[str, str] = {}
    for i, q in enumerate(questions, start=1):
        results[q] = mapping.get(str(i), "").strip()

    return results