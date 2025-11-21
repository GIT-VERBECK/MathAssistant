"""
Service pour résoudre des problèmes mathématiques via WolframAlpha API
"""
import httpx
import re
import math
from typing import Dict, List, Optional
from app.config import config


class WolframService:
    """Service pour communiquer avec l'API WolframAlpha"""
    
    API_URL = "https://api.wolframalpha.com/v2/query"
    
    def __init__(self):
        self.app_id = config.WOLFRAM_APP_ID
    
    def _latex_to_text(self, latex: str) -> str:
        """
        Convertit du LaTeX en format texte simple pour WolframAlpha
        
        Args:
            latex: Expression LaTeX
            
        Returns:
            Expression en format texte
        """
        if not latex:
            return ""
        
        # Convertit les commandes LaTeX communes en texte
        text = latex
        
        # Remplace les puissances: x^{2} -> x^2, x^2 -> x^2
        text = re.sub(r'\^{(\d+)}', r'^\1', text)
        text = re.sub(r'\^(\d+)', r'^\1', text)
        
        # Remplace les fractions: \frac{a}{b} -> (a/b)
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)
        
        # Remplace les racines: \sqrt{x} -> sqrt(x)
        text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', text)
        text = re.sub(r'\\sqrt\[(\d+)\]\{([^}]+)\}', r'(\2)^(1/\1)', text)
        
        # Nettoie les espaces et caractères spéciaux
        text = text.replace('\\', '').replace('{', '').replace('}', '')
        text = text.replace(' ', '')
        
        return text
    
    def _calculate_simple_expression(self, expression: str) -> Optional[str]:
        """
        Calcule une expression mathématique simple en Python
        Utilisé comme fallback si WolframAlpha échoue
        
        Args:
            expression: Expression mathématique en texte
            
        Returns:
            Résultat calculé ou None si impossible
        """
        try:
            # Nettoie l'expression
            expr = expression.strip()
            
            # Remplace les opérateurs communs
            expr = expr.replace('^', '**')  # Puissance Python
            expr = expr.replace('×', '*').replace('·', '*')
            expr = expr.replace('÷', '/')
            
            # Évalue l'expression de manière sécurisée
            # On utilise seulement les fonctions mathématiques de base
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
            })
            
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            
            # Formate le résultat
            if isinstance(result, float):
                if result.is_integer():
                    return str(int(result))
                return str(round(result, 10))
            return str(result)
        except:
            return None
    
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
        
        # Convertit le LaTeX en format texte si nécessaire
        wolfram_query = query
        if '\\' in query or '{' in query or '^' in query:
            # C'est probablement du LaTeX, on le convertit
            wolfram_query = self._latex_to_text(query)
        
        params = {
            "input": wolfram_query,
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
                        didyoumeans = query_result.get("didyoumeans", {}).get("val", "")
                        
                        # Log pour debug
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"WolframAlpha query failed. Query: {wolfram_query}, Error: {error_msg}, Suggestions: {didyoumeans}")
                        
                        if error_msg:
                            raise Exception(f"Erreur WolframAlpha: {error_msg}")
                        elif didyoumeans:
                            raise Exception(f"Impossible de résoudre. Suggestion: {didyoumeans}")
                        else:
                            # Essayer un calcul simple en fallback
                            simple_result = self._calculate_simple_expression(wolfram_query)
                            if simple_result:
                                return {
                                    "solution": simple_result,
                                    "steps": [{
                                        "title": "Calcul direct",
                                        "description": f"Calcul de l'expression: {wolfram_query}",
                                        "formula": f"{wolfram_query} = {simple_result}",
                                        "explanation": f"Le résultat de {wolfram_query} est {simple_result}."
                                    }]
                                }
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

