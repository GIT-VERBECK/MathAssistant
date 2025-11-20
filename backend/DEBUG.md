# Guide de débogage - Math Assistant Backend

## 🔍 Diagnostic des erreurs

### 1. Vérifier les logs du backend

Quand vous lancez le backend avec `python main.py`, vous devriez voir des logs dans le terminal. 

**Erreurs courantes à vérifier :**

#### Erreur : "API credentials non configurées"
```
ValueError: OpenAI API key non configurée...
```
**Solution :** Vérifiez que votre fichier `backend/.env` contient :
```env
OPENAI_API_KEY=your_actual_key_here
WOLFRAM_APP_ID=your_actual_app_id_here
```

#### Erreur : "Invalid API key"
```
Exception: Clé API OpenAI invalide ou expirée.
```
**Solution :** Vérifiez que votre clé OpenAI est valide sur https://platform.openai.com/api-keys

#### Erreur : "WolframAlpha API credentials non configurées"
```
ValueError: WolframAlpha API credentials non configurées...
```
**Solution :** Ajoutez `WOLFRAM_APP_ID` dans votre fichier `.env`

#### Erreur CORS
```
Access to fetch at 'http://localhost:5000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solution :** Vérifiez que `CORS_ORIGINS` dans `backend/.env` contient l'URL de votre frontend :
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 2. Tester les endpoints directement

#### Test avec curl (PowerShell)

```powershell
# Test du health check
curl http://localhost:5000/health

# Test de l'extraction LaTeX (remplacez le chemin par une vraie image)
curl -X POST http://localhost:5000/api/latex -F "image=@chemin/vers/image.png"
```

#### Test avec le navigateur

1. Allez sur http://localhost:5000/docs
2. Testez l'endpoint `/api/latex` directement depuis Swagger
3. Regardez les erreurs détaillées dans la réponse

### 3. Vérifier la configuration

#### Fichier `.env` dans `backend/`

Vérifiez que le fichier existe et contient au minimum :

```env
# REQUIS
OPENAI_API_KEY=sk-...  # Votre vraie clé OpenAI
WOLFRAM_APP_ID=...     # Votre vrai App ID WolframAlpha

# Configuration serveur
HOST=0.0.0.0
PORT=5000
DEBUG=true  # Activez pour plus de logs

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 4. Vérifier les clés API

#### OpenAI
- Allez sur https://platform.openai.com/api-keys
- Vérifiez que votre clé est active
- Vérifiez que vous avez des crédits disponibles

#### WolframAlpha
- Allez sur https://products.wolframalpha.com/api/
- Vérifiez que votre App ID est valide
- Vérifiez votre quota

### 5. Mode DEBUG

Activez le mode DEBUG pour plus d'informations :

Dans `backend/.env` :
```env
DEBUG=true
```

Puis redémarrez le serveur. Vous verrez des logs détaillés de chaque requête.

### 6. Erreurs spécifiques

#### "Erreur lors de l'extraction LaTeX"
- Vérifiez que l'image est valide (PNG, JPEG, GIF, WEBP)
- Vérifiez que l'image contient bien une équation mathématique
- Vérifiez que l'image n'est pas trop grande (max 10MB)

#### "Impossible de détecter d'équation mathématique"
- L'image ne contient peut-être pas d'équation claire
- Essayez avec une image plus nette
- Vérifiez que l'équation est bien visible

#### "Trop de requêtes"
- Vous avez atteint la limite de votre quota API
- Attendez quelques minutes avant de réessayer
- Vérifiez votre quota sur les sites des APIs

### 7. Logs détaillés

Le backend log toutes les requêtes. Regardez le terminal où le backend tourne pour voir :
- Les requêtes entrantes
- Les erreurs détaillées
- Les appels aux APIs externes

Exemple de logs normaux :
```
INFO:     127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
INFO:     Extraction LaTeX demandée pour un fichier de 123456 bytes
INFO:     LaTeX extrait avec succès (confidence: 0.90)
```

## 🆘 Si rien ne fonctionne

1. **Vérifiez que le backend est bien lancé** : http://localhost:5000/health
2. **Vérifiez les logs du backend** dans le terminal
3. **Vérifiez la console du navigateur** (F12) pour les erreurs CORS ou réseau
4. **Testez avec Swagger** : http://localhost:5000/docs
5. **Vérifiez votre fichier `.env`** dans le dossier `backend/`

## 📝 Checklist de débogage

- [ ] Le backend répond sur http://localhost:5000/health
- [ ] Le fichier `backend/.env` existe et contient les clés API
- [ ] Les clés API sont valides (testées sur les sites officiels)
- [ ] CORS_ORIGINS contient l'URL du frontend
- [ ] Les logs du backend montrent des erreurs spécifiques
- [ ] Le frontend pointe vers http://localhost:5000/api
- [ ] Pas d'erreurs dans la console du navigateur (F12)

