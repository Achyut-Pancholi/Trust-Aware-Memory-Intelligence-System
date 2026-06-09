# Trust-Aware Memory Intelligence System

A multi-agent memory intelligence system designed to ingest noisy, conflicting, evolving claims and convert them into a trusted memory store. 

This is not a simple RAG or chatbot. It is a continuous intelligence loop handling memory evolution, trust scoring, provenance tracking, and explainability.

## Architecture

The system utilizes:
- **FastAPI** for backend ingestion and REST APIs.
- **LangGraph** & **Groq (Llama 3.3 70B)** for a multi-agent validation workflow (Extraction, Verification, Contradiction Detection, Trust Scoring, Curator).
- **SQLite + SQLAlchemy ORM** for persistent storage of memories and immutable change logs.
- **Streamlit** for the frontend dashboard, visualizing trust evolution and provenance via **Plotly**, **PyVis**, and **NetworkX**.

## Setup & Run Locally

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your `GROQ_API_KEY`:
   ```bash
   cp .env.example .env
   ```

3. Run the Backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

4. Run the Frontend:
   ```bash
   streamlit run frontend/app.py
   ```

## Development Status
*Project structure initialized. Core database components in development.*
