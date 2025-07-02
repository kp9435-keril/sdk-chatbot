from helpers import StreamlitSecretsHelper
from openai import AzureOpenAI
from utils import get_suggestions_from_csv
from pydantic import BaseModel

class AzureOpenAIClient:

    SYSTEM_PROMPT = (
        "You are a helpful assistant for Zebra Technologies Printers. "
        "Answer the user's question directly and clearly. "
        "Do not mention any documents, sources, vector stores, or how you found the answer. "
        "Only provide the answer to the user's question."
    )

    def __init__(self):
        self.api_key = StreamlitSecretsHelper.get_azure_openai_api_key()
        self.endpoint = StreamlitSecretsHelper.get_azure_openai_endpoint()
        self.api_version = StreamlitSecretsHelper.get_azure_openai_api_version()
        self.model = StreamlitSecretsHelper.get_azure_openai_model()
        self.vector_store_ids = StreamlitSecretsHelper.get_vector_store_id_list()

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def get_response_for_query(self, query: str, previous_response_id: str = None):
        """
        Get the response for the given query using Azure OpenAI.
        """
        tools = [
            {
                "type": "file_search",
                "vector_store_ids": self.vector_store_ids
            }
        ]

        params = {
            "model": self.model,
            "input": query,
            "instructions": self.SYSTEM_PROMPT,
            "tools": tools,
        }
        if previous_response_id:
            params["previous_response_id"] = previous_response_id

        response = self.client.responses.create(**params)
        return response

    def get_suggestions(self, query: str):
        """
        Get suggestions based on the query.
        """
        tools = [
            {
                "type": "file_search",
                "vector_store_ids": self.vector_store_ids
            }
        ]
        return self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": "Give next 3 probable queries based on the provided user query."},
                {"role": "user",   "content": query}
            ],
            tools=tools,
            text_format=Suggestions
        ).output_parsed

class Suggestions(BaseModel):
    suggestion1: str
    suggestion2: str
    suggestion3: str