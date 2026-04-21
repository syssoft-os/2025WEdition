# Schlankes Python 3.12 Basis-Image
FROM python:3.12-slim

# Arbeitsverzeichnis im Container erstellen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Container starten und die Anwendung ausführen
CMD ["python", "santa/main.py"]