FROM python:3.10-slim
WORKDIR /app

# Install CPU-only torch FIRST so pip sees 2.3.0 already satisfied
# and skips the massive CUDA download when requirements.txt is installed
RUN pip install --no-cache-dir torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/logs
EXPOSE 5000
CMD ["python", "app.py"]
