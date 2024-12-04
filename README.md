# Genai_AzurePDFChatbot

This project extracts content from PDF files, uploads it to Azure Cognitive Search, and allows querying using a Streamlit app.

## Setup

1. Clone the repository.
   ```sh
   git clone https://github.com/yourusername/Genai_AzurePDFChatbot.git
   cd Genai_AzurePDFChatbot
   ```

2. Create a virtual environment and activate it.
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r backend/requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the `backend` directory with the following content:
   ```env
   SEARCH_SERVICE_NAME=your_search_service_name
   SEARCH_INDEX_NAME=your_search_index_name
   SEARCH_API_KEY=your_search_api_key
   AZURE_OPENAI_ENDPOINT=your_openai_endpoint
   AZURE_OPENAI_KEY=your_openai_key
   DEPLOYMENT_NAME=your_deployment_name
   ```

5. Run the Streamlit app:
   ```sh
   streamlit run backend/app.py
   ```

6. Access the app in your browser at [http://localhost:8501](http://localhost:8501).

## Usage

1. Upload a PDF file using the Streamlit app.
2. The content of the PDF will be extracted and uploaded to Azure Cognitive Search.
3. You can query the extracted content using the search functionality in the app.

## Development

### Testing

1. To test the PDF extraction logic, you can use the provided Jupyter notebook:
   ```sh
   jupyter notebook backend/test.ipynb
   ```

2. To run unit tests, use the following command:
   ```sh
   pytest
   ```

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License.