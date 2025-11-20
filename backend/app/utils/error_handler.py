"""
Gestionnaire d'erreurs centralisé pour l'API
"""
import logging
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Exception personnalisée pour les erreurs API"""
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


def create_error_response(
    message: str,
    status_code: int = 500,
    error_code: Optional[str] = None,
    details: Optional[dict] = None
) -> JSONResponse:
    """
    Crée une réponse d'erreur standardisée
    
    Args:
        message: Message d'erreur
        status_code: Code HTTP
        error_code: Code d'erreur personnalisé (optionnel)
        details: Détails supplémentaires (optionnel)
        
    Returns:
        JSONResponse avec l'erreur formatée
    """
    error_body = {
        "error": True,
        "message": message,
    }
    
    if error_code:
        error_body["error_code"] = error_code
    
    if details:
        error_body["details"] = details
    
    logger.error(f"API Error [{status_code}]: {message}", extra={"error_code": error_code, "details": details})
    
    return JSONResponse(
        status_code=status_code,
        content=error_body
    )


def handle_service_error(error: Exception) -> HTTPException:
    """
    Gère les erreurs des services et les convertit en HTTPException appropriée
    
    Args:
        error: Exception levée par un service
        
    Returns:
        HTTPException avec message approprié
    """
    error_message = str(error)
    
    # Erreurs de configuration (credentials manquantes)
    if "credentials" in error_message.lower() or "configur" in error_message.lower():
        logger.error(f"Configuration error: {error_message}")
        return HTTPException(
            status_code=500,
            detail="Configuration API manquante. Vérifiez vos clés API dans le fichier .env."
        )
    
    # Erreurs de quota/rate limiting
    if any(keyword in error_message.lower() for keyword in ["quota", "rate limit", "trop de requêtes", "429"]):
        logger.warning(f"Rate limit error: {error_message}")
        return HTTPException(
            status_code=429,
            detail="Trop de requêtes. Veuillez patienter quelques instants."
        )
    
    # Erreurs d'authentification
    if any(keyword in error_message.lower() for keyword in ["invalid", "401", "403", "unauthorized", "forbidden"]):
        logger.error(f"Authentication error: {error_message}")
        return HTTPException(
            status_code=500,
            detail="Erreur d'authentification API. Vérifiez vos clés API."
        )
    
    # Erreurs de timeout
    if "timeout" in error_message.lower():
        logger.warning(f"Timeout error: {error_message}")
        return HTTPException(
            status_code=504,
            detail="Le service externe a pris trop de temps à répondre. Veuillez réessayer."
        )
    
    # Erreurs de réseau
    if any(keyword in error_message.lower() for keyword in ["connection", "network", "dns", "resolve"]):
        logger.error(f"Network error: {error_message}")
        return HTTPException(
            status_code=503,
            detail="Service temporairement indisponible. Vérifiez votre connexion internet."
        )
    
    # Erreurs génériques
    logger.error(f"Service error: {error_message}")
    return HTTPException(
        status_code=500,
        detail=error_message
    )

