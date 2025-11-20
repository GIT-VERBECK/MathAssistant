# Conseils pour améliorer la reconnaissance d'écriture manuscrite

## 📝 Meilleures pratiques pour les images manuscrites

### 1. Qualité de l'image

**✅ À faire :**
- Prenez la photo avec une bonne luminosité (évitez les ombres)
- Assurez-vous que l'écriture est nette et contrastée
- Utilisez un fond blanc ou clair
- Évitez les reflets et les plis sur le papier

**❌ À éviter :**
- Images floues ou pixelisées
- Mauvais éclairage (trop sombre ou trop clair)
- Fond coloré ou avec motifs
- Écriture trop petite ou trop grande

### 2. Qualité de l'écriture

**✅ À faire :**
- Écrivez clairement et lisiblement
- Espacez bien les symboles
- Distinguez clairement les chiffres des lettres :
  - 0 (zéro) vs O (lettre)
  - 1 (un) vs l (L minuscule)
  - 2 vs Z
  - 5 vs S
- Écrivez les fractions sur plusieurs lignes si possible
- Utilisez des lignes claires pour les fractions (—)

**❌ À éviter :**
- Écriture trop serrée
- Symboles qui se chevauchent
- Chiffres et lettres ambigus
- Écriture trop rapide ou illisible

### 3. Symboles mathématiques

**Symboles bien reconnus :**
- Opérations de base : +, -, ×, ÷, =
- Puissances : petits chiffres en haut (x², x³)
- Indices : petits chiffres en bas (x₁, x₂)
- Fractions : utilisez une barre horizontale claire
- Racines : dessinez clairement le symbole √
- Intégrales : dessinez clairement ∫
- Sommes : dessinez clairement Σ
- Lettres grecques : dessinez-les clairement (α, β, γ, δ, θ, π)

**Symboles à dessiner avec soin :**
- Les fractions : utilisez une barre horizontale bien visible
- Les puissances : petits chiffres bien visibles
- Les indices : petits chiffres bien visibles
- Les racines : symbole √ bien formé
- Les intégrales : symbole ∫ bien formé

### 4. Format recommandé

**Pour de meilleurs résultats :**
- Écrivez une seule équation par image
- Centrez l'équation dans l'image
- Laissez de l'espace autour de l'équation
- Utilisez du papier quadrillé si possible (aide à l'alignement)

### 5. Exemples de bonnes pratiques

**✅ Bon exemple :**
```
    x² + 5x - 3 = 0
```
- Écriture claire
- Espacement correct
- Symboles bien formés

**✅ Bon exemple pour fractions :**
```
    x + 1
    ───── = 2
     3
```
- Fraction bien formatée
- Barre horizontale claire

**❌ Mauvais exemple :**
```
x2+5x-3=0
```
- Trop serré
- Pas d'espacement
- Difficile à lire

### 6. Si ça ne fonctionne pas

**Essayez :**
1. **Réécrivez plus clairement** - Parfois une réécriture plus soignée suffit
2. **Prenez une nouvelle photo** - Avec un meilleur éclairage
3. **Utilisez un scanner** - Si disponible, les scanners donnent de meilleurs résultats
4. **Écrivez plus grand** - Les symboles plus grands sont mieux reconnus
5. **Séparez les équations complexes** - Une équation par image

### 7. Alternatives

Si la reconnaissance manuscrite ne fonctionne pas bien :
- **Tapez directement le LaTeX** - Vous pouvez entrer le LaTeX manuellement dans l'interface
- **Utilisez un éditeur LaTeX** - Écrivez d'abord en LaTeX, puis prenez une capture d'écran
- **Utilisez une tablette graphique** - Pour une écriture plus nette

## 🔧 Améliorations techniques

Le système utilise maintenant :
- **GPT-4o avec haute résolution** (`detail: "high"`) pour mieux voir les détails
- **Prompt optimisé** pour le manuscrit avec instructions spécifiques
- **Température à 0** pour plus de précision et cohérence
- **Tokens augmentés** (1500) pour les équations complexes

Ces améliorations devraient considérablement améliorer la reconnaissance du manuscrit.

