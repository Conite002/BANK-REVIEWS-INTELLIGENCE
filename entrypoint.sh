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
# until curl -s http://ollama:11434/; do
# until curl -s http://localhost:11434/; do
#   echo "Waiting for Ollama..."
#   sleep 2
# done

echo -e "\033[32m Ollama is up - connection successful!\033[0m"


# --------------------------------------------------------------------------
# Superset Initialization
# --------------------------------------------------------------------------
log "Initializing Superset"

# Generate dynamic secrets
export SECRET_KEY="$(openssl rand -base64 42)"
export SUPERSET_SECRET_KEY="$(openssl rand -base64 42)"
export FLASK_APP=superset 

# Initialize the database
superset db upgrade

# Create an admin user (you can customize these credentials)
superset fab create-admin --username admin --firstname admin --lastname admin --email admin@example.com --password admin

# Load some data to play with
superset load_examples

# Create default roles and permissions
superset init

log "Superset initialization complete"

# --------------------------------------------------------------------------
# Start Superset Server
# --------------------------------------------------------------------------
log "Starting Superset Server"
superset run -p 8088 --with-threads --reload --debugger &




# Lancer l'application principale (ou tout autre processus)
exec python3 /app/src/main.py
