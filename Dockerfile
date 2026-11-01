FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pump_monitoring ./pump_monitoring
COPY models ./models
COPY tests ./tests
RUN mkdir -p /app/data
EXPOSE 8001
CMD ["uvicorn", "pump_monitoring.api:app", "--host", "0.0.0.0", "--port", "8001"]
