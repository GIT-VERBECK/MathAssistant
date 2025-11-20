# Math Assistant - Backend

API FastAPI pour résoudre des problèmes mathématiques à partir d'images, avec extraction LaTeX, résolution et explications.

## Technologies

- **FastAPI** - Framework web moderne et rapide
- **Mathpix API** - Extraction LaTeX depuis des images
- **WolframAlpha API** - Résolution de problèmes mathématiques
- **OpenAI/Gemini** - Génération d'explications avec LLM
- **Uvicorn** - Serveur ASGI
- **httpx** - Client HTTP asynchrone

## Installation

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Créez un fichier `.env` à la racine du dossier `backend` (copiez depuis `.env.example`) :

```bash
cp .env.example .env
```

Puis éditez le fichier `.env` avec vos clés API :

```env
# Configuration du serveur
HOST=0.0.0.0
PORT=5000
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Mathpix API (pour extraction LaTeX)
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key

# WolframAlpha API (pour résolution)
WOLFRAM_APP_ID=your_wolfram_app_id

# LLM Configuration
LLM_PROVIDER=openai  # ou "gemini"

# OpenAI (si LLM_PROVIDER=openai)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# Google Gemini (si LLM_PROVIDER=gemini)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Obtenir les clés API

**Minimum requis :**
- **OpenAI**: https://platform.openai.com/api-keys (pour extraction LaTeX et explications)
- **WolframAlpha**: https://products.wolframalpha.com/api/ (pour résolution)

**Optionnel :**
- **Mathpix**: https://mathpix.com/ (alternative à OpenAI pour extraction LaTeX, plus précis mais payant)
- **Gemini**: https://aistudio.google.com/app/apikey (alternative à OpenAI pour explications)

**Note :** Si vous n'avez pas Mathpix, le backend utilisera automatiquement OpenAI Vision pour extraire le LaTeX depuis les images.

## Développement

### Lancer le serveur

```bash
python main.py
```

Ou avec uvicorn directement :

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

Le serveur sera accessible sur `http://localhost:5000`

### Documentation API

Une fois le serveur lancé, accédez à :
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## Structure du projet

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration et variables d'environnement
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py             # Routes API
│   └── services/
│       ├── __init__.py
│       ├── mathpix_service.py # Service Mathpix pour extraction LaTeX
│       ├── wolfram_service.py # Service WolframAlpha pour résolution
│       └── llm_service.py     # Service LLM pour explications
├── main.py                    # Application principale FastAPI
├── requirements.txt           # Dépendances Python
├── .env.example               # Exemple de configuration
└── README.md                  # Ce fichier
```

## API Endpoints

### `POST /api/latex`

Extrait le LaTeX depuis une image.

**Request**: FormData avec `image` (File)

**Response**:
```json
{
  "latex": "\\frac{1}{2}",
  "confidence": 0.95
}
```

### `POST /api/analyze`

Analyse complète : LaTeX → Résolution → Explication

**Request**: FormData avec `image` (File) et `latex` (string, optionnel)

**Response**:
```json
{
  "problem": "2x² + 5x - 3 = 0",
  "latex": "2x^2 + 5x - 3 = 0",
  "solution": "x = 0.5, x = -3",
  "steps": [
    {
      "title": "Use the quadratic formula",
      "description": "For an equation ax² + bx + c = 0...",
      "formula": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}",
      "explanation": "..."
    }
  ]
}
```

### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Services

### MathpixService

Service pour extraire le LaTeX depuis des images via l'API Mathpix.

- **Méthode principale**: `extract_latex(image_bytes)`
- **Retourne**: `{"latex": str, "confidence": float}`

### WolframService

Service pour résoudre des problèmes mathématiques via l'API WolframAlpha.

- **Méthode principale**: `solve(query)`
- **Retourne**: `{"solution": str, "steps": List[Dict]}`

### LLMService

Service pour générer des explications enrichies avec un LLM (OpenAI ou Gemini).

- **Méthode principale**: `generate_explanation(problem, solution, steps)`
- **Retourne**: `List[Dict]` avec les étapes enrichies
- **Configuration**: Via `LLM_PROVIDER` dans `.env`

## Gestion des erreurs

L'API gère les erreurs et retourne des messages clairs :

- `400`: Requête invalide
- `413`: Fichier trop volumineux
- `422`: Impossible de détecter d'équation
- `429`: Trop de requêtes (rate limiting)
- `500`: Erreur serveur

## Notes

- Les images acceptées : PNG, JPEG, GIF, WEBP
- Taille maximale par défaut : 10MB (configurable via `MAX_UPLOAD_SIZE`)
- Le LLM est optionnel : si les clés ne sont pas configurées, les étapes brutes de WolframAlpha sont retournées
- En mode développement, activez `DEBUG=true` pour le reload automatique

