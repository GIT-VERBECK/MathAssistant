"""
Script de démarrage simplifié pour le backend
"""
import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )

