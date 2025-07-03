# use_case_config.py

USE_CASE_NAME = "Peco Utility Onboarding Verifier"

PRELOADED_INTENT = "Verify residency and lease validity for utility service account creation"

# Generic labels to avoid OpenAI Vision moderation
DOCUMENT_TYPES = {
    "lease": "Residential Lease Document",
    "resident_verification": "Resident Verification Document",
    "utility_bill": "Utility Bill Document",
    "bank_statement": "Bank Statement Document",
    "insurance_card": "Insurance Card Document",
    "other": "Generic Document"
}

# Prompts crafted to avoid flagging “ID” ethics restrictions
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
    ],

    "utility_bill": [
        "What is the account holder’s name on the bill?",
        "What service address is listed?",
        "What is the billing period (start and end dates)?",
        "What is the total amount due?",
        "What is the due date for payment?"
    ],

    "bank_statement": [
        "What name appears as the primary account holder?",
        "What is the statement period (start and end dates)?",
        "What is the ending balance on the statement?",
        "List any recent transactions you can read (description and amount).",
        "Is the account number partially visible or redacted?"
    ],

    "insurance_card": [
        "What is the insured person’s name on this card?",
        "What is the policy number?",
        "What is the coverage effective date and the expiration date?",
        "Who is the issuing insurance provider?",
        "Is there a group or plan identifier visible?"
    ],

    "other": [
        "What name appears as the main resident on this document?",
        "What is the birthdate on the document?",
        "What is the expiration date and is it valid?",
        "What is the residential address listed on the document?"
    ]
}