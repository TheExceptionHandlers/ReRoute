#!/bin/sh
echo "===> Starting FastAPI Backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

echo "===> Starting Streamlit Frontend on port 8080..."
streamlit run frontend/app.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true