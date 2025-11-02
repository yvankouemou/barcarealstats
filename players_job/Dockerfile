FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Recup_joueurs.py .

CMD ["python", "Recup_joueurs.py"]
