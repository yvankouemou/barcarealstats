import os
import json
from datetime import datetime
import requests
from google.cloud import bigquery

# Variables d’environnement
API_KEY = os.getenv("FOOTBALL_API_KEY")
TEAM_IDS = os.getenv("TEAM_IDS", "").split(",")
LEAGUE_IDS = os.getenv("LEAGUE_IDS", "").split(",")
YEAR = 2021 #datetime.now().year
DATASET = os.getenv("BQ_DATASET")
TABLE = os.getenv("BQ_TEAMS_TABLE")


def get_team_statistics(team_id, league_id):
    """Récupère les statistiques d'une équipe pour une ligue donnée."""
    url = (
        f"https://v3.football.api-sports.io/teams/statistics"
        f"?season={YEAR}&team={team_id}&league={league_id}"
    )
    headers = {"x-apisports-key": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur récupération stats équipe {team_id}, ligue {league_id}: {response.text}")
        return None

    data = response.json()
    return data.get("response")


def insert_into_bigquery(data):
    """Insère les données brutes dans BigQuery."""
    if not data:
        print("Aucune donnée équipe à insérer.")
        return

    client = bigquery.Client()
    table_id = f"{client.project}.{DATASET}.{TABLE}"

    errors = client.insert_rows_json(table_id, data)
    if errors:
        print(f"Erreurs d'insertion BigQuery: {errors}")
    else:
        print(f"{len(data)} lignes insérées avec succès dans {table_id}.")


def main():
    """Récupère les statistiques de toutes les équipes pour toutes les ligues et les insère dans BigQuery."""
    print("Début de la récupération des statistiques d'équipes")
    all_team_stats = []

    for league_id in LEAGUE_IDS:
        for team_id in TEAM_IDS:
            print(f"Récupération stats pour équipe {team_id} - ligue {league_id}")
            stats = get_team_statistics(team_id, league_id)
            if stats:
                all_team_stats.append(stats)
                print(f"Données récupérées pour équipe {team_id} - ligue {league_id}")
            else:
                print(f"Aucune donnée pour équipe {team_id} - ligue {league_id}")

    print(f"Total d'entrées récupérées : {len(all_team_stats)}")

    if all_team_stats:
        insert_into_bigquery(all_team_stats)


if __name__ == "__main__":
    main()
