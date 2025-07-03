import os
import json
import base64
from datetime import datetime
from PIL import Image
from vision_core.vision_utils import ask_batch_vision
from vision_core.prompt_builder import generate_questions_from_intent
from vision_core.cross_reasoner import analyze_cross_document_consistency
from vision_core.response_aggregator import evaluate_results
import fitz  # PyMuPDF
import io
import logging


logging.basicConfig(
    filename="visionflow-debug.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def save_temp_file(file):
    os.makedirs("uploads", exist_ok=True)
    filename = f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
    with open(filename, "wb") as f:
        f.write(file.read())
    return filename


def convert_file_to_images(file_path):
    print("I'm in the convert file to images function")
    images = []
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
    else:
        images.append(Image.open(file_path))
    return images


def run_pipeline(intent, typed_files):
    print("I'm in run pipeline function in vision runner file")
    """
    intent: string
    typed_files: list of (UploadedFile, doc_type) tuples
    returns: full_trace, checklist, page_evidence, final_verdict
    """
    logging.debug(f"=== run_pipeline START intent={intent!r} ===")
    os.makedirs("outputs", exist_ok=True)
    full_trace = []
    requirements = []

    for file, doc_type in typed_files:
        logging.debug(f"[file] {file.name} as {doc_type}")
        # 1) save upload locally
        local_path = save_temp_file(file)

        # 2) initial questions for this doc_type
        questions = generate_questions_from_intent(intent, doc_type)
        print("here is the initial question for this doc type")
        print(questions)
        logging.debug(f"[prompts] {questions}")
        print("I'm about to execute requirements.extend(questions.copy())")
        requirements.extend(questions.copy())
        print("Did it. Just copy the questions in the requiments")
        print("Here's what in the requirements")
        print(requirements)

        # 3) convert to images
        print("I'm converting the images using convert file to images function ")
        images = convert_file_to_images(local_path)
        print("Just finished converting images")

        # 4) loop pages
        for page_num, img in enumerate(images, start=1):
            if not questions:
                logging.debug(f"[pages] all answered; breaking at page {page_num}")
                break

            logging.debug(f"[batch] page {page_num}, questions={questions}")
            try:
                print("I'm sending the image one page of image to vision AI for answering")
                answers = ask_batch_vision(img, questions)
                print("Just got the answers back from vision AI")
                print(answers)
                logging.debug(f"[batch answers] {answers}")
            except Exception as e:
                print("I'm in the exception of the try bloc which send image to vision AI")
                print("Which mean we were not able to send the questions and images to vision AI")
                logging.error(f"[batch ask] page {page_num} error: {e}", exc_info=True)
                # record an error for each question
                for q in questions:
                    print("I'm in the for q in questions bloc to append to full trace")
                    full_trace.append({
                        "source_file": file.name,
                        "doc_type":   doc_type,
                        "page":       page_num,
                        "prompt":     q,
                        "response":   f"ERROR: {e}",
                        "image":      img,
                    })
                    print("I'm printing full trace")
                    print(full_trace)
                # skip to next page
                print("I don't know what happen but I'm in the except bloc skiping to the next page")
                continue

            # 5) record each Q→A, drop answered ones
            print("I'am about to record all Q and A, and drop those that has been answered")
            NEG_KEYWORDS = [
                "not visible", "no visible", "cannot determine",
                "not present", "none", "n/a"
            ]
            for q, a in answers.items():
                full_trace.append({
                    "source_file": file.name,
                    "doc_type":   doc_type,
                    "page":       page_num,
                    "prompt":     q,
                    "response":   a,
                    "image":      img,
                })
                print("I need to see what's currently in full trace to be able to to see those questions that has been ansewred")
                print(full_trace)
                # only drop if the answer is non-empty AND *doesn't* contain a negative signal
                content = a.strip()
                lower = content.lower()
                is_negative = any(neg in lower for neg in NEG_KEYWORDS)
                if content and not is_negative:
                    logging.debug(f"[answered] {q!r} → removing from queue")
                    print("I'm removing the question that has been answered")
                    print("Here's what question contain before removing")
                    print(questions)
                    questions.remove(q)
                    print("Just removed a question that has been answered")
                    print("here are the remaining questions to send")
                    print(questions)

    # 6) final aggregation
    logging.debug(f"[aggregate] full_trace length={len(full_trace)}, requirements={requirements}")
    print("I'm about to call checklist, page_evidence = evaluate_results(full_trace, requirements)")
    checklist, page_evidence = evaluate_results(full_trace, requirements)
    print("did it I just called evaluate results from response aggregator file")
    print("Now I will print checklist and page evidence that resulted")
    print("Checklist:")
    print(checklist)
    print("Page Evidence:")
    print(page_evidence)
    print("I'm about to call final_verdict = analyze_cross_document_consistency(full_trace, checklist, intent)")
    final_verdict = analyze_cross_document_consistency(full_trace, checklist, intent)
    print("Just ran analyze cross document consistency from the cross reasonner file")
    print("And this is the final verdict that resulted from it")
    print("Final verdict:")
    print(final_verdict)
    logging.debug(f"[results] checklist={checklist}, page_evidence={page_evidence}, verdict={final_verdict}")

    logging.debug("=== run_pipeline END ===\n")
    return full_trace, checklist, page_evidence, final_verdict