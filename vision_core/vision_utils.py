import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import fitz  # PyMuPDF

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt_vision(image: Image.Image, prompt: str) -> str:
    """
    Send a base64-encoded image and a prompt to GPT-4o Vision.
    Returns the model's text response.
    """
    buffered = image.convert("RGB")
    buffered.save("temp.png")
    with open("temp.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()


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