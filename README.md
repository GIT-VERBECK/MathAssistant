# Math Assistant - Frontend

Application React pour résoudre des problèmes mathématiques à partir d'images, avec rendu LaTeX et export PDF.

## Technologies

- **React 19** + **Vite**
- **KaTeX** - Rendu des équations mathématiques LaTeX
- **jsPDF** - Génération de PDF
- **ESLint** - Linting du code

## Installation

```bash
npm install
```

## Configuration

Créez un fichier `.env` à la racine du projet avec :

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## Développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## Build

```bash
npm run build
```

## Fonctionnalités

### ✅ Implémentées

- **Upload d'image** : Upload de fichier ou capture via caméra
- **Extraction LaTeX** : Interface pour extraire le LaTeX depuis l'image (via API backend)
- **Confirmation LaTeX** : Page de confirmation avant résolution
- **Rendu LaTeX** : Affichage des équations mathématiques avec KaTeX
- **Résolution** : Interface pour résoudre le problème (via API backend)
- **Affichage des résultats** : Étapes de résolution avec rendu LaTeX
- **Export PDF** : Téléchargement de la solution en PDF
- **Gestion d'erreurs** : Messages d'erreur clairs et user-friendly
- **Design responsive** : Mobile-first, adapté à tous les écrans

### ✅ Backend implémenté

- **Extraction LaTeX** : Connexion avec l'API Mathpix pour extraire le LaTeX depuis les images
- **Résolution** : Connexion avec l'API WolframAlpha pour résoudre les problèmes mathématiques
- **Explications** : Génération d'explications enrichies avec OpenAI ou Gemini
- **Validation** : Validation sécurisée des fichiers uploadés
- **Gestion d'erreurs** : Gestion robuste des erreurs avec messages clairs
- **Logging** : Logging détaillé pour le débogage

## Structure du projet

```
src/
├── components/
│   ├── LaTeXRenderer.jsx    # Composant pour afficher LaTeX
│   ├── ErrorDisplay.jsx     # Affichage des erreurs
│   └── ErrorDisplay.css
├── services/
│   └── api.js               # Service API pour communiquer avec le backend
├── utils/
│   └── pdfGenerator.js      # Générateur de PDF
├── App.jsx                   # Composant principal
├── App.css                   # Styles principaux
└── main.jsx                  # Point d'entrée
```

## API Backend attendue

Le frontend s'attend à un backend avec les endpoints suivants :

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

## Linting

```bash
npm run lint
```

## Notes

- Le frontend est prêt à communiquer avec le backend
- Les appels API sont gérés avec gestion d'erreurs complète
- Le rendu LaTeX fonctionne avec KaTeX
- L'export PDF fonctionne (version simplifiée sans rendu LaTeX dans le PDF)
- **Le backend est complètement implémenté** (voir `backend/README.md`)

## 🚀 Démarrage rapide

### 1. Backend (dans un terminal)

```bash
cd backend
python main.py
```

Le backend sera sur : **http://localhost:5000**

### 2. Frontend (dans un autre terminal)

```bash
npm run dev
```

Le frontend sera sur : **http://localhost:5173**

### 3. Tester

Ouvrez http://localhost:5173 et testez avec une image contenant une équation mathématique !

**Voir `TESTING.md` pour un guide de test complet.**

## Structure complète du projet

```
MathAssistant/
├── src/                    # Frontend React
│   ├── components/
│   ├── services/
│   └── utils/
├── backend/                # Backend FastAPI
│   ├── app/
│   │   ├── routes/        # Routes API
│   │   ├── services/      # Services (Mathpix, WolframAlpha, LLM)
│   │   ├── utils/         # Utilitaires (validation, gestion d'erreurs)
│   │   └── config.py      # Configuration
│   ├── main.py            # Application principale
│   ├── requirements.txt   # Dépendances Python
│   └── README.md          # Documentation backend
└── README.md              # Ce fichier
```

## 🚀 Déploiement

L'application est configurée pour être déployée sur :
- **Frontend** : [Vercel](https://vercel.com/)
- **Backend** : [Render](https://render.com/)

### Guides de déploiement

- 🚀 **[Déploiement rapide (10 min)](./QUICK_DEPLOY.md)** - Pour les impatients
- 📖 **[Guide complet](./DEPLOYMENT.md)** - Guide détaillé pas-à-pas
- ✅ **[Checklist de déploiement](./DEPLOYMENT_CHECKLIST.md)** - Pour suivre votre progression

### Déploiement rapide

#### Backend (Render)

1. Connectez votre repository GitHub à Render
2. Render détectera automatiquement le fichier `render.yaml`
3. Configurez les variables d'environnement (voir `DEPLOYMENT.md`)
4. Déployez

#### Frontend (Vercel)

1. Connectez votre repository GitHub à Vercel
2. Vercel détectera automatiquement le projet Vite
3. Configurez la variable d'environnement `VITE_API_BASE_URL` avec l'URL de votre backend Render
4. Déployez

### Variables d'environnement requises

**Backend (Render)** :
- `WOLFRAM_APP_ID` (requis)
- `OPENAI_API_KEY` (requis)
- `CORS_ORIGINS` (requis - URL du frontend Vercel)

**Frontend (Vercel)** :
- `VITE_API_BASE_URL` (requis - URL du backend Render avec `/api`)

### CI/CD

Le projet inclut un workflow GitHub Actions (`.github/workflows/ci.yml`) qui :
- Lint le code frontend et backend
- Vérifie que les builds fonctionnent
- S'exécute automatiquement sur chaque push et pull request

### Liens utiles

- 📖 [Guide de déploiement complet](./DEPLOYMENT.md)
- 🔧 [Configuration backend](./backend/README.md)
- 🧪 [Guide de test](./TESTING.md)
