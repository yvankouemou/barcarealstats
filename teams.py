import requests
import json
from datetime import datetime

def get_team_players(api_key, teams, leagues):
    try:
        headers = {'x-apisports-key': api_key}
        data = {}
        season = "2021"  # ou datetime.now().year

        for league_id in leagues:
            data[str(league_id)] = {}
            for team_id in teams:
                url = (
                    f"https://v3.football.api-sports.io/teams/statistics"
                    f"?season={season}&team={team_id}&league={league_id}"
                )
                response = requests.get(url, headers=headers)
                result = response.json()
                data[str(league_id)][str(team_id)] = result

                # Log minimal, dans le même esprit
                if result.get('response'):
                    print(f"✓ Ligue {league_id} - Équipe {team_id}: stats récupérées (saison {season})")
                else:
                    print(f"✗ Ligue {league_id} - Équipe {team_id}: aucune donnée")

        with open('teams.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Données sauvegardées dans teams.json (saison {season})")
        return data

    except Exception as e:
        print(f"Erreur: {e}")
        return None


# Utilisation
API_KEY = "48383a3d0febd24e425c386fb0703b29"
get_team_players(API_KEY, [529, 541], [2, 140, 556, 667, 3, 143])
