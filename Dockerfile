FROM python:3.12-slim
WORKDIR /opt/devpulse
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY devpulse ./devpulse
COPY dashboard ./dashboard
CMD ["python", "-m", "devpulse.cli", "--help"]
