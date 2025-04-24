from helpers import StreamlitSecretsHelper
from openai import AzureOpenAI
from utils import get_suggestions_from_csv
from pydantic import BaseModel



class AzureOpenAIClient:
    def __init__(self):
        self.api_key = StreamlitSecretsHelper.get_azure_openai_api_key()
        self.endpoint = StreamlitSecretsHelper.get_azure_openai_endpoint()
        self.api_version = StreamlitSecretsHelper.get_azure_openai_api_version()
        self.model = StreamlitSecretsHelper.get_azure_openai_model()
        self.azure_vector_store_id = StreamlitSecretsHelper.get_azure_vector_store_id()

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def get_response_for_query(self, query, previous_response_id):
        """
        Get the response for the given query using Azure OpenAI.
        """
        response = self.client.responses.create(
            model=self.model,
            input=query,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [self.azure_vector_store_id]
                }
            ],
            previous_response_id=previous_response_id,
        )
        return response
    
    def get_suggestions(self, query):
        """
        Get suggestions based on the query.
        """
        response = self.client.responses.parse(
            model=self.model,
            input= [
                {"role": "system", "content": "Give next 3 probable queries based on the provided user query in the structured format."},
                {"role": "user", "content": query}
            ],
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [self.azure_vector_store_id]
                }
            ],
            text_format=Suggestions
        )
        return response.output_parsed
    
class Suggestions(BaseModel):
    """
    Model for suggestions.
    """
    suggestion1: str
    suggestion2: str
    suggestion3: str