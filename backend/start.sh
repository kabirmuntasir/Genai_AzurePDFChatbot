# Run the Streamlit app
echo "Starting Streamlit app..."
streamlit run app.py --server.port ${PORT:-8000} --server.address 0.0.0.0