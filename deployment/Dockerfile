FROM python:3.11-slim
WORKDIR /app
COPY deployment/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY deployment/api.py /app/api.py
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
