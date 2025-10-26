import requests
import json
from datetime import datetime


def get_team_players(api_key, teams):
    try:
        headers = {'x-apisports-key': api_key}
        data = {}
        season = "2021"#datetime.now().year

        for team_id in teams:
            response = requests.get(
                f"https://v3.football.api-sports.io/players?season={season}&team={team_id}",
                headers=headers
            )
            result = response.json()
            data[team_id] = result

            if result['response']:
                nb_players = len(result['response'])
                print(f"✓ Équipe {team_id}: {nb_players} joueurs récupérés (saison {season})")
            else:
                print(f"✗ Équipe {team_id}: aucune donnée")

        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Données sauvegardées dans players.json (saison {season})")
        return data

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


# Utilisation
API_KEY = "48383a3d0febd24e425c386fb0703b29"
get_team_players(API_KEY, [529, 541])