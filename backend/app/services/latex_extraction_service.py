"""
Service pour l'extraction LaTeX depuis des images
Supporte OpenAI Vision (alternative à Mathpix)
"""
import base64
from typing import Dict, Optional
from app.config import config


class LatexExtractionService:
    """Service pour extraire le LaTeX depuis des images"""
    
    def __init__(self):
        self.openai_api_key = config.OPENAI_API_KEY
        self.mathpix_app_id = config.MATHPIX_APP_ID
        self.mathpix_app_key = config.MATHPIX_APP_KEY
    
    def extract_latex(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Extrait le LaTeX depuis une image
        Utilise OpenAI Vision si Mathpix n'est pas configuré
        
        Args:
            image_bytes: Bytes de l'image
            
        Returns:
            Dict avec 'latex' et 'confidence'
            
        Raises:
            Exception: Si l'API retourne une erreur
        """
        # Priorité 1: Mathpix si configuré
        if self.mathpix_app_id and self.mathpix_app_key:
            return self._extract_with_mathpix(image_bytes)
        
        # Priorité 2: OpenAI Vision
        if self.openai_api_key:
            return self._extract_with_openai_vision(image_bytes)
        
        # Aucune méthode disponible
        raise ValueError(
            "Aucune méthode d'extraction LaTeX configurée. "
            "Configurez soit MATHPIX_APP_ID/MATHPIX_APP_KEY, soit OPENAI_API_KEY dans le fichier .env"
        )
    
    def _extract_with_mathpix(self, image_bytes: bytes) -> Dict[str, any]:
        """Extrait le LaTeX avec Mathpix API"""
        import httpx
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            "app_id": self.mathpix_app_id,
            "app_key": self.mathpix_app_key,
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
                response = client.post(
                    "https://api.mathpix.com/v3/text",
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                latex = (
                    result.get("latex_simplified") or
                    result.get("latex_styled") or
                    result.get("text", "")
                )
                
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
                raise Exception("Trop de requêtes Mathpix. Veuillez patienter.")
            else:
                error_detail = e.response.json().get("error", "Erreur inconnue")
                raise Exception(f"Erreur Mathpix API: {error_detail}")
        except httpx.TimeoutException:
            raise Exception("Timeout lors de l'appel à Mathpix API.")
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction LaTeX avec Mathpix: {str(e)}")
    
    def _extract_with_openai_vision(self, image_bytes: bytes) -> Dict[str, any]:
        """Extrait le LaTeX avec OpenAI Vision API"""
        from openai import OpenAI
        import base64
        
        client = OpenAI(api_key=self.openai_api_key)
        
        # Convertit l'image en base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Détermine le type MIME (simplifié, on assume JPEG ou PNG)
        image_format = "jpeg"
        if image_bytes.startswith(b'\x89\x50\x4E\x47'):
            image_format = "png"
        elif image_bytes.startswith(b'GIF'):
            image_format = "gif"
        elif image_bytes.startswith(b'RIFF'):
            image_format = "webp"
        
        prompt = """Tu es un expert en reconnaissance d'écriture mathématique manuscrite et imprimée.

Extrait le code LaTeX de cette image mathématique. L'image peut être manuscrite ou imprimée.

INSTRUCTIONS IMPORTANTES :
1. Si l'image est MANUSCRITE, sois particulièrement attentif aux symboles et caractères similaires :
   - Distingue bien : 0 (zéro) vs O (lettre), 1 (un) vs l (L minuscule), 2 vs Z, 5 vs S
   - Les fractions manuscrites : reconnais / comme \frac{}{}
   - Les puissances : reconnais les petits chiffres en haut comme des exposants (^)
   - Les indices : reconnais les petits chiffres en bas comme des indices (_)
   - Les racines : reconnais les symboles √ comme \sqrt
   - Les intégrales, sommes, produits : reconnais les symboles ∫, Σ, Π
   - Les lettres grecques manuscrites : α, β, γ, δ, θ, π, etc.

2. Si l'image est IMPRIMÉE, extrais fidèlement tous les symboles mathématiques.

3. Format de réponse :
   - Réponds UNIQUEMENT avec le code LaTeX pur
   - Pas d'explication, pas de texte supplémentaire, pas de markdown
   - Si plusieurs équations, sépare-les par des sauts de ligne
   - Utilise la syntaxe LaTeX standard :
     * Fractions : \frac{numerateur}{denominateur}
     * Puissances : x^{2} ou x^2
     * Indices : x_{i} ou x_i
     * Racines : \sqrt{x} ou \sqrt[n]{x}
     * Intégrales : \int, \int_{a}^{b}
     * Sommes : \sum_{i=1}^{n}
     * Produits : \prod_{i=1}^{n}
     * Limites : \lim_{x \to \infty}
     * Fonctions trigonométriques : \sin, \cos, \tan, etc.
     * Lettres grecques : \alpha, \beta, \gamma, \delta, \theta, \pi, etc.

4. Si tu ne peux vraiment pas extraire de LaTeX, réponds avec "ERREUR".

Exemples de conversions :
- "x au carré" → x^2
- "x divisé par 2" → \frac{x}{2} ou x/2
- "racine de x" → \sqrt{x}
- "intégrale de f(x)" → \int f(x) dx
- "somme de i=1 à n" → \sum_{i=1}^{n}
- "pi" → \pi
- "alpha" → \alpha"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # GPT-4o a une meilleure vision pour le manuscrit
                messages=[
                    {
                        "role": "system",
                        "content": """Tu es un expert en reconnaissance d'écriture mathématique manuscrite et imprimée. 
Tu es spécialisé dans la conversion d'équations mathématiques (manuscrites ou imprimées) en code LaTeX.
Tu réponds UNIQUEMENT avec le code LaTeX pur, sans formatage markdown, sans explication, sans texte supplémentaire.
Tu es particulièrement doué pour reconnaître les symboles mathématiques manuscrits même s'ils sont mal formés."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{image_base64}",
                                    "detail": "high"  # Haute résolution pour mieux voir les détails manuscrits
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,  # Augmenté pour les équations complexes
                temperature=0.0  # Température à 0 pour plus de précision et cohérence
            )
            
            latex = response.choices[0].message.content.strip()
            
            # Nettoie le LaTeX (enlève les markdown code blocks si présents)
            if "```latex" in latex:
                latex = latex.split("```latex")[1].split("```")[0].strip()
            elif "```" in latex:
                latex = latex.split("```")[1].split("```")[0].strip()
            
            # Vérifie si c'est une erreur
            if "ERREUR" in latex.upper() or not latex:
                raise Exception("Impossible d'extraire le LaTeX depuis l'image. Essayez avec une image plus nette ou une écriture plus claire.")
            
            # Nettoie le LaTeX (enlève les espaces superflus, normalise)
            latex = latex.strip()
            # Enlève les sauts de ligne multiples
            latex = ' '.join(latex.split())
            
            # Confidence basée sur la longueur et la présence de caractères LaTeX typiques
            confidence = 0.80  # Par défaut (plus conservateur pour le manuscrit)
            
            # Indicateurs de qualité LaTeX
            latex_indicators = ['\\', '^', '_', '{', '}', 'frac', 'sqrt', 'int', 'sum', 'prod', 'lim']
            if any(indicator in latex for indicator in latex_indicators):
                confidence = 0.85
            
            # Si contient des symboles mathématiques avancés, confiance plus élevée
            advanced_symbols = ['\\alpha', '\\beta', '\\gamma', '\\delta', '\\theta', '\\pi', '\\sum', '\\int', '\\prod']
            if any(symbol in latex for symbol in advanced_symbols):
                confidence = 0.90
            
            # Si longue et bien formée
            if len(latex) > 15 and latex.count('{') == latex.count('}'):  # Parenthèses équilibrées
                confidence = min(confidence + 0.05, 0.95)
            
            return {
                "latex": latex,
                "confidence": confidence
            }
            
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Trop de requêtes OpenAI. Veuillez patienter.")
            elif "invalid" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                raise Exception("Clé API OpenAI invalide ou expirée.")
            elif "timeout" in error_msg.lower():
                raise Exception("Timeout lors de l'appel à OpenAI API.")
            else:
                raise Exception(f"Erreur lors de l'extraction LaTeX avec OpenAI: {error_msg}")


# Instance globale
latex_extraction_service = LatexExtractionService()

