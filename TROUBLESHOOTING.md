# Guide de résolution des problèmes - Math Assistant

## 🔴 Erreur : "Erreur serveur. Veuillez réessayer plus tard."

Cette erreur indique que le backend a rencontré un problème (code HTTP 500). Suivez ces étapes pour diagnostiquer :

### Étape 1 : Vérifier les logs du backend

**Dans le terminal où le backend tourne**, regardez les messages d'erreur. Vous devriez voir quelque chose comme :

```
ERROR:    ValueError lors de l'extraction LaTeX: OpenAI API key non configurée...
```

ou

```
ERROR:    Erreur inattendue lors de l'extraction LaTeX: ...
```

### Étape 2 : Vérifier la configuration

#### 1. Le fichier `.env` existe-t-il ?

Vérifiez que vous avez un fichier `backend/.env` (pas `backend/env.example.txt`)

#### 2. Le fichier `.env` contient-il les clés ?

Ouvrez `backend/.env` et vérifiez qu'il contient au minimum :

```env
OPENAI_API_KEY=sk-votre-vraie-cle-ici
WOLFRAM_APP_ID=votre-app-id-ici
```

**⚠️ Important :** 
- Les clés ne doivent PAS être entre guillemets
- Il ne doit pas y avoir d'espaces autour du `=`
- Les valeurs vides (`OPENAI_API_KEY=`) causeront des erreurs

#### 3. Redémarrer le backend après modification

Après avoir modifié le fichier `.env`, **redémarrez le serveur backend** :
1. Arrêtez le serveur (Ctrl+C)
2. Relancez : `python main.py`

### Étape 3 : Tester directement le backend

#### Test 1 : Health check

Ouvrez dans votre navigateur : **http://localhost:5000/health**

Vous devriez voir : `{"status":"healthy","version":"1.0.0"}`

Si ça ne fonctionne pas, le backend n'est pas lancé correctement.

#### Test 2 : Documentation Swagger

Ouvrez : **http://localhost:5000/docs**

Vous devriez voir la documentation de l'API. Testez l'endpoint `/api/latex` directement depuis Swagger pour voir l'erreur exacte.

### Étape 4 : Erreurs courantes et solutions

#### ❌ "OpenAI API key non configurée"

**Cause :** La clé OpenAI n'est pas dans le fichier `.env` ou est vide.

**Solution :**
1. Vérifiez que `OPENAI_API_KEY=sk-...` est dans `backend/.env`
2. Vérifiez que la clé est valide sur https://platform.openai.com/api-keys
3. Redémarrez le backend

#### ❌ "WolframAlpha API credentials non configurées"

**Cause :** L'App ID WolframAlpha n'est pas configuré.

**Solution :**
1. Ajoutez `WOLFRAM_APP_ID=votre-app-id` dans `backend/.env`
2. Obtenez votre App ID sur https://products.wolframalpha.com/api/
3. Redémarrez le backend

#### ❌ "Clé API OpenAI invalide ou expirée"

**Cause :** La clé OpenAI est invalide, expirée, ou vous n'avez plus de crédits.

**Solution :**
1. Vérifiez votre clé sur https://platform.openai.com/api-keys
2. Vérifiez vos crédits sur https://platform.openai.com/account/billing
3. Générez une nouvelle clé si nécessaire

#### ❌ "Trop de requêtes"

**Cause :** Vous avez atteint la limite de votre quota API.

**Solution :**
- Attendez quelques minutes
- Vérifiez votre quota sur les sites des APIs
- Pour OpenAI : https://platform.openai.com/account/usage

#### ❌ Erreur CORS

**Cause :** Le frontend ne peut pas communiquer avec le backend à cause de CORS.

**Solution :**
Dans `backend/.env`, vérifiez que :
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```
Puis redémarrez le backend.

### Étape 5 : Activer le mode DEBUG

Pour voir plus de détails dans les logs, activez le mode DEBUG :

Dans `backend/.env` :
```env
DEBUG=true
```

Puis redémarrez le backend. Vous verrez des logs beaucoup plus détaillés.

### Étape 6 : Vérifier la console du navigateur

1. Ouvrez les outils de développement (F12)
2. Allez dans l'onglet "Console"
3. Regardez les erreurs affichées
4. Allez dans l'onglet "Network" pour voir les requêtes HTTP et leurs réponses

### 📋 Checklist de diagnostic

- [ ] Le backend répond sur http://localhost:5000/health
- [ ] Le fichier `backend/.env` existe (pas juste `env.example.txt`)
- [ ] `OPENAI_API_KEY` est défini dans `.env` avec une vraie clé (commence par `sk-`)
- [ ] `WOLFRAM_APP_ID` est défini dans `.env` avec un vrai App ID
- [ ] Pas d'espaces autour du `=` dans `.env`
- [ ] Le backend a été redémarré après modification de `.env`
- [ ] Les clés API sont valides (testées sur les sites officiels)
- [ ] Les logs du backend montrent des erreurs spécifiques
- [ ] La console du navigateur (F12) ne montre pas d'erreurs CORS

### 🆘 Si le problème persiste

1. **Copiez les logs du backend** (les messages d'erreur dans le terminal)
2. **Copiez les erreurs de la console du navigateur** (F12 → Console)
3. **Vérifiez que vous avez bien :**
   - Un fichier `backend/.env` (pas `env.example.txt`)
   - Les clés API correctement formatées
   - Le backend redémarré après chaque modification

### 💡 Astuce

Pour tester rapidement si vos clés fonctionnent, testez l'endpoint directement depuis Swagger :
1. Allez sur http://localhost:5000/docs
2. Cliquez sur `POST /api/latex`
3. Cliquez sur "Try it out"
4. Uploadez une image
5. Regardez la réponse - elle vous dira exactement quelle est l'erreur

