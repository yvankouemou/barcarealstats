#!/usr/bin/env bash
set -euo pipefail

# Emplacement profile dbt
mkdir -p /root/.dbt

# Variables attendues :

DBT_PROJECT_ID="${DBT_PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-}}"
DBT_DATASET="${DBT_DATASET:-football_data_clean}"
DBT_LOCATION="${DBT_LOCATION:-europe-west9}"
DBT_PROFILE_NAME="${DBT_PROFILE_NAME:-dbt_brs}"
DBT_TARGET="${DBT_TARGET:-prod}"
DBT_KEYFILE_PATH="${DBT_KEYFILE_PATH:-/secrets/sa-key.json}"
DBT_CMD="${DBT_CMD:-dbt run}"



# Génération du profiles.yml dynamique (BigQuery)
cat > /root/.dbt/profiles.yml <<EOF
${DBT_PROFILE_NAME}:
  target: ${DBT_TARGET}
  outputs:
    ${DBT_TARGET}:
      type: bigquery
      method: service-account
      project: ${DBT_PROJECT_ID}
      dataset: ${DBT_DATASET}
      location: ${DBT_LOCATION}
      threads: 1
      timeout_seconds: 300
      priority: interactive
EOF

echo "Generated ~/.dbt/profiles.yml:"
cat /root/.dbt/profiles.yml

# Aller dans le répertoire dbt (où se trouve dbt_project.yml)
cd /app

# Avant d'exécuter, installer les dépendances dbt si nécessaire
# (dbt deps si tu utilises des packages)
if [ -f packages.yml ]; then
  echo "Running dbt deps..."
  dbt deps
fi

# Si la variable DBT_CMD est présente, exécuter la commande
echo "Running DBT command: ${DBT_CMD}"
# utiliser 'exec' pour remplacer le shell par le process dbt (bon pour signaux)
exec ${DBT_CMD}
