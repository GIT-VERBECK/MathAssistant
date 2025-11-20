# Guide de démarrage rapide - Backend Math Assistant

## 🚀 Installation rapide

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurer l'environnement

Créez un fichier `.env` à la racine du dossier `backend` :

```bash
# Windows
copy env.example.txt .env

# Linux/Mac
cp env.example.txt .env
```

### 3. Remplir les clés API dans `.env`

**Minimum requis pour fonctionner :**
- `OPENAI_API_KEY` - **OBLIGATOIRE** (pour extraction LaTeX depuis images et explications)
- `WOLFRAM_APP_ID` - **OBLIGATOIRE** (pour la résolution)

**Optionnel :**
- `MATHPIX_APP_ID` et `MATHPIX_APP_KEY` - Si configuré, sera utilisé à la place d'OpenAI pour l'extraction LaTeX (plus précis)
- `GEMINI_API_KEY` - Alternative à OpenAI pour les explications (si `LLM_PROVIDER=gemini`)

**Note :** 
- Si Mathpix n'est pas configuré, OpenAI Vision sera utilisé automatiquement pour extraire le LaTeX
- Si les clés LLM ne sont pas configurées, le backend fonctionnera mais utilisera les étapes brutes de WolframAlpha sans enrichissement

### 4. Lancer le serveur

```bash
# Méthode 1 : Avec le script
python run.py

# Méthode 2 : Directement
python main.py

# Méthode 3 : Avec uvicorn
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

Le serveur sera accessible sur : **http://localhost:5000**

### 5. Vérifier que ça fonctionne

- **Documentation API** : http://localhost:5000/docs
- **Health check** : http://localhost:5000/health

## ✅ Vérification rapide

1. **Le serveur démarre sans erreur** ✓
2. **Le endpoint `/health` retourne `{"status": "healthy"}`** ✓
3. **La documentation Swagger est accessible sur `/docs`** ✓
4. **Le frontend peut se connecter** (vérifier CORS_ORIGINS dans `.env`) ✓

## 🔧 Dépannage

### Erreur : "Module not found"
```bash
pip install -r requirements.txt
```

### Erreur : "Credentials non configurées"
Vérifiez que votre fichier `.env` contient bien les clés API nécessaires.

### Erreur : "Port already in use"
Changez le `PORT` dans le fichier `.env` ou arrêtez l'application qui utilise le port 5000.

### Le frontend ne peut pas se connecter
Vérifiez que `CORS_ORIGINS` dans `.env` contient l'URL de votre frontend (ex: `http://localhost:3000`).

## 📝 Prochaines étapes

Une fois le backend lancé :
1. Configurez votre frontend pour pointer vers `http://localhost:5000/api`
2. Testez l'upload d'une image avec une équation mathématique
3. Vérifiez les logs pour identifier d'éventuels problèmes

## 🔗 Liens utiles

- **Mathpix** : https://mathpix.com/ (compte gratuit : 1000 requêtes/mois)
- **WolframAlpha** : https://products.wolframalpha.com/api/ (essai gratuit disponible)
- **OpenAI** : https://platform.openai.com/api-keys
- **Gemini** : https://aistudio.google.com/app/apikey

