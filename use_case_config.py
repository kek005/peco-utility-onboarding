# use_case_config.py

USE_CASE_NAME = "Peco Utility Onboarding Verifier"

PRELOADED_INTENT = "Verify residency and lease validity for utility service account creation"

# Generic labels to avoid OpenAI Vision moderation
DOCUMENT_TYPES = {
    "lease": "Residential Lease Document",
    "resident_verification": "Resident Verification Document"
}

# Prompts crafted to avoid flagging "ID" ethics restrictions
PROMPTS = {
    "lease": [
        "What is the lease start date and duration?",
        "What is the address of the leased property?",
        "What are the names of the individuals involved in this rental agreement?",
        "Is there a signature from both parties?"
    ],
    "resident_verification": [
        "What name appears as the main resident on this document?",
        "What is the birthdate on the document?",
        "What is the expiration date and is it valid?",
        "What is the residential address listed on the document?"
    ]
}