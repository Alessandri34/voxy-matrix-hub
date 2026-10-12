# E1 — Module « Générateur de scripts » — spécification

> **Casquette : Directeur produit + ingénieur prompt.**
> **Date : 12 octobre 2026.** Prérequis : `E0` (architecture).
> ⚠️ **Règle D9 :** ce module existe d'abord en **v0 manuelle** (le formateur l'exécute avec le client). On ne code qu'après 10 exécutions réelles.

---

## 1. Ce que le module doit produire

**Entrée :** un dirigeant de TPE qui ne sait pas quoi filmer.
**Sortie :** **10 à 12 scripts vidéo** prêts à tourner, chacun avec son accroche, son déroulé seconde par seconde, ses plans à filmer, son appel à l'action, ses mentions légales — **et une garantie qu'il peut réellement les produire seul.**

### 🎯 Les 3 critères de réussite (non négociables)

| # | Critère | Test de recette |
|---|---|---|
| 1 | **Spécifique à SON entreprise** | Un concurrent du même secteur ne pourrait pas réutiliser le script tel quel |
| 2 | **Producible par LUI** | Il peut le tourner seul, avec son téléphone, en moins de 30 minutes |
| 3 | **Conforme** | Zéro formulation bannie, zéro promesse de résultat, mentions présentes |

> Le critère 2 est celui que tous les outils d'IA ratent. **Un script que le client ne peut pas produire vaut zéro.**

---

## 2. Le questionnaire d'entrée (objectif : < 6 minutes)

> Principe : **on demande le strict minimum et on enrichit automatiquement le reste.** Chaque question en trop fait perdre des utilisateurs.

### Étape 1 — Identification (15 secondes)

| # | Question | Traitement |
|---|---|---|
| 1 | **Nom de votre entreprise ou SIREN** | → API Recherche d'entreprises (gratuite) → SIREN, raison sociale, code NAF, adresse, géolocalisation |
| 2 | **Votre site web ou votre page Instagram/Facebook** (optionnel) | → lecture de page → offres, ton, positionnement, preuves existantes |

*Enrichissement automatique en arrière-plan : NAF + effectif (Sirene/INSEE), concurrents locaux, publicités actives du secteur.*

### Étape 2 — Le métier (3 minutes, 6 questions)

| # | Question | Pourquoi |
|---|---|---|
| 3 | **Qu'est-ce que vous vendez, en une phrase, comme vous le diriez à un client ?** | Capte ses mots à lui, pas le jargon du NAF |
| 4 | **Votre client type, c'est qui ? Décrivez le dernier.** | Persona ancré dans le réel, pas théorique |
| 5 | **Qu'est-ce qui déclenche l'achat ? À quel moment il vous appelle ?** | → le **signal**, base des angles |
| 6 | **Quelle est la question qu'on vous pose tout le temps ?** | → mine d'or d'angles éditoriaux |
| 7 | **Qu'est-ce qui vous distingue vraiment du concurrent d'à côté ?** | Différenciation |
| 8 | **Quelle objection revient le plus souvent avant d'acheter ?** | → angles « objection levée » |

### Étape 3 — Les moyens réels (1 minute, 3 questions) — ⭐ **l'étape qui change tout**

| # | Question | Impact direct |
|---|---|---|
| 9 | **Combien de temps par semaine, réellement ?** (< 30 min / 30-60 min / 1-2 h / plus) | Détermine le **nombre** de scripts générés |
| 10 | **Vous êtes à l'aise face caméra ?** (oui / moyen / pas du tout) | « pas du tout » → **zéro script facecam**, que de la voix off + plans de son activité |
| 11 | **Vous pouvez filmer quoi ?** (mon local / mes produits / mes chantiers / mes clients / juste moi) | Contraint les plans proposés aux **plans réellement tournables** |

> 💡 **Ces 3 questions sont la différence entre un générateur de texte et un outil utile.** Elles garantissent le critère de réussite n°2.

### Étape 4 — Contraintes réglementaires (automatique)
Déduit du code NAF : secteur réglementé (santé, droit, assurance, immobilier, alimentaire…) → injection des contraintes de communication propres au secteur.

---

## 3. Enrichissement automatique — sources & verdicts juridiques

