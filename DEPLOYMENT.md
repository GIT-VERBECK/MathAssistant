# Guide de déploiement MathAssistant

Ce guide vous accompagne dans le déploiement de l'application MathAssistant sur Vercel (frontend) et Render (backend).

> 💡 **Astuce** : Utilisez [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) pour suivre votre progression étape par étape.

## Table des matières

1. [Prérequis](#prérequis)
2. [Déploiement du Backend sur Render](#déploiement-du-backend-sur-render)
3. [Déploiement du Frontend sur Vercel](#déploiement-du-frontend-sur-vercel)
4. [Configuration GitHub](#configuration-github)
5. [Variables d'environnement](#variables-denvironnement)
6. [Dépannage](#dépannage)

## Prérequis

- Un compte GitHub
- Un compte Vercel (gratuit)
- Un compte Render (gratuit)
- Les clés API suivantes :
  - **WOLFRAM_APP_ID** (requis) - [Obtenir sur WolframAlpha](https://products.wolframalpha.com/api/)
  - **OPENAI_API_KEY** (requis) - [Obtenir sur OpenAI](https://platform.openai.com/api-keys)
  - **MATHPIX_APP_ID** et **MATHPIX_APP_KEY** (optionnel) - [Obtenir sur Mathpix](https://mathpix.com/)
  - **GEMINI_API_KEY** (optionnel, si vous utilisez Gemini) - [Obtenir sur Google AI Studio](https://aistudio.google.com/app/apikey)

## Déploiement du Backend sur Render

### Étape 1 : Préparer le repository GitHub

1. Assurez-vous que votre code est poussé sur GitHub
2. Vérifiez que le fichier `render.yaml` est présent à la racine du projet

### Étape 2 : Créer un service sur Render

1. Connectez-vous à [Render](https://render.com/)
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Connectez votre repository GitHub
4. Render détectera automatiquement le fichier `render.yaml`
5. Cliquez sur **"Apply"**

### Étape 3 : Configurer les variables d'environnement

Dans le dashboard Render, allez dans **"Environment"** et configurez les variables suivantes :

#### Variables requises :

```
WOLFRAM_APP_ID=votre_wolfram_app_id
OPENAI_API_KEY=votre_openai_api_key
CORS_ORIGINS=https://votre-app.vercel.app,https://votre-app-git-main.vercel.app
```

#### Variables optionnelles :

```
MATHPIX_APP_ID=votre_mathpix_app_id (si vous utilisez Mathpix)
MATHPIX_APP_KEY=votre_mathpix_app_key (si vous utilisez Mathpix)
GEMINI_API_KEY=votre_gemini_api_key (si vous utilisez Gemini)
LLM_PROVIDER=openai (ou "gemini")
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-1.5-flash
```

**Note importante** : Pour `CORS_ORIGINS`, vous devrez mettre à jour cette variable après avoir déployé le frontend sur Vercel pour obtenir l'URL exacte.

### Étape 4 : Déployer

1. Render commencera automatiquement le déploiement
2. Attendez que le déploiement soit terminé
3. Notez l'URL de votre backend (ex: `https://mathassistant-backend.onrender.com`)

### Étape 5 : Vérifier le déploiement

Visitez `https://votre-backend.onrender.com/health` pour vérifier que le backend fonctionne.

## Déploiement du Frontend sur Vercel

### Étape 1 : Connecter le repository

1. Connectez-vous à [Vercel](https://vercel.com/)
2. Cliquez sur **"Add New..."** → **"Project"**
3. Importez votre repository GitHub
4. Vercel détectera automatiquement que c'est un projet Vite

### Étape 2 : Configurer le projet

Vercel devrait détecter automatiquement :
- **Framework Preset** : Vite
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm install`

Si ce n'est pas le cas, configurez manuellement ces valeurs.

### Étape 3 : Configurer les variables d'environnement

Dans les paramètres du projet Vercel, allez dans **"Environment Variables"** et ajoutez :

```
VITE_API_BASE_URL=https://votre-backend.onrender.com/api
```

**Important** : Remplacez `https://votre-backend.onrender.com` par l'URL réelle de votre backend Render.

### Étape 4 : Déployer

1. Cliquez sur **"Deploy"**
2. Attendez que le déploiement soit terminé
3. Notez l'URL de votre frontend (ex: `https://mathassistant.vercel.app`)

### Étape 5 : Mettre à jour CORS sur Render

Retournez sur Render et mettez à jour la variable `CORS_ORIGINS` avec l'URL Vercel :

```
CORS_ORIGINS=https://mathassistant.vercel.app,https://mathassistant-git-main.vercel.app
```

Vercel génère plusieurs URLs (production, preview, etc.). Ajoutez toutes les URLs nécessaires séparées par des virgules.

### Étape 6 : Redéployer le backend

Après avoir mis à jour `CORS_ORIGINS`, redéployez le backend sur Render pour que les changements prennent effet.

## Configuration GitHub

### Workflow CI/CD

Le fichier `.github/workflows/ci.yml` est déjà configuré pour :
- Linter le code frontend et backend
- Vérifier que les builds fonctionnent
- Exécuter des tests de base

Le workflow s'exécute automatiquement sur chaque push et pull request.

### Secrets GitHub (optionnel)

Si vous souhaitez utiliser des secrets GitHub pour les tests CI, ajoutez-les dans **Settings → Secrets and variables → Actions** :

- `VITE_API_BASE_URL` : URL du backend pour les tests

## Variables d'environnement

### Frontend (Vercel)

| Variable | Description | Requis |
|----------|-------------|--------|
| `VITE_API_BASE_URL` | URL complète du backend (avec `/api`) | Oui |

**Exemple** : `https://mathassistant-backend.onrender.com/api`

### Backend (Render)

| Variable | Description | Requis |
|----------|-------------|--------|
| `WOLFRAM_APP_ID` | Clé API WolframAlpha | Oui |
| `OPENAI_API_KEY` | Clé API OpenAI | Oui |
| `CORS_ORIGINS` | Origines autorisées (séparées par virgules) | Oui |
| `LLM_PROVIDER` | `openai` ou `gemini` | Non (défaut: `openai`) |
| `OPENAI_MODEL` | Modèle OpenAI à utiliser | Non (défaut: `gpt-4o-mini`) |
| `GEMINI_API_KEY` | Clé API Gemini (si LLM_PROVIDER=gemini) | Conditionnel |
| `GEMINI_MODEL` | Modèle Gemini à utiliser | Non (défaut: `gemini-1.5-flash`) |
| `MATHPIX_APP_ID` | ID Mathpix (optionnel) | Non |
| `MATHPIX_APP_KEY` | Clé Mathpix (optionnel) | Non |
| `DEBUG` | Mode debug | Non (défaut: `false`) |
| `MAX_UPLOAD_SIZE` | Taille max upload en bytes | Non (défaut: `10485760`) |

## Dépannage

### Le frontend ne peut pas se connecter au backend

1. **Vérifiez `VITE_API_BASE_URL`** : Assurez-vous que la variable est correctement configurée dans Vercel
2. **Vérifiez CORS** : Assurez-vous que l'URL du frontend est dans `CORS_ORIGINS` sur Render
3. **Vérifiez l'URL du backend** : Testez l'endpoint `/health` directement dans le navigateur

### Erreur 500 sur le backend

1. **Vérifiez les logs Render** : Allez dans "Logs" sur le dashboard Render
2. **Vérifiez les clés API** : Assurez-vous que toutes les clés API sont correctement configurées
3. **Vérifiez les variables d'environnement** : Utilisez `render.yaml` comme référence

### Le build échoue sur Vercel

1. **Vérifiez les logs de build** : Consultez les logs détaillés dans Vercel
2. **Vérifiez `package.json`** : Assurez-vous que tous les scripts sont corrects
3. **Vérifiez `vercel.json`** : La configuration doit correspondre à votre setup

### Le backend ne démarre pas sur Render

1. **Vérifiez `render.yaml`** : La configuration doit être correcte
2. **Vérifiez `backend/start.sh`** : Le script doit être exécutable
3. **Vérifiez les logs** : Les erreurs de démarrage apparaissent dans les logs Render

### CORS errors

1. **Vérifiez `CORS_ORIGINS`** : Doit inclure toutes les URLs Vercel (production + preview)
2. **Format correct** : URLs séparées par des virgules, sans espaces
3. **Redéployez** : Après modification de CORS_ORIGINS, redéployez le backend

## Commandes utiles

### Développement local

```bash
# Frontend
npm run dev

# Backend
cd backend
python -m uvicorn main:app --reload
```

### Build local

```bash
# Frontend
npm run build
npm run preview

# Backend
cd backend
python -m uvicorn main:app
```

## Support

Pour plus d'aide :
- [Documentation Vercel](https://vercel.com/docs)
- [Documentation Render](https://render.com/docs)
- [Documentation GitHub Actions](https://docs.github.com/en/actions)

## Notes importantes

1. **Plan gratuit Render** : Le service peut s'endormir après 15 minutes d'inactivité. Le premier démarrage peut prendre 30-60 secondes.
2. **Limites Vercel** : Le plan gratuit a des limites sur la bande passante et les builds.
3. **Sécurité** : Ne commitez jamais vos clés API dans le repository. Utilisez toujours les variables d'environnement.

