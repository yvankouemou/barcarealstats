import os
import time
import json
import random
import requests
from datetime import datetime
from google.cloud import pubsub_v1



API_TIMEOUT = int(os.getenv("API_TIMEOUT"))
POLL_INTERVAL_LIVE = int(os.getenv("POLL_INTERVAL_LIVE"))   # pendant un match
POLL_INTERVAL_IDLE = int(os.getenv("POLL_INTERVAL_IDLE")) # pas de match → 1h
# ENV
api_base = os.getenv("API_URL")
api_key = os.getenv("FOOTBALL_API_KEY")
topic_id = os.getenv("PUBSUB_TOPIC")
project_id = os.getenv("GCP_PROJECT")
team_ids = os.getenv("TEAM_IDS", "").split(",")


def get_fixtures_in_progress(api_base, api_key, team_ids):
    """Retourne la liste des fixtures en cours pour les équipes spécifiées."""
    headers = {"x-apisports-key": api_key}
    team_params = "&".join([f"team={tid}" for tid in team_ids])

    url = f"{api_base}fixtures?live=all&{team_params}"

    try:
        response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        print(f"[ERROR] get_fixtures_in_progress → {e}")
        return []


def get_fixture_events(api_base, api_key, fixture_id):
    """Récupère les événements d'un match."""
    headers = {"x-apisports-key": api_key}
    url = f"{api_base}fixtures/events?fixture={fixture_id}"

    try:
        r = requests.get(url, headers=headers, timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json().get("response", [])
    except Exception as e:
        print(f"[ERROR] get_fixture_events → fixture={fixture_id} → {e}")
        return []


def publish_to_pubsub(publisher, topic_path, message_dict):
    """Publication avec validation & sérialisation JSON."""
    try:
        data = json.dumps(message_dict).encode("utf-8")
        future = publisher.publish(topic_path, data)
        future.result(timeout=8)
        print(f"[PUB] {message_dict['fixture_id']} event sent.")
    except Exception as e:
        print(f"[ERROR] publish_to_pubsub → {e}")


def start_stream():
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    print("✅ Service real-time events démarré.")

    while True:
        fixtures_live = get_fixtures_in_progress(api_base, api_key, team_ids)

        if not fixtures_live:
            print("⏳ Aucun match en cours. Prochain scan dans 1 heure.")
            time.sleep(POLL_INTERVAL_IDLE)
            continue

        print(f"⚽ {len(fixtures_live)} match(s) en cours détectés.")

        for fixture in fixtures_live:
            fixture_id = fixture["fixture"]["id"]
            league = fixture["league"]["name"]

            events = get_fixture_events(api_base, api_key, fixture_id)

            #for ev in events:
            message = {
                "fixture_id": fixture_id,
                "league": league,
                "timestamp": datetime.utcnow().isoformat(),
                "event": events
            }
            publish_to_pubsub(publisher, topic_path, message)

        sleep_time = POLL_INTERVAL_LIVE + random.randint(0, 5)
        print(f"⏳ Attente {sleep_time}s avant la prochaine lecture…")
        time.sleep(sleep_time)


if __name__ == "__main__":
    start_stream()
