import os
import json
import time
from pdfplumber import open as pdf_open
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)
from azure.search.documents.models import QueryType
from utils.helper_fn import generate_summary
from utils.clients import search_client, index_client

SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")

def index_exists(index_name):
    """Check if the search index exists."""
    try:
        index_client.get_index(index_name)
        return True
    except:
        return False

def create_search_index():
    """Create search index if it doesn't exist"""
    if index_exists(SEARCH_INDEX_NAME):
        print(f"Index {SEARCH_INDEX_NAME} already exists.")
        return

    try:
        # Define the index fields
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="content_summary", type=SearchFieldDataType.String),
            SimpleField(name="type", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="page_num", type=SearchFieldDataType.Int32, filterable=True)  # Add page_num field
        ]
        
        # Create semantic configuration
        semantic_config = SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content_summary")]
            )
        )
        
        # Create the index with semantic configuration
        index = SearchIndex(
            name=SEARCH_INDEX_NAME,
            fields=fields,
            semantic_search=SemanticSearch(
                configurations=[semantic_config]
            )
        )
        
        # Create new index
        result = index_client.create_index(index)
        print(f"Created index {result.name}")
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        raise e

def extract_pdf_content(file_path):
    """Extract structured content from a PDF file, including text and tables."""
    content = []
    with pdf_open(file_path) as pdf:
        # Store all pages content for analysis
        pages_content = {}
        
        # First pass - extract all raw content
        for page_num, page in enumerate(pdf.pages):
            current_content = page.extract_text()
            pages_content[page_num] = current_content
        
        # Second pass - calculate diff content
        for page_num in range(len(pages_content)):
            if page_num == 0:
                # First page - use as is
                unique_content = pages_content[page_num]
            else:
                # Find unique content by removing previous page content
                prev_content = pages_content[page_num - 1]
                current_content = pages_content[page_num]
                
                # Split into lines for better comparison
                prev_lines = set(prev_content.split('\n'))
                current_lines = current_content.split('\n')
                
                # Keep only lines that weren't in previous page
                unique_lines = [line for line in current_lines if line not in prev_lines]
                unique_content = '\n'.join(unique_lines)
            
            if unique_content.strip():  # Only add non-empty content
                content.append({"type": "text", "data": unique_content, "page_num": page_num})
            
            # Extract tables
            tables = pdf.pages[page_num].extract_tables()
            for table_num, table in enumerate(tables):
                if table and len(table) > 1 and len(table[0]) > 1:
                    content.append({"type": "table", "data": table, "page_num": page_num, "table_num": table_num})
    
    return content

def sanitize_file_name(file_name):
    """Sanitize the file name to ensure it only contains valid characters for the document key."""
    return ''.join(c if c.isalnum() or c in ['_', '-', '='] else '_' for c in file_name)

def upload_to_search(documents, file_name):
    """Upload documents to Azure Cognitive Search with proper formatting"""
    sanitized_file_name = sanitize_file_name(file_name)
    # Format documents for Azure Search
    formatted_docs = []
    for i, doc in enumerate(documents):
        content = json.dumps(doc)
        summary = generate_summary(content)
        doc_id = f"{sanitized_file_name}_{doc['page_num']}_{i}"  # Ensure unique ID for each piece of content
        formatted_doc = {
            "id": doc_id,  # Required unique ID
            "file_name": file_name,  # Store the original file name
            "content": content,  # Store original document as JSON string
            "content_summary": summary,  # Store generated summary
            "type": doc["type"],  # Keep type for filtering
            "page_num": doc["page_num"]  # Store page number for reference
        }
        formatted_docs.append(formatted_doc)
        print(f"Formatted document ID: {doc_id}, Type: {doc['type']}, Page: {doc['page_num']}")  # Debug log
    print(f"formatted_doc: {formatted_doc}")  # Debug log
    try:
        # Upload documents in batches of 1000
        batch_size = 1000
        for i in range(0, len(formatted_docs), batch_size):
            batch = formatted_docs[i:i + batch_size]
            result = search_client.upload_documents(documents=batch)
            print(f"Uploaded batch {i//batch_size + 1}, Success: {result[0].succeeded}")
    except Exception as e:
        print(f"Error uploading documents: {str(e)}")

def check_duplicate(file_name):
    """Check if a file with the same name already exists in the index."""
    results = search_client.search(
        search_text=file_name,
        filter=f"file_name eq '{file_name}'",
        query_type=QueryType.FULL
    )
    return len(list(results)) > 0

def preprocessing(pdf_path):
    """Preprocess the PDF content and upload to Azure Cognitive Search."""
    file_name = os.path.basename(pdf_path)
    
    # Step 1: Check for duplicates
    if check_duplicate(file_name):
        print(f"File {file_name} already exists in the index. Skipping upload.")
        return
    
    # Step 2: Create search index
    create_search_index()
    
    # Step 3: Extract content from the PDF
    extracted_content = extract_pdf_content(pdf_path)
    print(f"Extracted content: {extracted_content}")  # Debug log
    
    # Step 4: Upload extracted content to Azure Cognitive Search
    upload_to_search(extracted_content, file_name)
    print(f"Uploaded content for file: {file_name}")  # Debug log