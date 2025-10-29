import os
import json
from datetime import datetime
import requests
#from google.cloud import bigquery

# Chargement des variables d’environnement
API_KEY = os.getenv("FOOTBALL_API_KEY")
TEAM_IDS = os.getenv("TEAM_IDS", "").split(",")  # utilise la virgule pour séparer les équipes
YEAR = 2021 #datetime.now().year

#DATASET = os.getenv("BQ_DATASET")
#TABLE = os.getenv("BQ_PLAYERS_TABLE")

def get_team_players(api_key, teams, season):
    """Récupère les joueurs pour chaque équipe et retourne une liste de joueurs normalisée"""
    headers = {'x-apisports-key': api_key}
    players_data = []

    for team_id in teams:
        url = f"https://v3.football.api-sports.io/players?season={season}&team={team_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f" Erreur API pour l’équipe {team_id}: {response.text}")
            continue

        result = response.json()
        if not result.get("response"):
            print(f" Équipe {team_id}: aucune donnée")
            continue

        nb_players = len(result["response"])
        print(f"Équipe {team_id}: {nb_players} joueurs récupérés (saison {season})")

        for item in result["response"]:
            player = item.get("player", {})
            stats = item.get("statistics", [{}])[0]

            players_data.append({
                "player_id": player.get("id"),
                "name": player.get("name"),
                "firstname": player.get("firstname"),
                "lastname": player.get("lastname"),
                "age": player.get("age"),
                "nationality": player.get("nationality"),
                "team_id": stats.get("team", {}).get("id"),
                "team_name": stats.get("team", {}).get("name"),
                "season": season
            })

    return players_data

# def insert_into_bigquery(players_data):
#     """Insère la liste des joueurs dans BigQuery"""
#     if not players_data:
#         print("Aucune donnée à insérer.")
#         return

#     client = bigquery.Client()
#     table_id = f"{client.project}.{DATASET}.{TABLE}"

#     errors = client.insert_rows_json(table_id, players_data)
#     if errors:
#         print(f"Erreurs lors de l’insertion BigQuery: {errors}")
#     else:
#         print(f"{len(players_data)} joueurs insérés avec succès dans {table_id}")

def save_to_json(players_data, filename="players.json"):
    """Sauvegarde locale (optionnelle)"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(players_data, f, indent=2, ensure_ascii=False)
    print(f"Données sauvegardées localement dans {filename}")

def main():
    print(f" Récupération des joueurs (saison {YEAR})")
    players = get_team_players(API_KEY, TEAM_IDS, YEAR)
    save_to_json(players)
    #insert_into_bigquery(players)

if __name__ == "__main__":
    main()