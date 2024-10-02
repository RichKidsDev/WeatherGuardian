# Verwende ein offizielles Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die Anforderungen in das Image
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Quellcode in das Image
COPY . .

# Setze Umgebungsvariablen
ENV FLASK_APP=app.py

# Exponiere den Port, auf dem die Anwendung läuft
EXPOSE 5000

# Starte die Anwendung
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
