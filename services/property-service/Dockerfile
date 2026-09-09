FROM python:3.12-slim
WORKDIR /app
COPY property-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY seed_loader.py ./seed_loader.py
COPY seed ./seed
WORKDIR /app/property-service
COPY property-service/app.py ./app.py
EXPOSE 8100
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8100"]
