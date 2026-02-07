FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY backend/ backend/
COPY docs/ docs/
COPY db/ db/

WORKDIR /app/backend

CMD sh -c "python ingest.py && uvicorn main:app --host 0.0.0.0 --port 8000"
