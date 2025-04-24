# Streamlit Secrets Keys
AZURE_OPENAI_API_KEY = "azure_openai_api_key"
AZURE_OPENAI_ENDPOINT = "azure_openai_endpoint"
AZURE_OPENAI_API_VERSION = "azure_openai_api_version"
AZURE_OPENAI_API_MODEL = "azure_openai_api_model"
AZURE_VECTOR_STORE_ID = "azure_vector_store_id"

# Initial Constants for the Assistant
INITIAL_SUGGESTIONS = [
    "How do I set up my Zebra printer?",
    "How do I troubleshoot printing issues?",
    "How do I change the printer settings?",
]

INITIAL_MESSAGE = "Welcome to the Zebra Printer Assistant! How can I help you today?"

INITAL_MESSAGE_LIST = [
    {
        "role" : "assistant",
        "content" : INITIAL_MESSAGE,
    }
]