#!/bin/bash

# --------------------------------------------------------------------------
# PostgreSQL Connection Check
# --------------------------------------------------------------------------
set -e

log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log "Démarrage de la vérification de connexion PostgreSQL"

until pg_isready -h postgres_db -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo -e "\033[92mPostgreSQL is up - connection successful\033[0m"

# Pulling ollama
# ollama pull llama3.1
# Wait for Ollama
# until curl -s http://ollama:11434/; do
# until curl -s http://localhost:11434/; do
#   echo "Waiting for Ollama..."
#   sleep 2
# done

echo -e "\033[32m Ollama is up - connection successful!\033[0m"



# Lancer l'application principale (ou tout autre processus)
exec python3 /app/src/main.py
