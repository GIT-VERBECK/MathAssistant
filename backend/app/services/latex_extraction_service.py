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
                "include_latex": True,
                "handwritten_equation": True,  # Indique que c'est peut-être manuscrit
                "include_annotations": True,  # Inclut plus de détails pour manuscrits
                "enable_tables_fallback": True,  # Meilleure détection des structures
                "format_options": {
                    "text": {
                        "math_inline_delimiters": ["$", "$"],
                        "rm_spaces": False
                    }
                }
            },
            "handwritten": True  # Mode manuscrit activé
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
                
                # Post-traitement pour manuscrits
                if latex:
                    latex = self._post_process_handwritten_latex(latex.strip())
                
                confidence = result.get("confidence", 0.0)
                if "is_printed" in result:
                    # Si manuscrit, confiance légèrement réduite mais toujours utilisable
                    confidence = 0.95 if result["is_printed"] else 0.82
                elif confidence == 0.0:
                    # Par défaut pour manuscrits
                    confidence = 0.80
                
                return {
                    "latex": latex,
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
            raise Exception(f"Erreur lors de l'extraction {str(e)}")
    
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

⚠️ INSTRUCTIONS CRITIQUES POUR LES MANUSCRITS ⚠️

1. PUISSANCES ET EXPOSANTS (PRIORITÉ ABSOLUE) :
   - Les petits chiffres ÉCRITS AU-DESSUS d'un nombre ou d'une lettre sont TOUJOURS des exposants
   - Même si l'exposant est mal aligné, légèrement décalé, ou mal formé, c'est TOUJOURS un exposant
   - Si tu vois un chiffre positionné AU-DESSUS ou légèrement plus haut que le nombre de base, c'est un exposant
   - IMPORTANT : Dans "37 - 4^2", le "2" est un exposant car il est écrit AU-DESSUS du "4"
   - Exemples manuscrits typiques :
     * "4 avec un petit 2 en haut" → 4^2 ou 4^{2}
     * "37 - 4²" ou "37 - 4 avec 2 en haut" → 37-4^{2} ou 37 - 4^2
     * "x avec un petit 3 en haut" → x^3 ou x^{3}
     * "x²" → x^{2} ou x^2
     * "a³" → a^{3} ou a^3
   - Si un chiffre suit immédiatement un nombre sans opérateur visible ET qu'il est positionné plus haut → exposant
   - Pattern courant : "nombre nombre" où le second nombre est plus petit/haut → puissance

2. CARACTÈRES SIMILAIRES (MANUSCRITS) :
   - Distingue bien : 0 (zéro) vs O (lettre), 1 (un) vs l (L minuscule), 2 vs Z, 5 vs S
   - Le contexte aide : si c'est dans une opération mathématique, c'est probablement un chiffre

3. SYMBOLES MATHÉMATIQUES :
   - Les fractions manuscrites : reconnais / comme \frac{}{} ou laisse /
   - Les puissances : TOUJOURS utiliser ^ pour les exposants
   - Les indices : reconnais les petits chiffres en bas comme des indices (_)
   - Les racines : reconnais les symboles √ comme \sqrt
   - Les intégrales, sommes, produits : reconnais ∫, Σ, Π
   - Les lettres grecques manuscrites : α, β, γ, δ, θ, π, etc.

4. OPÉRATIONS DE BASE :
   - + (addition), - (soustraction), × ou * (multiplication), ÷ ou / (division), = (égal)
   - Les espaces autour des opérateurs sont optionnels

5. Format de réponse :
   - Réponds UNIQUEMENT avec le code LaTeX pur, sans formatage markdown
   - Pas d'explication, pas de texte supplémentaire
   - Utilise la syntaxe LaTeX standard :
     * Puissances : x^{2} ou x^2 (TOUJOURS avec ^)
     * Indices : x_{i} ou x_i
     * Fractions : \frac{numerateur}{denominateur} ou a/b
     * Racines : \sqrt{x} ou \sqrt[n]{x}
     * Intégrales : \int, \int_{a}^{b}
     * Sommes : \sum_{i=1}^{n}
     * Produits : \prod_{i=1}^{n}

6. EXEMPLES SPÉCIFIQUES DE MANUSCRITS (RÉFÉRENCE) :
   - "37 - 4²" ou "37 - 4 avec 2 en haut" → 37-4^{2} ou 37 - 4^2
   - "37 - 4 2" (sans opérateur entre 4 et 2, 2 est plus haut) → 37-4^{2}
   - "x² + 5" ou "x avec 2 en haut plus 5" → x^{2}+5 ou x^2 + 5
   - "2³" ou "2 avec 3 en haut" → 2^{3} ou 2^3
   - "a²b³" → a^{2}b^{3} ou a^2 b^3
   - "x + 1 = 0" → x+1=0 ou x + 1 = 0
   - "5² - 3" → 5^{2}-3 ou 5^2 - 3
   - "10 - 2²" → 10-2^{2} ou 10 - 2^2

7. DÉTECTION DES EXPOSANTS MANUSCRITS :
   - Examine attentivement la POSITION VERTICALE des chiffres
   - Si un chiffre est clairement plus haut que le chiffre précédent → exposant
   - Si deux chiffres sont côte à côte sans opérateur, et le second est plus petit/haut → exposant
   - Même si l'alignement n'est pas parfait (typique des manuscrits), détecte les exposants par position

7. Si tu ne peux vraiment pas extraire de LaTeX, réponds avec "ERREUR"."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # GPT-4o a une meilleure vision pour le manuscrit
                messages=[
                    {
                        "role": "system",
                        "content": """Tu es un expert en reconnaissance d'écriture mathématique manuscrite et imprimée. 
Tu es spécialisé dans la conversion d'équations mathématiques (manuscrites ou imprimées) en code LaTeX.
Tu réponds UNIQUEMENT avec le code LaTeX pur, sans formatage markdown, sans explication, sans texte supplémentaire.

TU ES TRÈS DOUÉ POUR :
- Reconnaître les PUISSANCES et EXPOSANTS manuscrits (petits chiffres en haut) et les convertir en notation ^
- Distinguer les chiffres manuscrits des lettres (0 vs O, 1 vs l, 2 vs Z, 5 vs S)
- Identifier les symboles mathématiques même s'ils sont mal formés ou mal alignés
- Extraire fidèlement les opérations arithmétiques de base (+, -, ×, ÷, =)

RÈGLE D'OR : Si tu vois un petit chiffre ÉCRIT AU-DESSUS d'un nombre ou d'une lettre, c'est TOUJOURS un exposant. Utilise ^ pour le représenter."""
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
                raise Exception("Impossible d'extraire l'équation depuis l'image. Essayez avec une image plus nette ou une écriture plus claire.")
            
            # Nettoie le LaTeX (enlève les espaces superflus, normalise)
            latex = latex.strip()
            # Enlève les sauts de ligne multiples
            latex = ' '.join(latex.split())
            
            # Post-traitement pour corriger les erreurs communes de manuscrits
            latex = self._post_process_handwritten_latex(latex)
            
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
                raise Exception(f"Erreur lors de l'extraction : {error_msg}")
    
    def _post_process_handwritten_latex(self, latex: str) -> str:
        """
        Post-traitement pour corriger les erreurs communes de reconnaissance manuscrite
        
        Args:
            latex: Code LaTeX brut
            
        Returns:
            Code LaTeX corrigé
        """
        import re
        
        # Remplacer les caractères unicode de puissance courants par ^
        # Exemples: ², ³, ⁴, etc.
        power_chars = {
            '²': '^2',
            '³': '^3',
            '⁴': '^4',
            '⁵': '^5',
            '⁶': '^6',
            '⁷': '^7',
            '⁸': '^8',
            '⁹': '^9',
            '¹': '^1',
            '⁰': '^0'
        }
        
        for char, replacement in power_chars.items():
            latex = latex.replace(char, replacement)
        
        # Corriger les patterns où un exposant est écrit comme un nombre normal
        # Pattern: "4 2" ou "4(2)" après un nombre dans une soustraction peut être une puissance
        # Exemple: "37 - 4 2" → "37 - 4^2"
        # Mais seulement si c'est suivi d'un opérateur ou d'une fin d'expression
        
        # Pattern pour détecter "nombre espace petit_chiffre" suivi d'opérateur ou fin
        # Exemple: "4 2 -" ou "4 2 ="
        pattern_power = r'(\d+)\s+([0-9])(?=\s*[+\-=×*÷/,\)]|\s*$|)'
        
        # Vérifier si le contexte suggère une puissance (petit nombre, 2-9)
        # On remplace seulement si le nombre suivant est 0-9 et que le contexte est bon
        def replace_potential_power(match):
            base = match.group(1)
            exponent = match.group(2)
            # Si l'exposant est 2-9, c'est probablement une puissance
            if exponent in '23456789':
                return f'{base}^{exponent}'
            return match.group(0)
        
        # Appliquer la correction avec prudence (seulement en contexte clair)
        latex = re.sub(pattern_power, replace_potential_power, latex)
        
        # Corriger les cas où "^2" ou "^3" sont écrits comme "2" ou "3" collés
        # Pattern: "4^ 2" → "4^2" ou "4 ^2" → "4^2"
        latex = re.sub(r'\^\s+(\d+)', r'^{\1}', latex)
        latex = re.sub(r'\^\s*(\d+)', r'^{\1}', latex)
        
        # Normaliser les espaces autour des opérateurs
        latex = re.sub(r'\s*([+\-=×*÷/])\s*', r' \1 ', latex)
        
        # Corriger les accolades autour des exposants simples pour meilleure lisibilité
        # x^{2} → x^2 (si exposant simple d'un seul chiffre)
        latex = re.sub(r'(\w+)\{(\d)\}', r'\1^{\2}', latex)
        # Mais garder les accolades pour les exposants complexes (plusieurs chiffres ou expressions)
        
        # Corriger les patterns communs de manuscrits mal reconnus
        # "4 2" peut devenir "42" ou "4^2" selon le contexte
        # Si on voit "nombre-nombre espace nombre" suivi d'un opérateur, c'est peut-être une puissance
        # Exemple: "37-4 2=" → "37-4^2="
        pattern_in_expression = r'(\d+)\s+([0-9])(?=\s*[=\+\-\)])'
        latex = re.sub(pattern_in_expression, lambda m: f'{m.group(1)}^{m.group(2)}' if m.group(2) in '23456789' else m.group(0), latex)
        
        # Enlever les espaces superflus mais garder les espaces autour des opérateurs
        latex = ' '.join(latex.split())
        
        # Normaliser les espaces autour des opérateurs une dernière fois
        latex = re.sub(r'\s*([+\-=×*÷/])\s*', r' \1 ', latex)
        
        return latex.strip()


# Instance globale
latex_extraction_service = LatexExtractionService()

