# Checklist de déploiement MathAssistant

Utilisez cette checklist pour vous assurer que tous les éléments sont en place avant et après le déploiement.

## Pré-déploiement

### Repository GitHub
- [ ] Code poussé sur GitHub
- [ ] `.gitignore` configuré correctement (exclut `.env`, `__pycache__`, etc.)
- [ ] Tous les fichiers de configuration présents :
  - [ ] `vercel.json`
  - [ ] `render.yaml`
  - [ ] `backend/start.sh`
  - [ ] `.github/workflows/ci.yml`

### Clés API
- [ ] **WOLFRAM_APP_ID** obtenu et prêt
- [ ] **OPENAI_API_KEY** obtenu et prêt
- [ ] **MATHPIX_APP_ID** et **MATHPIX_APP_KEY** (optionnel)
- [ ] **GEMINI_API_KEY** (optionnel, si utilisé)

## Déploiement Backend (Render)

### Configuration Render
- [ ] Compte Render créé
- [ ] Repository GitHub connecté à Render
- [ ] Service créé depuis `render.yaml` (Blueprint)
- [ ] Plan sélectionné (Free ou autre)

### Variables d'environnement Render
- [ ] `WOLFRAM_APP_ID` configuré
- [ ] `OPENAI_API_KEY` configuré
- [ ] `CORS_ORIGINS` configuré (mettre à jour après déploiement frontend)
- [ ] `LLM_PROVIDER` configuré (défaut: `openai`)
- [ ] `OPENAI_MODEL` configuré (défaut: `gpt-4o-mini`)
- [ ] `DEBUG` configuré à `false`
- [ ] `MATHPIX_APP_ID` et `MATHPIX_APP_KEY` (si utilisé)
- [ ] `GEMINI_API_KEY` et `GEMINI_MODEL` (si utilisé)

### Vérification Backend
- [ ] Déploiement réussi sur Render
- [ ] URL backend notée (ex: `https://mathassistant-backend.onrender.com`)
- [ ] Endpoint `/health` accessible et retourne `{"status": "healthy"}`
- [ ] Endpoint `/` accessible et retourne les informations de l'API
- [ ] Logs Render vérifiés (pas d'erreurs critiques)

## Déploiement Frontend (Vercel)

### Configuration Vercel
- [ ] Compte Vercel créé
- [ ] Repository GitHub connecté à Vercel
- [ ] Projet créé et détecté comme Vite

### Variables d'environnement Vercel
- [ ] `VITE_API_BASE_URL` configuré avec l'URL du backend Render + `/api`
  - Exemple: `https://mathassistant-backend.onrender.com/api`

### Vérification Frontend
- [ ] Déploiement réussi sur Vercel
- [ ] URL frontend notée (ex: `https://mathassistant.vercel.app`)
- [ ] Application accessible dans le navigateur
- [ ] Pas d'erreurs dans la console du navigateur
- [ ] Pas d'erreurs CORS

## Post-déploiement

### Mise à jour CORS
- [ ] Retourner sur Render
- [ ] Mettre à jour `CORS_ORIGINS` avec l'URL Vercel :
  - URL de production (ex: `https://mathassistant.vercel.app`)
  - URLs de preview si nécessaire
  - Format: `https://app1.vercel.app,https://app2.vercel.app`
- [ ] Redéployer le backend sur Render

### Tests fonctionnels
- [ ] Upload d'image fonctionne
- [ ] Capture caméra fonctionne (si testé sur mobile)
- [ ] Extraction LaTeX fonctionne
- [ ] Résolution de problème fonctionne
- [ ] Affichage des résultats fonctionne
- [ ] Export PDF fonctionne
- [ ] Gestion d'erreurs fonctionne correctement

### Tests de performance
- [ ] Temps de réponse backend acceptable
- [ ] Temps de chargement frontend acceptable
- [ ] Pas d'erreurs dans les logs

### Sécurité
- [ ] Aucune clé API dans le code source
- [ ] Variables d'environnement correctement configurées
- [ ] CORS correctement configuré (pas de `*`)
- [ ] HTTPS activé (automatique sur Vercel et Render)

## CI/CD

### GitHub Actions
- [ ] Workflow CI exécuté avec succès
- [ ] Linting frontend réussi
- [ ] Linting backend réussi
- [ ] Build frontend réussi
- [ ] Build backend réussi

## Documentation

- [ ] `DEPLOYMENT.md` consulté
- [ ] `README.md` mis à jour avec les URLs de production
- [ ] Documentation à jour

## Support et monitoring

- [ ] Logs Render accessibles et surveillés
- [ ] Logs Vercel accessibles et surveillés
- [ ] Endpoints de santé vérifiés régulièrement

## Notes importantes

### Plan gratuit Render
- ⚠️ Le service peut s'endormir après 15 minutes d'inactivité
- ⚠️ Le premier démarrage peut prendre 30-60 secondes
- ⚠️ Considérez un plan payant pour la production

### Plan gratuit Vercel
- ⚠️ Limites sur la bande passante
- ⚠️ Limites sur les builds
- ⚠️ Consultez les limites sur vercel.com

## URLs de production

Après déploiement, notez vos URLs ici :

- **Frontend (Vercel)** : `https://________________.vercel.app`
- **Backend (Render)** : `https://________________.onrender.com`
- **API Health Check** : `https://________________.onrender.com/health`

## Problèmes rencontrés

Notez ici les problèmes rencontrés et leurs solutions :

1. 
2. 
3. 

---

**Date de déploiement** : _______________
**Déployé par** : _______________

