# Étapes de déploiement - Guide pratique

## ✅ Étape 1 : Pousser le code sur GitHub

Dans votre terminal, à la racine du projet `MathAssistant`, exécutez :

```bash
# Vérifier que vous êtes dans le bon dossier
cd C:\wamp64\www\MathAssistant

# Initialiser git si pas déjà fait (ou vérifier le statut)
git status

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Créer un commit
git commit -m "Configuration complète pour déploiement Vercel + Render"

# Ajouter le remote GitHub (si pas déjà fait)
git remote add origin https://github.com/GIT-VERBECK/MathAssistant.git

# Pousser sur GitHub
git branch -M main
git push -u origin main
```

**Note** : Si vous avez déjà un remote, utilisez plutôt :
```bash
git remote set-url origin https://github.com/GIT-VERBECK/MathAssistant.git
git push -u origin main
```

---

## ✅ Étape 2 : Déployer le Backend sur Render

### 2.1 Connecter Render à GitHub

1. Allez sur [render.com](https://render.com) et connectez-vous
2. Cliquez sur **"New +"** en haut à droite
3. Sélectionnez **"Blueprint"**
4. Connectez votre compte GitHub si ce n'est pas déjà fait
5. Sélectionnez le repository **`GIT-VERBECK/MathAssistant`**
6. Render détectera automatiquement le fichier `render.yaml`
7. Cliquez sur **"Apply"**

### 2.2 Configurer les variables d'environnement

**IMPORTANT** : Vous devez avoir vos clés API avant de continuer :
- **WOLFRAM_APP_ID** : [Obtenir ici](https://products.wolframalpha.com/api/)
- **OPENAI_API_KEY** : [Obtenir ici](https://platform.openai.com/api-keys)

Dans le dashboard Render, après la création du service :

1. Allez dans l'onglet **"Environment"**
2. Ajoutez ces variables (cliquez sur **"Add Environment Variable"** pour chacune) :

```
WOLFRAM_APP_ID=votre_wolfram_app_id_ici
OPENAI_API_KEY=votre_openai_api_key_ici
CORS_ORIGINS=https://mathassistant.vercel.app
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
DEBUG=false
```

**Note** : Pour `CORS_ORIGINS`, mettez une URL temporaire pour l'instant. Vous la mettrez à jour après avoir déployé le frontend.

3. Cliquez sur **"Save Changes"**
4. Render va automatiquement redéployer

### 2.3 Noter l'URL du backend

Une fois le déploiement terminé (peut prendre 2-5 minutes) :

1. Dans le dashboard Render, vous verrez l'URL de votre service
2. Elle ressemblera à : `https://mathassistant-backend.onrender.com`
3. **Notez cette URL**, vous en aurez besoin pour le frontend
4. Testez l'endpoint de santé : `https://votre-backend.onrender.com/health`
   - Vous devriez voir : `{"status":"healthy","version":"1.0.0"}`

---

## ✅ Étape 3 : Déployer le Frontend sur Vercel

### 3.1 Créer un compte Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Cliquez sur **"Sign Up"**
3. Choisissez **"Continue with GitHub"**
4. Autorisez Vercel à accéder à vos repositories

### 3.2 Importer le projet

1. Dans le dashboard Vercel, cliquez sur **"Add New..."** → **"Project"**
2. Sélectionnez le repository **`GIT-VERBECK/MathAssistant`**
3. Vercel détectera automatiquement que c'est un projet Vite
4. Vérifiez la configuration :
   - **Framework Preset** : Vite
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
   - **Install Command** : `npm install`

### 3.3 Configurer les variables d'environnement

**AVANT de cliquer sur "Deploy"** :

1. Cliquez sur **"Environment Variables"**
2. Ajoutez cette variable :

```
VITE_API_BASE_URL=https://votre-backend.onrender.com/api
```

**Remplacez `votre-backend.onrender.com` par l'URL réelle de votre backend Render** (notée à l'étape 2.3)

3. Cliquez sur **"Add"**
4. Cliquez sur **"Deploy"**

### 3.4 Noter l'URL du frontend

Une fois le déploiement terminé (1-2 minutes) :

1. Vercel vous donnera une URL
2. Elle ressemblera à : `https://mathassistant.vercel.app` ou `https://mathassistant-git-main.vercel.app`
3. **Notez cette URL**, vous en aurez besoin pour mettre à jour CORS

---

## ✅ Étape 4 : Mettre à jour CORS sur Render

Maintenant que vous avez l'URL du frontend Vercel :

1. Retournez sur [render.com](https://render.com)
2. Allez dans votre service backend
3. Cliquez sur l'onglet **"Environment"**
4. Trouvez la variable `CORS_ORIGINS`
5. Mettez à jour avec l'URL Vercel réelle :

```
CORS_ORIGINS=https://mathassistant.vercel.app,https://mathassistant-git-main.vercel.app
```

**Note** : Vercel peut générer plusieurs URLs (production, preview). Ajoutez-les toutes séparées par des virgules.

6. Cliquez sur **"Save Changes"**
7. Render redéploiera automatiquement

---

## ✅ Étape 5 : Vérification finale

### Tester le backend
- Visitez : `https://votre-backend.onrender.com/health`
- Vous devriez voir : `{"status":"healthy","version":"1.0.0"}`

### Tester le frontend
- Visitez : `https://votre-app.vercel.app`
- L'application devrait se charger
- Testez l'upload d'une image avec une équation mathématique

### Vérifier la connexion
- Ouvrez la console du navigateur (F12)
- Essayez d'uploader une image
- Vérifiez qu'il n'y a pas d'erreurs CORS

---

## 🆘 En cas de problème

### Le backend ne démarre pas
- Vérifiez les logs Render (onglet "Logs")
- Vérifiez que toutes les variables d'environnement sont correctement configurées
- Vérifiez que vos clés API sont valides

### Erreur CORS
- Vérifiez que `CORS_ORIGINS` contient bien l'URL Vercel exacte
- Vérifiez qu'il n'y a pas d'espaces dans `CORS_ORIGINS`
- Redéployez le backend après modification de CORS

### Le frontend ne peut pas se connecter au backend
- Vérifiez que `VITE_API_BASE_URL` est correctement configuré dans Vercel
- Vérifiez que l'URL se termine par `/api`
- Vérifiez que le backend est bien démarré (testez `/health`)

---

## 📝 Résumé des URLs

Notez vos URLs ici :

- **Backend Render** : `https://________________.onrender.com`
- **Frontend Vercel** : `https://________________.vercel.app`
- **Health Check** : `https://________________.onrender.com/health`

---

**Félicitations ! 🎉** Votre application est maintenant déployée !

