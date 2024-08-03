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

log "PostgreSQL is up - connection successful"

# Lancer l'application principale (ou tout autre processus)
exec python3 /app/src/main.py
