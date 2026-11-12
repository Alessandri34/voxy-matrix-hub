# VOXY MATRIX — Vidéo motion design (60 s, 16:9, 1080p60)

**Fichiers finaux :**
- `VOXY_MATRIX_Motion_16x9_VO.mp4` : version avec voix off (Fish Speech)
- `VOXY_MATRIX_Motion_16x9.mp4` : version musique et sound design seuls
- `VOXY_MATRIX_sous-titres.srt` : sous-titres de la voix off, à importer sur LinkedIn, Meta ou YouTube

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
- **Licence de la voix** : les poids de Fish Speech 1.5 sont publiés sous licence **CC BY-NC-SA 4.0, qui interdit l'usage commercial**. Une publicité pour votre offre est un usage commercial. Avant toute diffusion, obtenez une licence commerciale auprès de Fish Audio (ou passez par leur offre payante, dont vous vérifierez les conditions), ou remplacez la voix par un enregistrement humain. Le mixeur accepte n'importe quel fichier audio, voir plus bas.

## Voix off

Le script et ses timecodes sont dans `voix_off/cues.json`, qui sert de source unique pour les sous-titres, la génération et le mixage. Pour chaque réplique, le fichier donne aussi une note de jeu (intention, mots à appuyer).

### Générer la voix avec Fish Speech 1.5 (open source, en local, sur CPU)
```bash
git clone --branch v1.5.1 https://github.com/fishaudio/fish-speech.git
# environnement Python 3.11 : torch 2.4.1 (CPU), transformers 4.46.3, faster-whisper, puis `pip install -e fish-speech`
huggingface-cli download fishaudio/fish-speech-1.5 --local-dir ckpt/fish-speech-1.5
python voix_off/fish/generate_vo.py --fish-src fish-speech --ckpt ckpt/fish-speech-1.5 \
  --ref-codes voix_off/fish/voix_reference.npy \
  --ref-text "Bonjour. Aujourd'hui, je vais vous présenter une façon simple et concrète de développer votre entreprise, sans perdre de temps." \
  --takes 3                     # --only 04,09 pour ne refaire que certaines répliques
python3 tools/mix_voiceover.py  # → VOXY_MATRIX_Motion_16x9_VO.mp4
```
- **Même voix partout** : chaque réplique est générée en clonant une voix de référence (`voix_reference.npy`), retenue après un casting de 11 voix. Deux alternatives sont fournies : `voix_alt_claire.npy` (masculine, plus claire) et `voix_alt_feminine.npy`. On peut les écouter dans `voix_off/fish/casting_3_voix.mp3`, dans l'ordre : référence, claire, féminine.
- **Contrôle qualité automatique** : chaque prise est transcrite par Whisper et comparée au texte (taux d'erreur), et sa durée est comparée à son créneau. On garde la prise la mieux articulée qui tient dans le temps, avec une hauteur de voix homogène.
- **Votre propre voix** : enregistrez 10 à 20 s de vous en train de lire un texte, encodez-les en `.npy` avec `python -m fish_speech.models.vqgan.inference -i ma_voix.wav`, puis passez-les en `--ref-codes` avec leur transcription en `--ref-text`.

### Ou utiliser une voix humaine enregistrée
Déposez une prise par réplique dans `voix_off/prises/01.wav` à `13.wav` (mp3, m4a ou wav), puis lancez `python3 tools/mix_voiceover.py`.

### Ce que fait le mixeur
- Il coupe les silences et cale chaque réplique sur son timecode. Si une prise déborde, il l'accélère légèrement sans changer la hauteur (6 % au plus, 13 % s'il faut libérer la place pour la réplique suivante).
- Il applique une chaîne de traitement studio : passe-haut, EQ (moins de bas-médium, plus de présence et d'air), de-esser, compression, limiteur.
- Il baisse la musique d'environ 8 dB sous la voix (ducking) et creuse la bande 1,5–4,5 kHz de la musique pour dégager la voix. Les effets baissent d'environ 3 dB.
- Le master final sort à −14 LUFS avec une crête vraie à −1 dBTP.
