# Déploiement rapide MathAssistant

Guide ultra-rapide pour déployer l'application en 10 minutes.

## 🚀 Déploiement en 3 étapes

### 1️⃣ Backend sur Render (5 min)

1. Allez sur [render.com](https://render.com) et connectez votre compte GitHub
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Sélectionnez votre repository `MathAssistant`
4. Render détectera automatiquement `render.yaml`
5. Cliquez sur **"Apply"**
6. Dans **"Environment"**, ajoutez :
   ```
   WOLFRAM_APP_ID=votre_wolfram_app_id
   OPENAI_API_KEY=votre_openai_api_key
   CORS_ORIGINS=https://votre-app.vercel.app
   ```
7. Notez l'URL du backend (ex: `https://mathassistant-backend.onrender.com`)

### 2️⃣ Frontend sur Vercel (3 min)

1. Allez sur [vercel.com](https://vercel.com) et connectez votre compte GitHub
2. Cliquez sur **"Add New..."** → **"Project"**
3. Importez votre repository `MathAssistant`
4. Dans **"Environment Variables"**, ajoutez :
   ```
   VITE_API_BASE_URL=https://votre-backend.onrender.com/api
   ```
   (Remplacez par l'URL réelle de votre backend)
5. Cliquez sur **"Deploy"**
6. Notez l'URL du frontend (ex: `https://mathassistant.vercel.app`)

### 3️⃣ Mettre à jour CORS (2 min)

1. Retournez sur Render
2. Mettez à jour `CORS_ORIGINS` avec l'URL Vercel :
   ```
   CORS_ORIGINS=https://mathassistant.vercel.app
   ```
3. Redéployez le backend

## ✅ Vérification

- Backend : Visitez `https://votre-backend.onrender.com/health`
- Frontend : Visitez `https://votre-app.vercel.app`
- Testez l'upload d'une image avec une équation mathématique

## 📚 Documentation complète

Pour plus de détails, consultez :
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Guide complet
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Checklist détaillée

## ⚠️ Notes importantes

- Le plan gratuit Render peut s'endormir après 15 min d'inactivité
- Le premier démarrage peut prendre 30-60 secondes
- Assurez-vous d'avoir toutes vos clés API avant de commencer