| Source | Usage | Coût | Verdict |
|---|---|---|---|
| **API Recherche d'entreprises** (DINUM) | Nom → SIREN, NAF, adresse | **0 €** | ✅ Open data, sans clé |
| **API Sirene / INSEE** | NAF, tranche d'effectif, établissements | **0 €** | ✅ Source autoritative |
| **Pappers** (optionnel) | Dirigeants, bilans | ~20 €/mois | ✅ API B2B payante |
| **Lecture du site client** | Offres, ton, preuves | ~0 € | ✅ **Sous mandat écrit au contrat** |
| **Meta Ad Library** (`pays=FR`, `type=ALL`) | Publicités actives des concurrents | **0 €** | ⚠️ **Zone grise** — voir ci-dessous |
| **Google Ads Transparency** (jeu BigQuery public) | Publicités Google des concurrents | **≈ 0 €** | ✅ **La source la plus propre juridiquement** |
| ❌ TikTok Research / Commercial Content Library | — | — | ❌ **Utilisateurs commerciaux explicitement inéligibles** |
| ❌ Foreplay / AdSpy / Minea / BigSpy | — | — | ❌ **Interdit en backend** (ToS). ✅ Autorisé comme **outil de recherche interne** pour notre équipe |

### ⚠️ Règles de prudence sur l'analyse concurrentielle
1. 🔴 **Premier chantier de développement : un appel de test réel** à l'API Meta Ad Library avec `ad_reached_countries=['FR']&ad_type=ALL`. Les sources divergent sur ce qui est réellement renvoyé en UE (le DSA impose un registre de **toutes** les publicités). **Toute l'architecture du module en dépend — 10 minutes de test avant d'écrire une ligne.**
2. ❌ **Ne jamais réhéberger les créas vidéo des concurrents** (droit d'auteur). On lie vers l'aperçu officiel, on **stocke uniquement l'analyse dérivée** (angles, hooks, structures).
3. ❌ **Ne jamais promettre l'exhaustivité** : aucune source n'est complète. À dire dans l'interface.
4. ⚠️ `ad_snapshot_url` est un **lien d'aperçu, pas un fichier média** — l'analyse porte sur le texte et les métadonnées, pas sur la vidéo.
5. 💡 **Le signal le plus utile est gratuit : la durée de diffusion.** Une publicité diffusée depuis 4 mois fonctionne. C'est un meilleur indicateur de performance que n'importe quelle métrique déclarée.

---

## 4. 🧠 Le moteur de raisonnement — 3 passes

> Architecture à 3 passes, inspirée de ce qu'on a validé pour nos propres scripts.
> **Optimisation clé : les 3 passes partagent le même préfixe de contexte (~15 000 tokens) → mise en cache du prompt = −65 % sur l'entrée.** C'est le plus gros levier de coût du produit.

```
   FICHE ENTREPRISE + MARCHÉ
            ↓
┌───────────────────────────────┐
│ PASSE 1 — ANALYSE             │  modèle économique, UE
│ signal · personas · 10 angles │  température basse
│ niveau de conscience          │  sortie structurée (JSON)
└───────────────┬───────────────┘
                ↓   🚦 point de validation client
┌───────────────────────────────┐
│ PASSE 2 — RÉDACTION           │  meilleur modèle français
│ 10-12 scripts complets        │  température haute
│ hook × angle × persona        │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ PASSE 3 — CONTRÔLE 🛡️          │  modèle économique
│ conformité · producibilité    │  température ~0
│ note de conversion /100       │  déterministe
└───────────────┬───────────────┘
                ↓
      SCRIPTS LIVRÉS + NOTES
```

### Passe 1 — ANALYSE
**Produit :** le signal, 3 personas, le niveau de conscience de chacun, et **10 angles** (5 « persona » / 5 « douleur ») — la méthode validée au chantier A.

**Entrées :** fiche entreprise enrichie + angles extraits des publicités concurrentes actives + réponses au questionnaire.

> 🚦 **Point de validation client (obligatoire).** On montre les personas et les 10 angles **avant** d'écrire. Deux raisons : la qualité (le client corrige ce qui est faux) et l'**adhésion** (il a participé, il produira les scripts). *C'est aussi une phase réflexive AFEST valorisable comme preuve pédagogique.*

### Passe 2 — RÉDACTION
Pour chaque script : **1 format × 1 angle × 1 persona** (règle du chantier A).

**Bibliothèques mobilisées :**
- **50 accroches** classées par famille (visuelles 1-16 · sonores 17-22 · copywriting 23-40 · preuve/format 41-50)
- **Niveaux de conscience (Schwartz)** → nos cibles sont *conscientes du problème*, pas du produit → **structure Problème → Agitation → Solution imposée, pitch direct interdit**
- **Étapes de maturité** : découverte / considération / décision
- **Contraintes de producibilité** (questions 9-11) → ne propose que des plans tournables

### Passe 3 — CONTRÔLE 🛡️ *(la passe qui transforme une contrainte légale en fonction produit)*

| Contrôle | Règle | Action si échec |
|---|---|---|
| **Formulations bannies** | `gratuit` · `100 % financé` · `sans reste à charge` · `offert` · `garanti` · `résultat garanti` | 🔴 Blocage + réécriture automatique |
| **Allégation de résultat** | Aucun chiffre de CA, de clients ou de gains promis | 🔴 Blocage |
| **Vocabulaire « emploi »** *(si usage publicitaire)* | `reconversion` · `employabilité` · `diplôme` · `carrière` | 🟠 Alerte (risque de catégorie spéciale Meta) |
| **Secteur réglementé** | Contraintes propres (assurance, santé, droit, alimentaire) | 🟠 Alerte + reformulation |
| **Mentions obligatoires** | « Publicité » si contenu sponsorisé | 🟠 Ajout automatique |
| **Producibilité** | Chaque plan est-il tournable avec les moyens déclarés ? | 🔴 Remplacement du plan |
| **Unicité** | 1 script = 1 angle = 1 persona | 🟠 Signalement |
| **Note de conversion** | /100 sur 6 critères (ci-dessous) | 🟠 Réécriture si < 60 |

**Grille de notation de conversion (/100) :**
| Critère | Points | Question |
|---|---|---|
| Force de l'accroche | 25 | Les 3 premières secondes arrêtent-elles le défilement ? |
| Concordance avec le niveau de conscience | 20 | L'angle parle-t-il au client là où il en est ? |
| Spécificité | 20 | Un concurrent pourrait-il réutiliser ce script tel quel ? Si oui → 0 |
| Clarté de l'appel à l'action | 15 | Une seule action, explicite |
| Producibilité | 10 | Tournable seul en < 30 min |
| Conformité | 10 | Zéro signalement |

> 💡 **La passe 3 est aussi un argument commercial :** *« notre outil refuse d'écrire ce qui vous mettrait en infraction »*. Aucun outil généraliste ne le fait.

---

## 5. Format de sortie d'un script

```markdown
## Script 04 — « Vous payez 30 % à une plateforme pour vos propres clients »

🎯 Persona : Sophie · restauratrice · Montpellier
📊 Niveau de conscience : conscient du problème
🏷️ Angle : dépendance aux plateformes
🎬 Format : voix off + plans du restaurant (pas de facecam) ⟵ adapté à « pas à l'aise caméra »
⏱️ Durée cible : 28 s · Tournage estimé : 20 min
⭐ Note de conversion : 84/100

### Accroche (0-3 s) — n° 35 « statistique choc »
> 🎙️ « Trente pour cent. C'est ce que la plateforme prend sur chaque commande. »
> 📺 Texte à l'écran : « 30 % — sur CHAQUE commande »
> 🎥 Plan : gros plan sur un ticket de commande, puis sur la note de commission

### Développement (3-18 s)
> 🎙️ « Ce client, il habite à 400 mètres. Il serait venu directement s'il vous connaissait. »
> 🎥 Plan : vue de la rue depuis la devanture, puis la salle

### Bascule (18-25 s)
> 🎙️ « Les restaurants qu'on voit passer sur les réseaux, ce ne sont pas les meilleurs.
>      Ce sont ceux qu'on reconnaît. »
> 🎥 Plan : service en cuisine, un plat dressé

### Appel à l'action (25-28 s)
> 🎙️ « Montrez ce que vous faites. Ça commence par une vidéo. »
> 📺 Texte : nom + ville du restaurant

### ✅ Contrôles
- Conformité : OK — aucune formulation bannie, aucune promesse chiffrée
- Producibilité : OK — 4 plans, téléphone seul, pas de figurant
- Mentions : aucune requise (contenu organique non sponsorisé)
```

---

## 6. 🏆 La boucle de mesure — ce qui fait la différence

> Rappel `E0` §8 : **c'est ce qui transforme un générateur copiable en actif qui se renforce.**

Après chaque script généré, le produit demande (en 2 clics, au rituel hebdomadaire suivant) :

| Question | Réponse | Usage |
|---|---|---|
| Tu l'as tourné ? | oui / non / pas encore | Si « non » → **pourquoi ?** → améliore la producibilité |
| Tu l'as publié ? | oui / non | Mesure l'activation réelle |
| Ça a donné quoi ? | vues (tranche) · messages reçus · demandes | **Étiquette de performance** |

**Ce qu'on en tire :**
1. **Pour le client** : « tes accroches de type "question directe" marchent 2× mieux que les autres — on en fait plus. »
2. **Pour nous** : un corpus français étiqueté par la performance → les angles qui marchent **par secteur, par ville, par persona**.
3. **Pour la formation** : preuve d'apprentissage réel (trace horodatée) → `E0` §2.

> ⚠️ **Piège à éviter :** ne pas demander trop de données. **3 questions, 2 clics, au moment du rituel hebdomadaire.** Un formulaire de mesure long n'est jamais rempli.

---

## 7. Squelette de prompt (passe 2 — rédaction)

> Structure conforme aux bonnes pratiques 2026 : rôle court, **données longues en haut**, le *pourquoi* de chaque consigne, balises descriptives, critères de succès explicites.
> ⚠️ Le **préremplissage de réponse n'est plus supporté** — on obtient le format par consigne explicite et sortie structurée.

```xml
<role>
Tu écris des scripts vidéo courts pour des dirigeants de TPE françaises.
</role>

<entreprise>
  <identite>{raison_sociale} · {naf} · {effectif} · {ville}</entreprise>
  <offre_mots_du_client>{réponse Q3}</offre_mots_du_client>
  <client_type>{réponse Q4}</client_type>
  <declencheur_achat>{réponse Q5}</declencheur_achat>
  <question_recurrente>{réponse Q6}</question_recurrente>
  <differenciation>{réponse Q7}</differenciation>
  <objection_principale>{réponse Q8}</objection_principale>
</entreprise>

<moyens_reels>
  <temps_hebdo>{Q9}</temps_hebdo>
  <aisance_camera>{Q10}</aisance_camera>
  <plans_possibles>{Q11}</plans_possibles>
</moyens_reels>

<marche_local>
  <concurrents_visibles>{3 concurrents + leurs angles publicitaires actifs}</concurrents_visibles>
  <angles_satures>{angles déjà très utilisés — à éviter}</angles_satures>
</marche_local>

<analyse_validee>
  <!-- sortie de la passe 1, corrigée par le client -->
  <signal>{signal}</signal>
  <personas>{3 personas + niveau de conscience}</personas>
  <angles>{10 angles validés}</angles>
</analyse_validee>

<bibliotheque_accroches>{50 accroches classées par famille}</bibliotheque_accroches>

<task>
Écris {N} scripts vidéo. Un script = 1 format × 1 angle × 1 persona.
Pourquoi cette règle : un script qui mélange deux angles ne convertit sur aucun des deux.
</task>

<success_criteria>
- Un concurrent du même secteur ne pourrait PAS réutiliser le script tel quel.
- Chaque plan est tournable avec les moyens déclarés dans <moyens_reels>.
- L'accroche tient en 3 secondes et utilise une accroche de la bibliothèque.
- La structure suit Problème → Agitation → Solution
  (pourquoi : la cible est consciente du problème, pas du produit — un pitch direct
   serait rejeté).
- Les mots employés sont ceux du client (voir offre_mots_du_client), pas du jargon.
</success_criteria>

<constraints>
INTERDIT : gratuit · 100 % financé · sans reste à charge · offert · garanti ·
tout chiffre de chiffre d'affaires, de clients ou de gains promis.
{contraintes_sectorielles}
</constraints>

<out_of_scope>
Pas de script nécessitant du matériel non déclaré, un figurant, ou un montage
dépassant les capacités d'une application mobile gratuite.
</out_of_scope>

<output_format>
Pour chaque script : titre · persona · niveau de conscience · angle · format ·
durée · accroche (voix off + texte écran + plan) · développement · bascule ·
appel à l'action · mentions.
</output_format>

<reliability>
Si une information manque, écris [À PRÉCISER] — n'invente aucun chiffre,
aucun témoignage, aucun résultat client.
</reliability>
```

---

## 8. Plan de construction

| Étape | Contenu | Quand |
|---|---|---|
| **0** | 🔴 **Test de l'API Meta Ad Library sur `FR` + `ALL`** — tranche l'architecture | Avant tout |
| **1** | **v0 manuelle** : le formateur exécute les 3 passes avec le client en session. 10 exécutions minimum. | M0-M3 |
| **2** | Chaîne d'enrichissement : Recherche d'entreprises → Sirene → lecture du site | M3 |
| **3** | Passes 1-2-3 outillées + mise en cache du préfixe | M4 |
| **4** | Interface questionnaire + validation client des angles | M4-M5 |
| **5** | **Boucle de mesure** (§6) — *à ne surtout pas repousser : c'est le moat* | M5 |
| **6** | Analyse concurrentielle automatisée (Meta + BigQuery Google) | M6 |

---

## 9. Points de vigilance

1. 🔴 **Ne pas repousser la boucle de mesure.** Sans elle, le module est un wrapper copiable en un week-end.
2. 🔴 **Le point de validation client après la passe 1 est obligatoire.** Sans lui : scripts génériques, zéro adhésion, zéro production.
3. 🟠 **Le questionnaire doit rester sous 6 minutes.** Chaque question supplémentaire coûte des utilisateurs.
4. 🟠 **Tester sur 20 briefs réels** avant de choisir le modèle — aucun classement public ne mesure la rédaction créative en français.
5. 🟠 **Secteurs réglementés** : prévoir une liste d'exclusion. Santé et droit → ne pas servir en v1.

---

> **Suite :** `E2_Module_Generateur_Prompts.md`
