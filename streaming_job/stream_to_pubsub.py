import os
import json
import time
import threading
import requests
from datetime import datetime, timezone
from fastapi import FastAPI
import uvicorn
from google.cloud import pubsub_v1


API_BASE = os.getenv("API_URL")
API_KEY = os.getenv("FOOTBALL_API_KEY")
TEAM_IDS = os.getenv("TEAM_IDS", "").split(",")
POLL_DEFAULT = 1800  # 30 min(hors match)
SEASON = datetime.now().year

PROJECT_ID = os.getenv("GCP_PROJECT")
TOPIC_ID = os.getenv("PUBSUB_TOPIC")

app = FastAPI()

# Appel API

def api_get(endpoint, params=None, timeout=15, retries=3, backoff=2):
    headers = {"x-apisports-key": API_KEY}
    url = f"{API_BASE}{endpoint}"

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f" Erreur : l’appel API a échoué (tentative {attempt+1}/{retries}): {e}")
            time.sleep(backoff)
    print(" Erreur fatale : API inaccessible après plusieurs tentatives.")
    return None

# Récupérer le prochain match de l'équipe

def get_next_fixture(team_id):
    params = {"team": team_id, "season": SEASON}
    data = api_get("fixtures", params=params)
    if not data or "response" not in data:
        return None

    upcoming = []
    for fixture in data["response"]:
        dt = datetime.fromisoformat(fixture["fixture"]["date"].replace("Z", "+00:00"))
        if dt > datetime.now(timezone.utc):
            upcoming.append(dt)

    return min(upcoming) if upcoming else None

# Récupère les matchs en cours
def get_live_fixtures():
    data = api_get("fixtures", params={"live": "all"})
    if not data or "response" not in data:
        return []
    live = []
    for fixture in data["response"]:
        team_ids = [
            fixture["teams"]["home"]["id"],
            fixture["teams"]["away"]["id"]
        ]
        if any(str(tid) in TEAM_IDS for tid in team_ids):
            live.append(fixture)
    return live

#Récupère les événements d'un match
def get_fixture_events(fixture_id):
    return api_get("fixtures/events", params={"fixture": fixture_id})

# Calcul de l'intervalle de polling
def compute_poll_interval(next_match):
    now = datetime.now(timezone.utc)
    if not next_match:
        return 1800

    delta = next_match - now
    minutes = delta.total_seconds() / 60

    if minutes > 720:      # > 12h
        return 1800        # 30 min
    elif 60 < minutes <= 720:
        return 300         # 5 min
    elif 15 < minutes <= 60:
        return 60          # 1 min
    elif 0 < minutes <= 15:
        return 30          # 30 sec
    elif minutes <= 0:
        return 15          # live mode

    return 1800

# Configuration Pub/Sub
def pubsub_setup():
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    return publisher, topic_path


def publish_raw_event(publisher, topic_path, payload):
    publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
    print("Evénement publié.")

# Boucle de polling

def polling_loop():
    print("Polling football events…")

    publisher, topic_path = pubsub_setup()

    while True:
        print("Vérification du statut du match…")

        live_fixtures = get_live_fixtures()
        if live_fixtures:
            print("Match en cours → polling 15 sec")
            for fixture in live_fixtures:
                events = get_fixture_events(fixture["fixture"]["id"])
                if events:
                    publish_raw_event(publisher, topic_path, events)
            time.sleep(15)
            continue

        next_matches = [get_next_fixture(t) for t in TEAM_IDS]
        next_matches = [m for m in next_matches if m]

        if not next_matches:
            print("Aucun match → pause 30 min")
            time.sleep(1800)
            continue

        next_match = min(next_matches)
        poll_interval = compute_poll_interval(next_match)

        print(f"Prochain match : {next_match}")
        print(f"Prochain appel dans {poll_interval} sec")
        time.sleep(poll_interval)


# Endpoints FastAPI pour monitoring

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    return {"teams": TEAM_IDS, "project": PROJECT_ID, "topic": TOPIC_ID}

#  Démarage du thread de polling au lancement de l'application

@app.on_event("startup")
def start_background_thread():
    thread = threading.Thread(target=polling_loop, daemon=True)
    thread.start()


#  ENTRYPOINT

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
