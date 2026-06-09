# Trust-Aware Memory Intelligence System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-00a393.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0+-FF4B4B.svg)](https://streamlit.io)

> **Welcome Judges!** If you are evaluating this project, please start with the **[Guide for Judges](#guide-for-judges)** section below.

Live URL : https://trust-aware-memory-intelligence-system-44.streamlit.app/

A multi-agent memory intelligence system designed to ingest noisy, conflicting, evolving claims and convert them into a trusted memory store. 

This is not a simple RAG or chatbot. It is a continuous intelligence loop handling memory evolution, trust scoring, provenance tracking, and explainability.

## 🚀 Guide for Judges

Right now, standard AI systems suffer from "blind trust"—they believe whatever text they ingest last. If you feed them conflicting information, they get confused. They have no concept of source reliability, contradictions, or memory evolution.

We built the **Trust-Aware Memory Intelligence System** to fix this. It acts like an AI brain with a built-in lie-detector. It filters, evaluates, and audits information before remembering it.

### How to Evaluate This Project

1. **Visit the Dashboard:** Look at the real-time system metrics.
2. **Interactive Playground:** 
   - Try submitting a claim: `"Startup A raised 5 Million"` (Source Reliability: 0.8). You'll see it gets `ACCEPTED`.
   - Submit a conflicting rumor: `"Startup A raised 8 Million"` (Source Reliability: 0.3). You'll see it gets `DOWNGRADED` or `REJECTED` because the existing memory is stronger.
   - Submit a highly reliable confirmation: `"Startup A raised 8 Million"` (Source Reliability: 0.95). You'll see the system dynamically `UPDATES` the memory, overwriting the $5M figure.
3. **Change Log:** Go to the Change Log tab to see the **immutable audit trail** of every decision the system just made. This solves the "Black Box" AI problem.
4. **Explainability Engine:** Open a memory detail page and read the natural language reasoning for *why* the system believes a fact.

### Core Architecture Components

Our multi-agent pipeline is orchestrated via **LangGraph**:

1. **Claim Extraction Agent:** Converts natural language text into JSON Triples `(Subject, Predicate, Object)`.
2. **Verification Agent:** Evaluates if a claim is logical, coherent, and verifiable.
3. **Contradiction Detection Agent:** Queries the Memory Store to see if the subject and predicate match existing entries but the object differs.
4. **Trust Scoring Agent:** Calculates a mathematical trust score based on Source Reliability x Verification Confidence.
5. **Memory Curator Agent:** The final judge that decides to `ACCEPT`, `REJECT`, `UPDATE`, `DOWNGRADE`, `MERGE`, or `FORGET` the memory.

For a detailed walkthrough, architecture diagrams, and our presentation deck, please see the `/submission_docs` folder.

---

## 🏗️ Architecture Stack

- **Backend:** FastAPI for asynchronous ingestion and REST APIs.
- **AI Orchestration:** LangGraph & Groq (Llama-3.1-8b) for lightning-fast multi-agent workflow execution.
- **Database:** SQLite + SQLAlchemy ORM for persistent storage of memories, provenance, and the immutable change log.
- **Frontend:** Streamlit for the dashboard, visualizing trust evolution and knowledge networks via Plotly, PyVis, and NetworkX.

---

## 🛠️ Local Setup & Installation

Follow these step-by-step instructions to run the full system locally.

### Prerequisites
- Python 3.10+
- A Groq API Key (get one at console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/Achyut-Pancholi/Trust-Aware-Memory-Intelligence-System.git
cd Trust-Aware-Memory-Intelligence-System
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and add your Groq API key:
```bash
# On Linux/macOS
cp .env.example .env
# On Windows
copy .env.example .env
```
Open `.env` in a text editor and set:
`GROQ_API_KEY=your_api_key_here`

### 4. Run the Backend API
Start the FastAPI server:
```bash
uvicorn backend.main:app --reload
```
*The backend will be available at `http://localhost:8000`. You can view the API docs at `http://localhost:8000/docs`.*

### 5. Run the Frontend Dashboard
Open a **new terminal window**, activate your virtual environment, and run:
```bash
streamlit run frontend/app.py
```
*The frontend will automatically open in your browser at `http://localhost:8501`.*

---

## 📁 Repository Structure

- `/backend`: FastAPI application, LangGraph multi-agent pipeline, and database models.
- `/frontend`: Streamlit application, pages, and UI components.
- `/submission_docs`: Architecture diagrams, slide decks, and presentation materials for hackathon judging.
