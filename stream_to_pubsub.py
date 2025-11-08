import os
import time
import json
import requests
from datetime import date
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

def stream_to_pubsub():
    api_base = os.getenv("API_URL")
    api_key = os.getenv("FOOTBALL_API_KEY")
    team_ids = os.getenv("TEAM_IDS", "")
    poll_interval = int(os.getenv("POLL_INTERVAL", "5"))
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    topic_id = os.getenv("PUBSUB_TOPIC")
    project_id = os.getenv("GCP_PROJECT")

    # Année et date du jour
    season = date.today().year
    today = date.today().isoformat()

    # Authentification GCP
    credentials = service_account.Credentials.from_service_account_file(creds_path)
    publisher = pubsub_v1.PublisherClient(credentials=credentials)
    topic_path = publisher.topic_path(project_id, topic_id)

    headers = {"x-apisports-key": api_key}

    print(f"Streaming des données {today}, saison {season}...")

    while True:
        for team_id in team_ids.split(","):
            team_id = team_id.strip()
            if not team_id:
                continue

            api_url = f"{api_base}fixtures?team={team_id}&season={season}&date={today}"
            try:
                response = requests.get(api_url, headers=headers, timeout=20)
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))

                publisher.publish(topic_path, json.dumps(data).encode("utf-8"))
                print(f"✓ Données publiées pour l'équipe {team_id} à {time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"❌ Erreur pour l'équipe {team_id}: {e}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    stream_to_pubsub()
