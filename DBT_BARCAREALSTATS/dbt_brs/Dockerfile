# DBT image for BigQuery
FROM python:3.11-slim

# Préparation de l'environnement
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie du projet dbt
COPY . /app

# Entrypoint qui va générer ~/.dbt/profiles.yml à partir des ENV
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Par défaut on lance dbt via l'entrypoint 
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["dbt", "run"]
