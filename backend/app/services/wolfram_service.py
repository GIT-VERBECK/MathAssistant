"""
Service pour résoudre des problèmes mathématiques via WolframAlpha API
"""
import httpx
from typing import Dict, List, Optional
from app.config import config


class WolframService:
    """Service pour communiquer avec l'API WolframAlpha"""
    
    API_URL = "https://api.wolframalpha.com/v2/query"
    
    def __init__(self):
        self.app_id = config.WOLFRAM_APP_ID
    
    def solve(self, query: str) -> Dict[str, any]:
        """
        Résout un problème mathématique
        
        Args:
            query: Problème mathématique en texte ou LaTeX
            
        Returns:
            Dict avec 'solution' et 'steps'
            
        Raises:
            Exception: Si l'API retourne une erreur
        """
        if not self.app_id:
            raise ValueError(
                "WolframAlpha API credentials non configurées. "
                "Définissez WOLFRAM_APP_ID dans le fichier .env"
            )
        
        params = {
            "input": query,
            "appid": self.app_id,
            "output": "json",
            "includepodid": "Result,Solution,Step-by-step solution"
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.API_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse la réponse WolframAlpha
                solution = ""
                steps = []
                
                if "queryresult" in data:
                    query_result = data["queryresult"]
                    
                    if query_result.get("success", False):
                        pods = query_result.get("pods", [])
                        
                        for pod in pods:
                            pod_id = pod.get("id", "")
                            subpods = pod.get("subpods", [])
                            
                            # Solution principale
                            if pod_id == "Result" and subpods:
                                solution_text = subpods[0].get("plaintext", "")
                                if solution_text:
                                    solution = solution_text
                            
                            # Solution alternative (si Result n'est pas disponible)
                            elif pod_id == "Solution" and not solution and subpods:
                                solution_text = subpods[0].get("plaintext", "")
                                if solution_text:
                                    solution = solution_text
                            
                            # Étapes de résolution
                            if pod_id in ["Solution", "Step-by-step solution", "Result"]:
                                for idx, subpod in enumerate(subpods):
                                    step_text = subpod.get("plaintext", "")
                                    if step_text and step_text not in [s.get("description", "") for s in steps]:
                                        # Extrait la formule mathématique si disponible
                                        mathml = subpod.get("mathml", "")
                                        formula = ""
                                        
                                        # Essaye d'extraire une formule depuis mathml ou img
                                        img_src = subpod.get("img", {}).get("src", "")
                                        
                                        steps.append({
                                            "title": pod.get("title", f"Étape {len(steps) + 1}"),
                                            "description": step_text,
                                            "formula": formula,
                                            "explanation": step_text
                                        })
                    
                    else:
                        # Si pas de succès, essayer d'extraire des infos partielles
                        error_msg = query_result.get("error", {}).get("msg", "")
                        if error_msg:
                            raise Exception(f"Erreur WolframAlpha: {error_msg}")
                        else:
                            raise Exception("Impossible de résoudre le problème avec WolframAlpha.")
                
                return {
                    "solution": solution,
                    "steps": steps
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Identifiants WolframAlpha invalides.")
            elif e.response.status_code == 403:
                raise Exception("Accès refusé à WolframAlpha API.")
            elif e.response.status_code == 429:
                raise Exception("Trop de requêtes WolframAlpha. Veuillez patienter.")
            else:
                raise Exception(f"Erreur WolframAlpha API: {e.response.status_code}")
        except httpx.TimeoutException:
            raise Exception("Timeout lors de l'appel à WolframAlpha API.")
        except Exception as e:
            if "credentials" in str(e).lower() or "WolframAlpha" in str(e):
                raise
            raise Exception(f"Erreur lors de la résolution: {str(e)}")


# Instance globale
wolfram_service = WolframService()

