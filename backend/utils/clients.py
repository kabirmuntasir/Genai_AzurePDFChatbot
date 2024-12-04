import os
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Azure configurations
SEARCH_SERVICE_NAME = os.getenv("SEARCH_SERVICE_NAME")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

# Initialize Azure Cognitive Search client with proper credentials
search_client = SearchClient(
    endpoint=f"https://{SEARCH_SERVICE_NAME}.search.windows.net",
    index_name=SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_API_KEY)
)

# Initialize Azure Cognitive Search Index client
index_client = SearchIndexClient(
    endpoint=f"https://{SEARCH_SERVICE_NAME}.search.windows.net",
    credential=AzureKeyCredential(SEARCH_API_KEY)
)

# Initialize Azure OpenAI client
azure_openai_client = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=DEPLOYMENT_NAME,
    api_key=AZURE_OPENAI_KEY,
    api_version=os.getenv("OPENAI_API_VERSION")
)