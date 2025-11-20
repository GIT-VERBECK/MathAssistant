# Guide de test - Math Assistant

## ✅ Étape 1 : Vérifier que le backend fonctionne

Le serveur backend devrait être lancé sur `http://localhost:5000`

### Test rapide dans le navigateur :

1. Ouvrez votre navigateur et allez sur : **http://localhost:5000/health**
   - Vous devriez voir : `{"status":"healthy","version":"1.0.0"}`

2. Documentation API : **http://localhost:5000/docs**
   - Vous devriez voir la documentation Swagger avec les endpoints disponibles

### Test avec curl (optionnel) :

```bash
# Test du health check
curl http://localhost:5000/health

# Test de la route principale
curl http://localhost:5000/
```

## ✅ Étape 2 : Lancer le frontend

Dans un **nouveau terminal**, allez dans le dossier du projet :

```bash
cd C:\wamp64\www\MathAssistant
npm run dev
```

Le frontend sera accessible sur : **http://localhost:5173** (ou un autre port si 5173 est occupé)

## ✅ Étape 3 : Tester l'application complète

### Test 1 : Upload d'image et extraction LaTeX

1. Ouvrez **http://localhost:5173** dans votre navigateur
2. Cliquez sur "Choisir une image" ou utilisez la caméra
3. Sélectionnez une image avec une équation mathématique (ex: `x² + 5x - 3 = 0`)
4. Cliquez sur "Extraire le LaTeX"
5. Vérifiez que le LaTeX est extrait correctement

### Test 2 : Analyse complète

1. Après l'extraction LaTeX, cliquez sur "Confirmer et résoudre"
2. L'application devrait :
   - Extraire le LaTeX (si pas déjà fait)
   - Résoudre avec WolframAlpha
   - Générer des explications avec OpenAI
   - Afficher les étapes de résolution

### Test 3 : Export PDF

1. Après avoir obtenu les résultats
2. Cliquez sur "Télécharger en PDF"
3. Vérifiez que le PDF est généré et téléchargé

## 🔧 Dépannage

### Le frontend ne peut pas se connecter au backend

**Vérifiez :**
1. Le backend est bien lancé sur le port 5000
2. Le fichier `.env` à la racine contient : `VITE_API_BASE_URL=http://localhost:5000/api`
3. Redémarrez le serveur frontend après avoir créé/modifié le `.env`

### Erreur CORS

Si vous voyez une erreur CORS dans la console :
- Vérifiez que `CORS_ORIGINS` dans `backend/.env` contient l'URL du frontend
- Par défaut : `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

### Erreur "API credentials non configurées"

Vérifiez que votre fichier `backend/.env` contient :
- `OPENAI_API_KEY=your_key_here`
- `WOLFRAM_APP_ID=your_app_id_here`

### L'image n'est pas reconnue

- Assurez-vous que l'image contient bien une équation mathématique claire
- Formats supportés : PNG, JPEG, GIF, WEBP
- Taille maximale : 10MB

## 📝 Checklist de test

- [ ] Backend accessible sur http://localhost:5000/health
- [ ] Documentation Swagger accessible sur http://localhost:5000/docs
- [ ] Frontend accessible sur http://localhost:5173
- [ ] Upload d'image fonctionne
- [ ] Extraction LaTeX fonctionne
- [ ] Résolution avec WolframAlpha fonctionne
- [ ] Génération d'explications fonctionne
- [ ] Export PDF fonctionne
- [ ] Pas d'erreurs dans la console du navigateur
- [ ] Pas d'erreurs dans les logs du backend

## 🎉 Si tout fonctionne

Félicitations ! Votre application Math Assistant est opérationnelle !

Vous pouvez maintenant :
- Résoudre des équations mathématiques à partir d'images
- Obtenir des explications détaillées
- Exporter les solutions en PDF

