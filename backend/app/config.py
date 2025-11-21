"""
Configuration de l'application
Gère les variables d'environnement
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de l'application"""
    
    # API Keys
    # Mathpix (optionnel - si non configuré, utilise OpenAI Vision)
    MATHPIX_APP_ID = os.getenv("MATHPIX_APP_ID", "")
    MATHPIX_APP_KEY = os.getenv("MATHPIX_APP_KEY", "")
    
    # WolframAlpha (requis pour la résolution)
    WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" ou "gemini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Requis pour extraction LaTeX si Mathpix non configuré
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    # Support pour plusieurs origines séparées par des virgules
    # En production, inclure l'URL Vercel dans CORS_ORIGINS (ex: https://mathassistant.vercel.app)
    # Format: "https://app1.vercel.app,https://app2.vercel.app"
    _cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins_str.split(",") if origin.strip()]
    
    # Image upload
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))  # 10MB par défaut
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

config = Config()

