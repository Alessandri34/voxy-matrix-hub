# VOXY MATRIX — Vidéo motion design (60 s, 16:9, 1080p60)

**Fichier final :** `VOXY_MATRIX_Motion_16x9.mp4`

Vidéo de présentation style "keynote SaaS" : typographie cinétique, inserts UI animés en guise de b-rolls, sound design synthétisé et calé à l'image près. Elle suit une structure de conversion : accroche → douleur → solution → preuve → rareté → appel à l'action.

## Storyboard

| Temps | Scène | Message | Insert / b-roll | Son |
|---|---|---|---|---|
| 0–4 s | Accroche (fond noir) | « Chaque année, votre budget formation s'évapore. » | Jauge « Droits formation » qui se vide → pastille *Expiré* | tic-tac d'horloge, drone, thud d'erreur |
| 4–8 s | Douleur | « On vous a vendu… » site vitrine 5 000 €, formation 40 h, agence 12 mois | 3 cartes barrées en rouge | pops, glitchs de rature |
| 8–12 s | Bascule | « Et si votre formation construisait votre machine à clients ? » | Zoom/flou vers la caméra | riser + silence avant l'impact |
| 12–16 s | Révélation de la marque | VOXY MATRIX · Centre d'Implémentation Qualiopi | Logo matrice 3×3 en ressort, reflet lumineux, badges | gros impact, shimmer |
| 16–20 s | Promesse | « Zéro théorie. Que de l'exécution. » + 100 % finançable* | Anneau de progression animé | ticks de compteur, cloche |
| 20–26 s | Système 01 — E-Com Commando | Boutique qui vend jour et nuit | Navigateur : 50 fiches produits générées par IA, notifications de commande | pops de génération, dings de notification |
| 26–32 s | Système 02 — Outbound Autonome | Votre agenda se remplit, sans vous | Agenda qui se remplit (12 RDV) + carte « Agent vocal IA » avec forme d'onde | pops de RDV, voix téléphonique synthétique, chime de succès |
| 32–38 s | Système 03 — Drive-to-Store | Dominez Google Maps dans votre ville | Carte, saisie de la recherche, chute du pin, passage de #4 à #1, 12 → 148 avis | frappe clavier, chute du pin, swoosh de reclassement |
| 38–44 s | Preuve (fond noir) | +300 % de demandes de devis en 2 mois (BTP, 34) | Courbe animée, cartes 2 h/semaine et 100 % FAFCEA | ticks montants, impact |
| 44–48 s | Méthode | 3 étapes. Zéro paperasse. | Frise : Audit → Financement → Implémentation | notes ascendantes |
| 48–52 s | Rareté (fond noir) | 5 entreprises par mois. Sélection sur dossier. | 5 cases qui s'allument, zoom avant | breakdown, riser |
| 52–60 s | Appel à l'action + carton final | « Vérifiez votre éligibilité. » | Bouton cliqué par un curseur → « Demande envoyée », puis logo | impact, clic, chime, accord final |

Musique : 120 BPM (1 mesure = 2 s, chaque changement de scène tombe sur une mesure). Intro en La mineur, puis progression I–V–vi–IV en Do majeur, avec sidechain, delay et réverbération. Mixée à −14 LUFS (norme YouTube, LinkedIn et Meta).

## Personnaliser

Tout le contenu (textes, chiffres, couleurs) est dans `composition.html`. Pour visualiser une image précise, ouvrez `composition.html?t=23.5` dans un navigateur.

```bash
bash tools/build.sh                  # rendu complet : images, son et MP4
node tools/preview.js <dossier> 12 24.5 40   # captures d'écran à des instants précis
```

## À vérifier avant diffusion
- Les chiffres (+300 %, 2 h/semaine, 100 % FAFCEA, 5 places par mois, première vente sous 14 jours) proviennent de votre landing page FAFCEA et de votre catalogue d'offres. Vérifiez que vous pouvez les justifier. Des mentions « selon éligibilité » et « les résultats varient » sont déjà affichées à l'écran.
- Les interfaces (boutique, agenda, carte) sont des illustrations : les noms et les montants sont fictifs.
- Il n'y a pas de voix off. Le texte à l'écran porte le message, ce qui fonctionne sans le son, comme c'est le cas sur la plupart des réseaux sociaux.
