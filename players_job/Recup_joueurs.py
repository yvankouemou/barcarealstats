import os
import json
from datetime import datetime
import requests
from google.cloud import bigquery

API_KEY = os.getenv("FOOTBALL_API_KEY")
TEAM_IDS = os.getenv("TEAM_IDS", "").split(",")  # utilise la virgule pour séparer les équipes
YEAR = 2021 #datetime.now().year
DATASET = os.getenv("BQ_DATASET")
TABLE = os.getenv("BQ_PLAYERS_TABLE")

def get_all_players(team_id):
    """Récupère tous les joueurs d'une équipe sur toutes les pages."""
    all_players = []
    page = 1

    while True:
        url = f"https://v3.football.api-sports.io/players?team={team_id}&season={YEAR}&page={page}"
        headers = {"x-apisports-key": API_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erreur récupération joueurs équipe {team_id}: {response.text}")
            break

        data = response.json()
        players = data.get("response", [])
        if not players:
            break

        all_players.extend(players)

        # Si on a atteint la dernière page, on sort
        paging = data.get("paging", {})
        if paging.get("current") == paging.get("total"):
            break

        page += 1

    return all_players

def save_to_json(players_data, filename="players.json"):
    """Sauvegarde locale (optionnelle)"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(players_data, f, indent=2, ensure_ascii=False)
    print(f"Données sauvegardées localement dans {filename}")

# def insert_into_bigquery(data):
#     """Insère les données brutes dans BigQuery."""
#     if not data:
#         print("Aucune donnée joueur à insérer.")
#         return

#     client = bigquery.Client()
#     table_id = f"{client.project}.{DATASET}.{TABLE}"

#     errors = client.insert_rows_json(table_id, data)
#     if errors:
#         print(f"Erreurs d'insertion BigQuery: {errors}")
#     else:
#         print(f"{len(data)} lignes insérées avec succès dans {table_id}.")


def main():
    """Récupère les données de toutes les équipes et les insère dans BigQuery."""
    print("Début de la récupération des données joueurs...")
    all_players_data = []

    for team_id in TEAM_IDS:
        print(f"--- Équipe {team_id} ---")
        players = get_all_players(team_id)
        save_to_json(players)
        all_players_data.extend(players)
        print(f"{len(players)} joueurs récupérés pour l'équipe {team_id}")

    # print(f"Total joueurs récupérés: {len(all_players_data)}")
    # insert_into_bigquery(all_players_data)


if __name__ == "__main__":
    main()


    # def save_to_json(players_data, filename="players.json"):
    # """Sauvegarde locale (optionnelle)"""
    # with open(filename, 'w', encoding='utf-8') as f:
    #     json.dump(players_data, f, indent=2, ensure_ascii=False)
    # print(f"Données sauvegardées localement dans {filename}")

    # save_to_json(players)