# VOXY Formation — film motion design (52 s)

Vidéo de présentation de l'offre VOXY (16:9, 1920×1080, 60 i/s, son stéréo).

- **Livrable :** `out/voxy-motion-design.mp4`
- Bande-son seule : `out/voxy-soundtrack.m4a` · Vignette : `out/voxy-poster.jpg`

## Déroulé

| Temps | Scène | Message |
|---|---|---|
| 0–4 s | Accroche | « Chaque année, vous cotisez pour la formation. Non utilisé, ce budget est perdu. » |
| 4–8 s | Problème | Une agence vous facture : trésorerie, abonnement, actifs qui restent à l'agence |
| 8–12 s | Révélation | VOXY Formation — « Nous construisons votre infrastructure digitale. Pendant que nous vous formons à la piloter. » |
| 12–16 s | Offre | 5 000 € → 0 € de reste à charge, pris en charge par l'OPCO |
| 16–22 s | Programme 01 | E-Com Commando |
| 22–28 s | Programme 02 | Outbound Hybride |
| 28–34 s | Programme 03 | Drive-to-Store |
| 34–40 s | Processus | De l'audit à l'autonomie, en 4 étapes |
| 40–44 s | Preuves | 0 € · 100 % propriétaire · 10 min |
| 44–52 s | Appel à l'action | « Vérifiez votre éligibilité » — audit de financement gratuit |

Tous les textes et chiffres viennent des pages du hub (`CATALOGUE_PORTAL`, pages de vente des trois offres).

## Modifier la vidéo

Le film est une page web animée, rendue image par image puis encodée :

- `src/index.html` — textes et structure des scènes
- `src/style.css` — charte (couleurs, typographies Outfit / Cormorant)
- `src/main.js` — timeline des animations (GSAP)
- `audio.py` — musique et bruitages, synthétisés et calés sur la timeline
- `render.cjs` — capture des images avec Chromium (Playwright)

Reconstruire : `./build.sh` (nécessite node + playwright, ffmpeg, python3 avec numpy et scipy).
Aperçu rapide : ouvrir `src/index.html` dans un navigateur puis cliquer sur « Lecture avec le son ».
