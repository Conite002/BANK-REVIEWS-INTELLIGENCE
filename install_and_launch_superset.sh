#!/bin/bash

# --------------------------------------------------------------------------
# Script to Install and Launch Apache Superset
# --------------------------------------------------------------------------

# Define environment variables
export SUPSET_ENV_PATH="$HOME/superset_env"
export SUPSET_PORT=8090
export ADMIN_USERNAME=admin
export ADMIN_FIRSTNAME=admin
export ADMIN_LASTNAME=admin
export ADMIN_EMAIL=admin@example.com
export ADMIN_PASSWORD=admin

# Generate dynamic secrets using tr
export SECRET_KEY="$(tr -dc A-Za-z0-9 </dev/urandom | head -c 42)"
export SUPERSET_SECRET_KEY="$(tr -dc A-Za-z0-9 </dev/urandom | head -c 42)"
export FLASK_APP=superset

# Print environment variables for debugging
echo "SECRET_KEY=${SECRET_KEY}"
echo "SUPERSET_SECRET_KEY=${SUPERSET_SECRET_KEY}"

# Create superset_config.py with the secrets in the current directory
cat <<EOL > superset_config.py
import os

# Secret key for Flask
SECRET_KEY = '${SECRET_KEY}'
SUPERSET_SECRET_KEY = '${SUPERSET_SECRET_KEY}'
EOL

# Print the content of the config file for debugging
cat superset_config.py

# Log function for output messages
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Update and install dependencies
log "Updating system and installing dependencies"
sudo apt-get update -y
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev python3-pip python3-venv

# Create virtual environment
log "Creating virtual environment at $SUPSET_ENV_PATH"
python3 -m venv "$SUPSET_ENV_PATH"
source "$SUPSET_ENV_PATH/bin/activate"

# Upgrade pip
log "Upgrading pip"
pip install --upgrade pip

# Install Apache Superset
log "Installing Apache Superset"
pip install apache-superset
pip install psycopg2-binary


# Initialize Superset and start the server
superset db upgrade
superset fab create-admin --username admin --firstname admin --lastname admin --email admin@example.com --password admin
superset load_examples
superset init
superset run -p "$SUPSET_PORT" --with-threads --reload --debugger &


log "Superset installation and initialization complete"
# Start Superset
log "Starting Superset server on port $SUPSET_PORT"
superset run -p "$SUPSET_PORT" --with-threads --reload --debugger

log "Run this to see address of postgres container : docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres_db"