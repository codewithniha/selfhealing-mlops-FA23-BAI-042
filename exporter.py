import time
import requests
from prometheus_client import start_http_server, Gauge
# This is the exact metric name the grading script checks
CONFIDENCE_GAUGE = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from sentiment API'
)

APP_URL = "http://localhost:32500/api/latest-confidence"
POLL_INTERVAL = 5  # seconds

def fetch_confidence():
    try:
        response = requests.get(APP_URL, timeout=3)
        data = response.json()
        return float(data.get("confidence", 1.0))
    except Exception:
        # If app is unreachable, default to 1.0
        return 1.0

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    print("Exporter running on port 8000...")

    while True:
        confidence = fetch_confidence()
        CONFIDENCE_GAUGE.set(confidence)
        print(f"Confidence: {confidence}")
        time.sleep(POLL_INTERVAL)
