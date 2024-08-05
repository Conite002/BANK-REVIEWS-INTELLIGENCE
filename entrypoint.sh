#!/bin/bash

# --------------------------------------------------------------------------
# PostgreSQL Connection Check
# --------------------------------------------------------------------------
set -e

log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log "Démarrage de la vérification de connexion PostgreSQL"

# Attendre que PostgreSQL soit prêt
until pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER}; do
  log "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo -e "\033[92mPostgreSQL is up - connection successful\033[0m"

# Pulling ollama
# ollama pull llama3.1
# Wait for Ollama
until curl -s http://ollama:11434/; do
  echo "Waiting for Ollama..."
  sleep 2
done

echo -e "\033[32m Ollama is up - connection successful!\033[0m"




# Lancer l'application principale (ou tout autre processus)
exec python3 /app/src/main.py
