FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (cached layer - only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code separately (this layer rebuilds on code changes only)
COPY app.py .
COPY templates/ templates/

RUN mkdir -p /app/logs

EXPOSE 5000

CMD ["python", "app.py"]
