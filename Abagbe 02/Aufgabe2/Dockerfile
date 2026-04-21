FROM python:3.11-slim

# Installiere ZeroMQ Abhängigkeit
RUN pip install pyzmq

WORKDIR /app
COPY . .

# Standardmäßig führen wir das Client-Skript aus
CMD ["python", "client.py"]