from typing import Any
from constants import *
import streamlit as st


class StreamlitSecretsHelper:
    @staticmethod
    def get_azure_openai_api_key() -> str:
        return StreamlitSecretsHelper.get_secret(AZURE_OPENAI_API_KEY)
    
    @staticmethod
    def get_azure_openai_endpoint() -> str:
        return StreamlitSecretsHelper.get_secret(AZURE_OPENAI_ENDPOINT)
    
    @staticmethod
    def get_azure_openai_api_version() -> str:
        return StreamlitSecretsHelper.get_secret(AZURE_OPENAI_API_VERSION)

    @staticmethod
    def get_azure_openai_model() -> str:
        return StreamlitSecretsHelper.get_secret(AZURE_OPENAI_API_MODEL)
    
    @staticmethod
    def get_vector_store_id_list() -> list[str]:
        csv_string = StreamlitSecretsHelper.get_secret(VECTOR_STORE_ID_LIST)
        return [item.strip() for item in csv_string.split(",") if item.strip()]

    @staticmethod
    def get_secret(name: str) -> Any:
        return st.secrets[name]