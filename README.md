# ⚽📊 BarcaRealStats

> **Analyse en temps réel des performances du Real Madrid et du FC Barcelone — propulsée par la data et l’IA !**

---

## 🧠 Description du projet

**BarcaRealStats** est une plateforme d’analyse de données en temps réel dédiée aux performances du **Real Madrid** et du **FC Barcelone**, ainsi qu’à leurs **joueurs**.  
Le projet exploite les données de **l’API-Football** pour suivre, transformer et visualiser des informations sportives précises et actualisées.

Grâce à une **architecture de données moderne** (ELT + modèle en médaillon), la plateforme permet de :
- 🔹 **Extraire** les données via des jobs automatisés (équipes & joueurs)  
- 🔹 **Stocker** les informations dans **BigQuery**  
- 🔹 **Transformer** les données avec **DBT**  
- 🔹 **Visualiser** les statistiques via **Looker**

---

## 🤖 Automatisation & Intelligence

💬 Lors des événements clés (buts, cartons, changements, etc.), le système déclenche automatiquement :
- Une génération de message grâce à **l’API Gemini (IA)**  
- Une publication en direct sur **X (Twitter)**  

👉 Cela assure une **communication instantanée**, enrichie par l’intelligence artificielle, directement connectée au flux de match.

---

## 🧩 Architecture technique

🧱 Le projet repose sur plusieurs composants intégrés :

| Composant | Description |
|------------|-------------|
| **API-Football** | Source principale des données sportives |
| **BigQuery** | Entrepôt de données pour le stockage et les analyses |
| **DBT** | Transformation des données (modèle en médaillon) |
| **Looker** | Visualisation et reporting en temps réel |
| **Gemini API** | Génération de messages automatisés |
| **X (Twitter) API** | Publication automatique lors des événements |
| **Pub/Sub + Cloud Run** | Orchestration des messages et des flux |
| **Docker** | Conteneurisation des jobs d’extraction |
| **Github** | Suivi et supervision technique |

---
