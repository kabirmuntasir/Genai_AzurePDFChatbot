import time
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from utils.clients import azure_openai_client

def generate_summary(content):
    """Generate summary using Azure OpenAI with retry logic for rate limiting."""
    prompt = f"Summarize the following content while preserving all original information and extracting any tabular data:\n\n{content}"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    max_retries = 5
    retry_delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = azure_openai_client.invoke(messages)
            return response.content
        except Exception as e:
            error_message = str(e)
            if "429" in error_message:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Error generating summary: {error_message}")
                return "Error: Could not generate summary."
    
    return "Error: Exceeded maximum retries due to rate limiting."

def generate_answer(prompt, max_tokens=64000):
    """Generate response using Azure OpenAI with context length management."""
    # Truncate prompt if too long (rough estimate: 4 chars per token)
    max_chars = max_tokens * 4
    if len(prompt) > max_chars:
        print(f"Truncating prompt from {len(prompt)} to {max_chars} characters")
        prompt = prompt[:max_chars] + "..."

    messages = [
        SystemMessage(content="You are a helpful assistant. Analyze the provided context and tables to answer questions about ownership and company information."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = azure_openai_client.invoke(messages)
        return response.content
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "Error: Could not generate answer due to context length limitations."