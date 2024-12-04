import os
import json
import streamlit as st
from dotenv import load_dotenv
import preprocessing  # Import the preprocessing module
from utils.search import query_search
from utils.helper_fn import generate_answer

load_dotenv()

# Ensure the uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

def main():
    st.title("Financial PDF Content Extraction and Query")
    
    # Upload PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        pdf_path = os.path.join("uploads", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded file: {uploaded_file.name}")
        
        if st.button("Preprocess and Upload Content"):
            with st.spinner("Preprocessing the PDF content..."):
                st.text("Creating search index...")
                preprocessing.create_search_index()
                st.text("Extracting content from the PDF...")
                extracted_content = preprocessing.extract_pdf_content(pdf_path)
                st.text("Uploading extracted content to Azure Cognitive Search...")
                preprocessing.upload_to_search(extracted_content, uploaded_file.name)
                st.success("Ready for user query || Ask any question of the documents.")
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    user_query = st.text_input("Enter your query:", key="user_query", value="")
    
    if st.button("Get Answer"):
        # Step 4: Query Azure Cognitive Search
        search_results = query_search(user_query)
        
        # Step 5: Combine search results and generate a GPT answer
        context = "\n\n".join([doc["content_summary"] for doc in search_results if doc["type"] == "text"])
        tables = [json.loads(doc["content"])["data"] for doc in search_results if doc["type"] == "table"]
        prompt = f"Context: {context}\nTables: {tables}\n\nQuestion: {user_query}\n\nAnswer:"
        
        answer = generate_answer(prompt)
        
        # Add the question and answer to the conversation history
        st.session_state.conversation.append({"question": user_query, "answer": answer})
        
        # Clear the input field by resetting the key
        st.rerun()
    
    # Display the conversation history
    for entry in reversed(st.session_state.conversation):
        st.markdown(
            f'<div style="text-align: right; margin: 10px 0; padding: 10px; background-color: #e1ffc7; border-radius: 10px;">'
            f'<strong>Question:</strong> {entry["question"]}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="text-align: left; margin: 10px 0; padding: 10px; background-color: #f1f1f1; border-radius: 10px;">'
            f'<strong>Answer:</strong> {entry["answer"]}'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()