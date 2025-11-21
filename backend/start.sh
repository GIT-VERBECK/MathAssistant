#!/bin/bash
# Script de démarrage pour Render
# Ce script est utilisé par Render pour démarrer l'application FastAPI

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Démarrer l'application avec uvicorn
# Render fournit automatiquement la variable d'environnement $PORT
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-5000}

