# Données brutes de la veille publicitaire

Relevé du **20/10/2026**, bibliothèque publicitaire Meta, France, annonces
actives. Analyse dans `../A3_Veille_Publicitaire.md`.

| Fichier | Contenu |
|---|---|
| `corpus.json` | Les 28 annonces : identifiant, date, texte, marqueurs |
| `extract.mjs` | Le navigateur qui passe le défi anti-robot de Meta |
| `parse.py` | L'extraction du texte depuis le HTML rendu |

## Pour refaire le relevé

```bash
node extract.mjs     # sauvegarde rendu-*.html (passe le défi)
python3 parse.py     # produit corpus.json
```

⚠️ **Meta bloque les passages rapprochés.** Le second appel de la session du
20/10 a été refusé. Espacer les relevés, et conserver les `rendu-*.html` :
ils contiennent tout, le `parse.py` peut être rejoué dessus sans rappeler Meta.

⚠️ **Les données périment vite** : Youdji a renouvelé 15 annonces sur 17 en
trois jours. Un relevé a une valeur d'instantané, pas de référence.
