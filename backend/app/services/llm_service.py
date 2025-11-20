"""
Service pour générer des explications avec un LLM (OpenAI ou Gemini)
"""
import json
import re
import logging
from typing import Dict, List, Optional
from app.config import config

logger = logging.getLogger(__name__)


class LLMService:
    """Service pour communiquer avec les LLMs"""
    
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.openai_api_key = config.OPENAI_API_KEY
        self.gemini_api_key = config.GEMINI_API_KEY
        self.openai_model = config.OPENAI_MODEL
        self.gemini_model = config.GEMINI_MODEL
    
    def generate_explanation(
        self,
        problem: str,
        solution: str,
        steps: List[Dict]
    ) -> List[Dict]:
        """
        Génère des explications enrichies pour chaque étape
        
        Args:
            problem: Problème mathématique
            solution: Solution du problème
            steps: Liste des étapes brutes
            
        Returns:
            Liste des étapes avec explications enrichies
        """
        if self.provider == "openai":
            return self._generate_with_openai(problem, solution, steps)
        elif self.provider == "gemini":
            return self._generate_with_gemini(problem, solution, steps)
        else:
            # Fallback: retourner les steps sans modification
            return steps
    
    def _generate_with_openai(
        self,
        problem: str,
        solution: str,
        steps: List[Dict]
    ) -> List[Dict]:
        """Génère des explications avec OpenAI"""
        try:
            from openai import OpenAI
            
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key non configurée. "
                    "Définissez OPENAI_API_KEY dans le fichier .env"
                )
            
            client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Tu es un professeur de mathématiques expert. Analyse ce problème et ses étapes de résolution.

Problème: {problem}
Solution: {solution}

Étapes brutes:
{chr(10).join([f"{i+1}. {step.get('description', '')}" for i, step in enumerate(steps)])}

Pour chaque étape, génère une explication claire et pédagogique en français, formatée comme suit:
- title: Un titre court et clair
- description: L'étape principale
- formula: La formule mathématique en LaTeX (si applicable)
- explanation: Une explication détaillée et pédagogique

Réponds uniquement avec un JSON valide contenant un tableau "steps" avec les objets ci-dessus. Ne pas inclure de markdown ou de texte supplémentaire."""
            
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "Tu es un professeur de mathématiques expert qui explique clairement les solutions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Nettoie le contenu (enlève les markdown code blocks si présents)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            
            if isinstance(result, dict) and "steps" in result:
                return result["steps"]
            elif isinstance(result, list):
                return result
            else:
                return steps
                
        except json.JSONDecodeError as e:
            # Si le JSON est invalide, essayer de récupérer au moins le texte
            try:
                # Essayer d'extraire un JSON valide même s'il y a du texte autour
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                    if isinstance(result, dict) and "steps" in result:
                        return result["steps"]
                    elif isinstance(result, list):
                        return result
            except:
                pass
            # En dernier recours, retourner les steps originaux
            logger.warning(f"Erreur parsing JSON OpenAI: {str(e)}")
            return steps
        except Exception as e:
            # En cas d'erreur, retourner les steps originaux
            logger.warning(f"Erreur LLM OpenAI: {str(e)}")
            return steps
    
    def _generate_with_gemini(
        self,
        problem: str,
        solution: str,
        steps: List[Dict]
    ) -> List[Dict]:
        """Génère des explications avec Gemini"""
        try:
            import google.generativeai as genai
            
            if not self.gemini_api_key:
                raise ValueError(
                    "Gemini API key non configurée. "
                    "Définissez GEMINI_API_KEY dans le fichier .env"
                )
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            
            prompt = f"""Tu es un professeur de mathématiques expert. Analyse ce problème et ses étapes de résolution.

Problème: {problem}
Solution: {solution}

Étapes brutes:
{chr(10).join([f"{i+1}. {step.get('description', '')}" for i, step in enumerate(steps)])}

Pour chaque étape, génère une explication claire et pédagogique en français, formatée comme suit:
- title: Un titre court et clair
- description: L'étape principale
- formula: La formule mathématique en LaTeX (si applicable)
- explanation: Une explication détaillée et pédagogique

Réponds uniquement avec un JSON valide contenant un tableau "steps" avec les objets ci-dessus. Ne pas inclure de markdown ou de texte supplémentaire."""
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                }
            )
            
            content = response.text
            
            # Nettoie le contenu
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            
            if isinstance(result, dict) and "steps" in result:
                return result["steps"]
            elif isinstance(result, list):
                return result
            else:
                return steps
                
        except json.JSONDecodeError as e:
            # Si le JSON est invalide, essayer de récupérer au moins le texte
            try:
                # Essayer d'extraire un JSON valide même s'il y a du texte autour
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                    if isinstance(result, dict) and "steps" in result:
                        return result["steps"]
                    elif isinstance(result, list):
                        return result
            except:
                pass
            # En dernier recours, retourner les steps originaux
            logger.warning(f"Erreur parsing JSON Gemini: {str(e)}")
            return steps
        except Exception as e:
            # En cas d'erreur, retourner les steps originaux
            logger.warning(f"Erreur LLM Gemini: {str(e)}")
            return steps


# Instance globale
llm_service = LLMService()

