"""
Utilitaires pour la validation des fichiers uploadés
"""
from typing import Tuple, Optional
from fastapi import HTTPException


# Signatures de fichiers magiques pour vérification réelle
IMAGE_SIGNATURES = {
    b'\xFF\xD8\xFF': 'image/jpeg',
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'RIFF': 'image/webp',  # WebP commence par RIFF
}

ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg', 
    'image/gif', 'image/webp'
}


def validate_image_file(file_bytes: bytes, content_type: Optional[str] = None, max_size: int = 10485760) -> Tuple[bool, str]:
    """
    Valide un fichier image de manière sécurisée
    
    Args:
        file_bytes: Bytes du fichier
        content_type: Type MIME déclaré (optionnel)
        max_size: Taille maximale en bytes
        
    Returns:
        Tuple (is_valid, error_message)
        Si is_valid est True, error_message est vide
    """
    # Vérification de la taille
    if len(file_bytes) == 0:
        return False, "Le fichier est vide."
    
    if len(file_bytes) > max_size:
        size_mb = max_size / 1024 / 1024
        return False, f"Image trop grande. Taille maximale: {size_mb:.1f}MB"
    
    # Vérification de la signature magique (plus sûr que le content-type)
    detected_type = None
    
    # Vérifie PNG
    if file_bytes.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        detected_type = 'image/png'
    # Vérifie JPEG
    elif file_bytes.startswith(b'\xFF\xD8\xFF'):
        detected_type = 'image/jpeg'
    # Vérifie GIF
    elif file_bytes.startswith(b'GIF87a') or file_bytes.startswith(b'GIF89a'):
        detected_type = 'image/gif'
    # Vérifie WebP (plus complexe, commence par RIFF et contient WEBP)
    elif file_bytes.startswith(b'RIFF') and b'WEBP' in file_bytes[:20]:
        detected_type = 'image/webp'
    
    # Si le type détecté ne correspond pas au content_type déclaré
    if detected_type:
        if content_type and detected_type not in ALLOWED_MIME_TYPES:
            return False, f"Format d'image non supporté. Type détecté: {detected_type}"
    else:
        # Si aucune signature n'a été détectée, le fichier n'est probablement pas une image valide
        return False, "Format d'image non supporté ou fichier corrompu. Utilisez PNG, JPEG, GIF ou WEBP."
    
    # Vérifie que le type détecté est autorisé
    if detected_type not in ALLOWED_MIME_TYPES:
        return False, f"Format d'image non supporté: {detected_type}"
    
    # Vérifie que le content_type déclaré correspond (si fourni)
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        return False, f"Type MIME déclaré non supporté: {content_type}"
    
    return True, ""


def get_file_extension(content_type: Optional[str] = None) -> str:
    """
    Obtient l'extension de fichier depuis le content-type
    
    Args:
        content_type: Type MIME
        
    Returns:
        Extension de fichier (sans le point)
    """
    mapping = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/gif': 'gif',
        'image/webp': 'webp',
    }
    return mapping.get(content_type or '', 'png')

