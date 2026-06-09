FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Script to run both
RUN echo '#!/bin/bash\nuvicorn backend.main:app --host 0.0.0.0 --port 8000 &\nstreamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0\n' > start.sh
RUN chmod +x start.sh

CMD ["./start.sh"]
