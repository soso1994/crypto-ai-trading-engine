FROM python:3.12-slim

WORKDIR /app
COPY services/ingest/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/ /app/services/

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "50", "services.ingest.app:app"]
