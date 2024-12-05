from utils.clients import search_client
from azure.search.documents.models import QueryType

def query_search(query):
    """Query Azure Cognitive Search with result limiting and debug logging."""
    results = search_client.search(
        query,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="semantic-config",
        top=5,  # Limit results to reduce context size
        select="content,content_summary,type,primary_business_name"  # Explicitly select fields
    )
    # Add debug logging
    print("Search Results:")
    results_list = list(results)
    for result in results_list:
        print(f"Type: {result['type']}")
        print(f"Primary Business Name: {result['primary_business_name']}")
        print(f"Content Summary: {result['content_summary'][:200]}...")  # Print first 200 chars of summary
        print("---")
    return results_list