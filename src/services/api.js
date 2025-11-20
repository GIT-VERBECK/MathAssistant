/**
 * Service API pour communiquer avec le backend
 * Toutes les fonctions retournent des Promises
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

/**
 * Convertit une image (base64 ou File) en FormData pour l'envoi
 */
const imageToFormData = (imageData) => {
  const formData = new FormData();
  
  if (typeof imageData === 'string') {
    // Si c'est un base64, convertir en blob
    const base64Data = imageData.split(',')[1] || imageData;
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/png' });
    formData.append('image', blob, 'image.png');
  } else if (imageData instanceof File) {
    formData.append('image', imageData);
  } else {
    throw new Error('Format d\'image non supporté');
  }
  
  return formData;
};

/**
 * Gère les erreurs de l'API et retourne des messages utilisateur clairs
 */
const handleApiError = (error) => {
  if (error.response) {
    // Erreur de réponse du serveur
    const status = error.response.status;
    const data = error.response.data;
    
    switch (status) {
      case 400:
        return data.message || 'Requête invalide. Vérifiez votre image.';
      case 413:
        return 'L\'image est trop grande. Veuillez utiliser une image plus petite.';
      case 422:
        return data.message || 'Impossible de détecter d\'équation mathématique dans l\'image.';
      case 429:
        return 'Trop de requêtes. Veuillez patienter quelques instants.';
      case 500:
        // Affiche le détail de l'erreur si disponible (en mode DEBUG)
        const detail = data.detail || data.message || '';
        if (detail && (detail.includes('credentials') || detail.includes('configur') || detail.includes('API'))) {
          return `Erreur de configuration: ${detail}. Vérifiez vos clés API dans le fichier backend/.env`;
        }
        return data.detail || data.message || 'Erreur serveur. Veuillez réessayer plus tard.';
      default:
        return data.message || 'Une erreur est survenue.';
    }
  } else if (error.request) {
    // Pas de réponse du serveur
    return 'Erreur de connexion. Vérifiez votre connexion internet.';
  } else {
    // Erreur lors de la configuration de la requête
    return error.message || 'Une erreur inattendue est survenue.';
  }
};

/**
 * Upload une image et obtient le LaTeX extrait
 * @param {string|File} imageData - Image en base64 ou File
 * @returns {Promise<{latex: string, confidence: number}>}
 */
export const getLaTeXFromImage = async (imageData) => {
  try {
    const formData = imageToFormData(imageData);
    
    const response = await fetch(`${API_BASE_URL}/latex`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
      throw { response: { status: response.status, data: error } };
    }

    const data = await response.json();
    return {
      latex: data.latex || data.text || '',
      confidence: data.confidence || 0,
    };
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
};

/**
 * Analyse complète d'une image : LaTeX → Résolution → Explication
 * @param {string|File} imageData - Image en base64 ou File
 * @param {string} latex - LaTeX confirmé par l'utilisateur (optionnel)
 * @returns {Promise<{problem: string, solution: string, steps: Array, latex: string}>}
 */
export const analyzeImage = async (imageData, latex = null) => {
  try {
    const formData = imageToFormData(imageData);
    if (latex) {
      formData.append('latex', latex);
    }
    
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
      throw { response: { status: response.status, data: error } };
    }

    const data = await response.json();
    return {
      problem: data.problem || '',
      solution: data.solution || '',
      steps: data.steps || [],
      latex: data.latex || '',
    };
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
};

/**
 * Upload simple d'une image (pour usage futur)
 * @param {string|File} imageData - Image en base64 ou File
 * @returns {Promise<string>} - URL de l'image uploadée
 */
export const uploadImage = async (imageData) => {
  try {
    const formData = imageToFormData(imageData);
    
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
      throw { response: { status: response.status, data: error } };
    }

    const data = await response.json();
    return data.url || data.imageUrl || '';
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
};

