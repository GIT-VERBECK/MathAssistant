"""
Routes API pour Math Assistant
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.services.latex_extraction_service import latex_extraction_service
from app.services.wolfram_service import wolfram_service
from app.services.llm_service import llm_service
from app.config import config
from app.utils.file_validation import validate_image_file
from app.utils.error_handler import handle_service_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/latex")
async def extract_latex(image: UploadFile = File(...)):
    """
    Extrait le LaTeX depuis une image
    
    Args:
        image: Fichier image uploadé
        
    Returns:
        JSON avec 'latex' et 'confidence'
    """
    try:
        # Lit l'image
        image_bytes = await image.read()
        
        # Validation sécurisée du fichier (signature magique + taille)
        is_valid, error_message = validate_image_file(
            image_bytes,
            content_type=image.content_type,
            max_size=config.MAX_UPLOAD_SIZE
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"Extraction LaTeX demandée pour un fichier de {len(image_bytes)} bytes")
        
        # Extrait le LaTeX
        result = latex_extraction_service.extract_latex(image_bytes)
        
        if not result.get("latex"):
            raise HTTPException(
                status_code=422,
                detail="Impossible de détecter d'équation mathématique dans l'image."
            )
        
        logger.info(f"LaTeX extrait avec succès (confidence: {result.get('confidence', 0):.2f})")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError lors de l'extraction LaTeX: {str(e)}")
        raise handle_service_error(e)
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'extraction LaTeX: {str(e)}", exc_info=True)
        raise handle_service_error(e)


@router.post("/analyze")
async def analyze_problem(
    image: UploadFile = File(...),
    latex: Optional[str] = Form(None)
):
    """
    Analyse complète : LaTeX → Résolution → Explication
    
    Args:
        image: Fichier image uploadé
        latex: LaTeX confirmé par l'utilisateur (optionnel)
        
    Returns:
        JSON avec 'problem', 'latex', 'solution' et 'steps'
    """
    try:
        # Lit l'image si nécessaire
        image_bytes = None
        if not latex:
            image_bytes = await image.read()
            
            # Validation sécurisée du fichier
            is_valid, error_message = validate_image_file(
                image_bytes,
                content_type=image.content_type,
                max_size=config.MAX_UPLOAD_SIZE
            )
            
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"Analyse complète demandée (latex fourni: {latex is not None})")
        
        # 1. Extraction LaTeX
        extracted_latex = latex
        if not extracted_latex:
            logger.info("Extraction LaTeX depuis l'image...")
            latex_result = latex_extraction_service.extract_latex(image_bytes)
            extracted_latex = latex_result.get("latex", "")
        
        if not extracted_latex:
            raise HTTPException(
                status_code=422,
                detail="Impossible de détecter d'équation mathématique dans l'image."
            )
        
        logger.info(f"LaTeX extrait: {extracted_latex[:50]}...")
        
        # 2. Résolution avec WolframAlpha
        logger.info("Résolution avec WolframAlpha...")
        solution = ""
        raw_steps = []
        
        try:
            wolfram_result = wolfram_service.solve(extracted_latex)
            solution = wolfram_result.get("solution", "")
            raw_steps = wolfram_result.get("steps", [])
            
            if solution:
                logger.info(f"Solution trouvée: {solution[:50]}...")
            else:
                logger.warning("Aucune solution trouvée par WolframAlpha")
        except Exception as e:
            logger.warning(f"Erreur WolframAlpha: {str(e)}, tentative de calcul direct")
            # Si WolframAlpha échoue, on essaie un calcul direct
            try:
                # Convertit le LaTeX en expression calculable
                import re
                calc_expr = extracted_latex
                
                # Remplace les puissances: 4^{2} -> 4**2, 4^2 -> 4**2
                calc_expr = re.sub(r'\^{(\d+)}', r'**\1', calc_expr)
                calc_expr = re.sub(r'\^(\d+)', r'**\1', calc_expr)
                
                # Nettoie les autres caractères LaTeX
                calc_expr = calc_expr.replace('\\', '').replace('{', '').replace('}', '')
                calc_expr = calc_expr.replace(' ', '')
                
                # Calcule directement
                import math
                allowed_names = {
                    k: v for k, v in math.__dict__.items() if not k.startswith("__")
                }
                allowed_names.update({'abs': abs, 'round': round})
                
                result = eval(calc_expr, {"__builtins__": {}}, allowed_names)
                
                if isinstance(result, float):
                    if result.is_integer():
                        solution = str(int(result))
                    else:
                        solution = str(round(result, 10))
                else:
                    solution = str(result)
                
                raw_steps = [{
                    "title": "Calcul direct",
                    "description": f"Calcul de l'expression: {extracted_latex}",
                    "formula": f"{extracted_latex} = {solution}",
                    "explanation": f"Le résultat de {extracted_latex} est {solution}."
                }]
                logger.info(f"Calcul direct réussi: {solution}")
            except Exception as calc_error:
                logger.warning(f"Calcul direct échoué: {str(calc_error)}")
                solution = ""
                raw_steps = []
        
        if not solution and not raw_steps:
            # Dernier fallback si tout échoue
            solution = "Résolution disponible"
            raw_steps = [{
                "title": "Analyse du problème",
                "description": extracted_latex,
                "formula": extracted_latex,
                "explanation": "Analyse du problème mathématique. Les étapes détaillées seront générées par l'IA."
            }]
        
        # 3. Enrichissement avec LLM
        logger.info(f"Enrichissement avec LLM ({llm_service.provider})...")
        try:
            enriched_steps = llm_service.generate_explanation(
                problem=extracted_latex,
                solution=solution,
                steps=raw_steps
            )
            
            if enriched_steps and len(enriched_steps) > 0:
                logger.info(f"{len(enriched_steps)} étapes enrichies générées")
            else:
                logger.warning("Aucune étape enrichie générée, utilisation des étapes brutes")
                enriched_steps = raw_steps
        except Exception as e:
            logger.warning(f"Erreur LLM: {str(e)}, utilisation des étapes brutes")
            enriched_steps = raw_steps
        
        # Format la réponse
        result = {
            "problem": extracted_latex,
            "latex": extracted_latex,
            "solution": solution,
            "steps": enriched_steps if enriched_steps else raw_steps
        }
        
        logger.info("Analyse complète terminée avec succès")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError lors de l'analyse: {str(e)}")
        raise handle_service_error(e)
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'analyse: {str(e)}", exc_info=True)
        raise handle_service_error(e)

