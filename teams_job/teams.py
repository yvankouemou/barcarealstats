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

#Equivalence des champs en chiffres de l'API avec les colonnes Bigquery
KEY_MAPPING = {
    "0-15": "m0_15",
    "16-30": "m16_30",
    "31-45": "m31_45",
    "46-60": "m46_60",
    "61-75": "m61_75",
    "76-90": "m76_90",
    "91-105": "m91_105",
    "106-120": "m106_120",
    "0.5": "u0_5",
    "1.5": "u1_5",
    "2.5": "u2_5",
    "3.5": "u3_5",
    "4.5": "u4_5",
}

def map_keys(obj):
    """
    Transforme récursivement les clés du JSON API en respectant
    le mapping vers le schéma BigQuery.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_key = KEY_MAPPING.get(k, k)  # remplace si présent dans le mapping
            new_obj[new_key] = map_keys(v)
        return new_obj
    elif isinstance(obj, list):
        return [map_keys(item) for item in obj]
    else:
        return obj
    
def save_to_json(team_stats, filename="teams_stats.json"):
    """Sauvegarde locale des statistiques d'équipes dans un fichier JSON."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(team_stats, f, indent=2, ensure_ascii=False)
        print(f" Données sauvegardées localement dans {filename}")
    except Exception as e:
        print(f" Erreur lors de la sauvegarde dans {filename} : {e}")


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
    raw_response = data.get("response")

    if not raw_response:
        return None
    # Nettoyage du JSON avant retour
    cleaned = map_keys(raw_response)
    return cleaned




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
        save_to_json(all_team_stats, "teams_stats.json")
        insert_into_bigquery(all_team_stats)


if __name__ == "__main__":
    main()
