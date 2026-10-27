# Analyse — Améliorer la transformation des campagnes Meta Ads

> Diagnostic basé sur tes offres (dépôt voxy-matrix-hub) et sur des sources publiques. Classé par impact attendu. Les objectifs chiffrés sont des **repères de départ à mesurer**, pas des promesses.

## Diagnostic en une phrase
Tes offres sont bien construites sur le papier (empilement de valeur, financement, garanties), mais **la preuve manque** (études de cas = textes à trous) et **Meta optimise aujourd'hui sur le volume de leads, pas sur les leads qui achètent**. Ce sont les deux leviers prioritaires.

---

## Les 10 actions, par ordre d'impact

### 1. Apprendre à Meta qui achète vraiment (API Conversions pour CRM) — impact très fort
- Passer les campagnes sur l'objectif **Leads → optimisation « Leads de conversion »**.
- Renvoyer à Meta, pour chaque lead, les étapes atteintes : `lead_qualifie` → `rdv_reserve` → `rdv_honore` → `client`.
- Résultat publié : **−21 % de coût par lead qualifié** (test A/B sur 1 031 annonceurs) ([Make](https://www.make.com/en/blog/meta-make-conversions-api-for-crm)). Une source indique que l'API Conversions est requise pour cet objectif sur les nouvelles campagnes depuis avril 2026 *(à vérifier dans l'aide Meta)*.
- **Faisable dans le service déjà construit** : chaque changement de statut du lead envoie un événement à Meta. C'est l'étape 6 du playbook.

### 2. Produire 3 preuves réelles — impact très fort
- La « probabilité perçue » est le multiplicateur de la Value Equation. Aujourd'hui : « [Nom du client] », « 1 500 € sauvés » non sourcés.
- 1 étude de cas par offre : avant/après chiffré, vidéo de 45–90 s du client, capture du résultat (CA Shopify, RDV dans l'agenda, avis Google).
- Utilisation : créa publicitaire, message J+1, page de confirmation de RDV, closing.
- Si tu n'as pas encore de clients sur une offre : faire 2–3 accompagnements à prix réduit **contre** une étude de cas filmée.

### 3. Formulaire « Intention plus forte » + 3 questions de qualification — impact fort
- Type de formulaire : **Intention plus forte** (écran de vérification avant envoi). Moins de volume, de meilleurs leads ([Jon Loomer](https://www.jonloomer.com/instant-forms/)).
- Questions : activité (routage de l'offre), statut (OPCO / FAFCEA / autre), délai de démarrage. Voir section 2 du playbook.
- Ajouter la **case de consentement** WhatsApp/SMS/téléphone (obligation CNIL + nouvelle loi sur le démarchage).
- Écran de fin : bouton « Réserver mon audit maintenant » vers l'agenda. Les leads chauds réservent sans attendre.

### 4. Vitesse de contact — impact fort (déjà construit)
- WhatsApp automatique en quelques secondes + appel humain < 5 min en horaires ouvrés (étude MIT : ×21 de qualification vs 30 min).
- KPI à suivre : **délai médian jusqu'au 1er contact humain**. Objectif : < 5 min de 10 h à 19 h.

### 5. Une campagne par offre et par persona — impact fort
Mélanger restaurateurs, e-commerçants et dirigeants B2B dans une même campagne brouille l'apprentissage de Meta.

| Campagne | Accroche (douleur réelle tirée de tes docs) | Lead magnet |
|---|---|---|
| E-Com Commando | « Votre site a du trafic mais ne vend pas ? Calculez le CA que vous perdez chaque mois. » | Calculateur de CA latent |
| Outbound Hybride | « 4 000 €/mois pour un SDR qui part au bout de 8 mois. Il existe une autre option. » | Audit coût par RDV |
| Drive-to-Store | « 30 % de commission UberEats sur chaque commande. Et si vos clients venaient directement ? » | Audit Google Business gratuit |
| FAFCEA Occitanie | « Artisan en Occitanie ? Votre formation digitale peut être prise en charge par le FAFCEA. » | Vérification d'éligibilité |

3 à 5 créas par campagne : 1 vidéo face caméra (toi), 1 témoignage client, 1 démonstration (OpusClip en direct, calculateur), 1 visuel chiffré.

### 6. Tester les publicités « Cliquer vers WhatsApp » — impact moyen à fort
- En complément du formulaire, une campagne dont le bouton ouvre directement une conversation WhatsApp. La conversation démarre chez le lead : fenêtre de 24 h ouverte, messages libres gratuits, pas de modèle à faire valider.
- Études de cas éducation publiées par WhatsApp : leads ×2 plus convertis (Universidad UK) ; 85 % des leads qualifiés convertis (FliQi). Chiffres auto-déclarés ([source](https://business.whatsapp.com/resources/success-stories/universidad-uk)).
- Test A/B à budget égal sur 2 semaines : formulaire vs WhatsApp, comparé sur le **coût par RDV honoré**.

### 7. Reciblage des « presque leads » et des leads froids — impact moyen
- Audience personnalisée « Formulaire instantané → **ouvert mais non envoyé** » : pub témoignage + « il ne vous reste qu'une étape ».
- Audience « leads envoyés depuis 7–60 jours sans RDV » (liste issue du service) : pub étude de cas + audit.
- **Exclure les clients** de toutes les campagnes d'acquisition.

### 8. Message financement : cadré et légal — impact moyen
- La publicité peut parler de prise en charge OPCO/FAFCEA ; **jamais de CPF** dans la prospection (loi 2022-1587).
- Ton document `Challenge/` le souligne : le reste à charge à 0 € via l'OPCO se resserre. Il faut des créas qui vendent le **ROI sur fonds propres** (« 3 500 € investis, 12 000 € récupérés en 60 jours » — **avec une vraie preuve**), pour ne pas dépendre du financement.

### 9. Un tableau de bord « du clic au chiffre d'affaires » — impact moyen (indispensable pour piloter)

| Étape | KPI | Repère de départ à mesurer |
|---|---|---|
| Pub → lead | Coût par lead | ~19 € de médiane en éducation en France ([SuperAds](https://www.superads.ai/facebook-ads-costs/cost-per-lead/education/france)), très variable |
| Lead → qualifié | % qualifiés | à mesurer la 1re quinzaine |
| Qualifié → RDV réservé | Taux de réservation | à mesurer |
| RDV → honoré | Taux de présence | 40–60 % sur des RDV issus de pub, 70 % et plus avec une bonne séquence *(éditeurs, non vérifié)* |
| Honoré → client | Taux de closing | à mesurer |
| **Global** | **Coût d'acquisition client vs panier** (3 500 € / 8 500 € / 11 000 €) | La seule métrique qui décide d'augmenter le budget |

Le service enregistre déjà chaque lead : je peux y brancher ce tableau de bord.

### 10. Rythme d'optimisation — impact cumulatif
- 1 changement par semaine : une créa, une question, un message de séquence.
- Couper une créa dont le coût par RDV honoré dépasse 2× la moyenne après une dépense de 2× le panier visé par RDV.
- Principe « 100 golden BBs » : beaucoup de gains de 1 à 3 % plutôt qu'une refonte.

---

## Plan sur 30 jours
| Semaine | Actions |
|---|---|
| S1 | Formulaire « Intention plus forte » + questions + consentement · déploiement de l'automatisation WhatsApp/SMS · agenda d'audit |
| S2 | 1 campagne par offre (3–5 créas chacune) · soumission des modèles WhatsApp · tournage de la 1re étude de cas |
| S3 | API Conversions CRM (événements de statut) · séquence 14 jours + séquence RDV · test « Cliquer vers WhatsApp » |
| S4 | Tableau de bord · 1re revue : couper les créas perdantes, garder le canal gagnant · 2e étude de cas |
