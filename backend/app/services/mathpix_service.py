"""
Service pour l'extraction LaTeX depuis des images via Mathpix API
"""
import base64
import httpx
from typing import Dict, Optional
from app.config import config


class MathpixService:
    """Service pour communiquer avec l'API Mathpix"""
    
    API_URL = "https://api.mathpix.com/v3/text"
    
    def __init__(self):
        self.app_id = config.MATHPIX_APP_ID
        self.app_key = config.MATHPIX_APP_KEY
    
    def _image_to_base64(self, image_bytes: bytes) -> str:
        """Convertit une image en base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_latex(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Extrait le LaTeX depuis une image
        
        Args:
            image_bytes: Bytes de l'image
            
        Returns:
            Dict avec 'latex' et 'confidence'
            
        Raises:
            Exception: Si l'API retourne une erreur
        """
        if not self.app_id or not self.app_key:
            raise ValueError(
                "Mathpix API credentials non configurées. "
                "Définissez MATHPIX_APP_ID et MATHPIX_APP_KEY dans le fichier .env"
            )
        
        image_base64 = self._image_to_base64(image_bytes)
        
        headers = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "src": f"data:image/jpeg;base64,{image_base64}",
            "formats": ["text", "latex_styled", "latex_simplified"],
            "data_options": {
                "include_asciimath": True,
                "include_latex": True
            }
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.API_URL, json=data, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                # Extrait le LaTeX (priorité: latex_simplified > latex_styled > text)
                latex = (
                    result.get("latex_simplified") or
                    result.get("latex_styled") or
                    result.get("text", "")
                )
                
                # Calcule la confiance (basée sur is_printed ou probabilité si disponible)
                confidence = result.get("confidence", 0.0)
                if "is_printed" in result:
                    confidence = 0.95 if result["is_printed"] else 0.85
                
                return {
                    "latex": latex.strip(),
                    "confidence": min(max(confidence, 0.0), 1.0)
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                raise Exception("Quota Mathpix dépassé. Vérifiez votre compte.")
            elif e.response.status_code == 401:
                raise Exception("Identifiants Mathpix invalides.")
            elif e.response.status_code == 429:
                raise Exception("Trop de requêtes. Veuillez patienter.")
            else:
                error_detail = e.response.json().get("error", "Erreur inconnue")
                raise Exception(f"Erreur Mathpix API: {error_detail}")
        except httpx.TimeoutException:
            raise Exception("Timeout lors de l'appel à Mathpix API.")
        except Exception as e:
            if "credentials" in str(e).lower() or "MATHPIX" in str(e):
                raise
            raise Exception(f"Erreur lors de l'extraction LaTeX: {str(e)}")


# Instance globale
mathpix_service = MathpixService()

