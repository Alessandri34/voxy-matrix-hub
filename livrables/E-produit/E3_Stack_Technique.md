# E3 — Stack technique, coûts & conformité

> **Casquette : Directeur technique.** Document de décision chiffré.
> **Date : 12 octobre 2026.** Prérequis : `E0` (architecture), `E1`, `E2`.
> ⚠️ **Réserve de méthode :** les prix des fournisseurs tiers sont **[À vérifier]** sur pages officielles avant engagement (l'environnement de recherche ne pouvait pas les atteindre). **La conclusion principale résiste à une erreur de ±50 % sur ces prix** — la démonstration est au §2.

---

## 1. 🔴 La décision la plus importante : jamais de GPU

> Tu envisageais d'héberger un modèle open source sur un VPS. **Les chiffres disent non — et pas de peu.**

### Hypothèse de consommation (notre pipeline à 3 passes, `E1` §4)

| Paramètre | Valeur |
|---|---|
| Contexte d'entrée par génération | ~15 000 tokens |
| Sortie par passe | ~8 000 tokens |
| Nombre de passes | 3 |
| **Total par génération** | **~45 000 tokens en entrée · ~24 000 en sortie** |

### Le seuil de bascule

| Comparaison | Seuil de rentabilité du GPU | Équivalent en clients |
|---|---|---|
| vs API européenne économique | **~15 300 générations/mois** | **~760 clients** |
| vs API premium avec mise en cache | **~5 700 générations/mois** | **~290 clients** |

### Notre volume réel

| Scénario | Clients | Générations/mois | Coût API | Coût GPU équivalent |
|---|---|---|---|---|
| Lancement | 20 | 400 | **~20-50 €** | 1 373 € |
| Croissance | 50 | 1 000 | **~90-240 €** | 1 373 € |
| **Plafond visé** | **100** | **2 000** | **~180-480 €** | **1 373 €** |

> ## 🎯 Verdict
> **À 100 clients, nous sommes 3× sous le seuil le plus favorable et 8× sous le seuil européen.**
> Un serveur GPU à ~1 100-1 400 €/mois tournerait **inoccupé ~95 % du temps**.
> **L'auto-hébergement ne se rentabilise jamais à notre échelle.** Même en divisant par deux tous les prix d'API, la conclusion tient.

### ⚠️ Le piège du « GPU à la seconde »
Le calcul à la facturation par seconde ne sauve pas l'option : notre pipeline produit **24 000 tokens de sortie** par génération, soit ~8 minutes de GPU — **le prix d'une API premium**, avec une qualité en français inférieure et des délais de démarrage à froid. **Un pipeline qui écrit beaucoup est le pire cas pour le serverless GPU.**

> ✅ **Décision D21 : on ne provisionne aucun GPU. Ni maintenant, ni en phase 2.** On construit le produit pour que ce ne soit jamais nécessaire.

---

## 2. Architecture LLM en 3 phases

### 🟢 Phase 1 — Lancement (0 → ~1 500 générations/mois, ≤ 75 clients)

**100 % API, routage « Europe d'abord ».**

| Passe | Modèle | Pourquoi |
|---|---|---|
| **1 — Analyse** | Classe économique, **hébergé en UE** | Travail structuré, pas créatif |
| **2 — Rédaction** | **Le meilleur disponible en français** | C'est là que se joue la qualité perçue |
| **3 — Contrôle** | Classe économique, **hébergé en UE**, température ~0 | Vérification déterministe |

**🔑 Le levier n°1 : la mise en cache du prompt.** Nos 3 passes réutilisent le **même préfixe de ~15 000 tokens** (fiche entreprise + marché + bibliothèques). La mise en cache réduit le coût d'entrée d'environ **65 %**. **C'est le plus gros gain unitaire disponible, et il est gratuit à implémenter.**

> **Coût phase 1 : 60-250 €/mois** (LLM + transcription) **+ 20-40 €/mois** d'hébergement applicatif.

**🔔 Déclencheur de passage en phase 2 :** facture LLM > 400 €/mois sur 3 mois consécutifs, **OU** > 2 000 générations/mois.

### 🟡 Phase 2 — Croissance (~2 000 → ~6 000 générations/mois)

**Toujours zéro GPU. On optimise, on n'achète pas.**
- Passes 1 et 3 basculées vers une classe à bas coût
- Seule la passe créative reste premium
- **Traitement par lot** (−50 %) pour tout ce qui n'est pas interactif (ex. le rituel hebdomadaire, généré la nuit)
- 🏆 **Investissement au meilleur retour de tout le plan : un jeu d'évaluation de 30 à 50 vrais briefs français notés.** Il permet de dégrader les modèles **sur preuve**, pas au ressenti. Sans lui, on paie du premium par peur.

> **Coût phase 2 : 250-700 €/mois.**

**🔔 Déclencheur de passage en phase 3 :** > 6 000 générations/mois soutenues (≈ 300 clients) **ET** une charge diurne régulière — **ou** une exigence contractuelle de non-transfert.

### 🔵 Phase 3 — Échelle (improbable avant ~300 clients)
Un serveur GPU 48 Go en UE, modèle **sous licence Apache 2.0** quantifié, pour les passes de volume. API premium conservée en repli et pour la passe créative.

> **Coût phase 3 : ~1 100-1 400 €/mois de GPU + exploitation + ~150 € d'API résiduelle.**

---

## 3. 🇪🇺 Souveraineté : une économie de conformité, pas un slogan

> **C'est l'argument technique le plus sous-estimé du dossier.**

| Hébergement | Obligations RGPD |
|---|---|
| **Fournisseur européen** (France / UE) | ✅ **Aucune formalité de transfert.** Pas d'analyse d'impact, pas de clauses contractuelles types, pas de vérification d'adéquation |
| Fournisseur américain | 🔴 Vérification d'adéquation **à la date du transfert** OU clauses types **+ analyse d'impact du transfert** · exposition au Cloud Act à documenter |
| ⚠️ Région « UE » d'un cloud américain | 🔴 Donne la résidence des données, **pas l'immunité au Cloud Act** → l'analyse de transfert reste due |

> 💡 **Pour un organisme certifié Qualiopi exposé à l'audit, c'est du dé-risquage bon marché.** Un contrôleur qui voit « données traitées en France » ne pose pas la question suivante. Un contrôleur qui voit un transfert hors UE en pose dix.

### Les 5 obligations à remplir (quel que soit le fournisseur)

| # | Obligation | Statut |
|---|---|---|
| 1 | **Contrat de sous-traitance (art. 28)** signé avec chaque fournisseur LLM et transcription | ⬜ À faire |
| 2 | **Configuration non-entraînement + rétention minimale** chez chaque fournisseur | ⬜ À faire |
| 3 | **Registre des traitements** + politique de confidentialité **nommant chaque fournisseur** | ⬜ À faire |
| 4 | **Information des bénéficiaires** (art. 13) — se branche sur les obligations d'information Qualiopi | ⬜ À faire |
| 5 | Analyse d'impact (AIPD) : probablement non requise pour de la génération de scripts — **mais documenter le raisonnement** | ⬜ À faire |

### 🔴 Le piège de qualification à connaître

> **« Données publiques d'entreprise » ne sort PAS du RGPD pour nos personas.**
> Karim (artisan), Sophie (restauratrice), Léa (salon) sont très majoritairement des **entrepreneurs individuels** — donc des **personnes physiques**. Leur raison sociale est leur nom.
> **À traiter comme des données personnelles**, au même titre que les enregistrements vocaux du module `E2`.

---

## 4. BYOK (le client fournit sa propre clé) — décision

> ❌ **Décision D22 : pas de BYOK en phases 1 et 2.**

| Raison | Détail |
|---|---|
| **Inadapté à la cible** | Un artisan ou un restaurateur **ne créera jamais** de compte chez un fournisseur d'IA. C'est une fonction d'entreprise, pas de TPE. |
| **Le vrai risque est contractuel, pas technique** | Les conditions d'utilisation des fournisseurs interdisent généralement de **revendre ou relouer l'accès**. Le schéma risqué, c'est **notre clé servant des clients payants**. |
| **Devenir gardien du secret d'autrui** | Si on relaie la clé du client, on est responsable de sa protection : chiffrement par enveloppe, clé par locataire, déchiffrement en mémoire seulement, jamais en journal. Charge lourde pour un bénéfice nul à ce stade. |
| **Le BYOK n'efface rien côté RGPD** | Si la donnée traverse notre back-end, nous restons sous-traitant et le fournisseur devient sous-traitant ultérieur. |

> ✅ **À garder pour le rare gros client avec exigence informatique** (phase 2+). Et **faire valider par un conseil** notre schéma de facturation au regard des conditions d'utilisation des fournisseurs.

---

## 5. Sources de données — verdicts juridiques

| Source | Usage | Coût/mois | Verdict |
|---|---|---|---|
| **API Recherche d'entreprises** (DINUM) | Nom → SIREN, NAF, adresse | **0 €** | ✅ Open data, sans clé |
| **API Sirene / INSEE** | NAF, effectif, établissements | **0 €** | ✅ Source autoritative (30 req/min) |
| **Pappers** | Dirigeants, bilans | ~20 € | ✅ API B2B payante |
| **Lecture du site client** | Offres, ton, preuves | 0-5 € | ✅ **Sous mandat écrit au contrat** |
| **Meta Ad Library** (`FR`, toutes pubs) | Publicités des concurrents | **0 €** | ⚠️ **Zone grise** — données publiques par obligation DSA, mais usage commercial discuté |
| **Google Ads Transparency** (jeu BigQuery public) | Publicités Google des concurrents | **≈ 0 €** | ✅ **La plus propre juridiquement.** Officiel, gratuit, France couverte |
| **DataForSEO** | Paysage local, fiches concurrentes | ~15 € | ✅/⚠️ Meilleur rapport prix/fonction |
| **Google Business Profile** (API) | Audit de **sa propre** fiche | 0 € | ✅ Via délégation d'accès du client |

### ❌ Les 6 interdits absolus

| # | Interdit | Raison |
|---|---|---|
| 1 | Réexposer les données de Foreplay / AdSpy / Minea / BigSpy dans notre produit | Conditions d'utilisation : scraping, œuvres dérivées et revente interdits. ✅ *Autorisé comme outil de recherche interne pour notre équipe* |
| 2 | API TikTok (Research / Commercial Content Library) | **Utilisateurs commerciaux explicitement inéligibles** — candidater serait une fausse déclaration |
| 3 | Meta Content Library | Recherche non commerciale uniquement |
| 4 | Stocker une base d'avis Google Places | Mise en cache interdite au-delà de l'identifiant de lieu |
| 5 | Scraping connecté de Meta ou TikTok | Conditions opposables comme titulaire de compte → **risque de bannissement du compte publicitaire dont dépend `D3`** |
| 6 | Réhéberger les créas vidéo des concurrents | Droit d'auteur → lier vers l'aperçu officiel, ne stocker que l'analyse dérivée |

> 🔴 **Premier chantier technique, avant toute ligne de code : un appel de test réel à l'API Meta Ad Library** avec `ad_reached_countries=['FR']&ad_type=ALL`. Les sources divergent sur ce qui est réellement renvoyé en UE. **10 minutes de test tranchent toute l'architecture du module `E1`.**

---

## 6. Transcription vocale (module `E2`)

| Décision | ✅ **API, jamais auto-hébergé** |
|---|---|
| **Volume** | 100 clients × 4 dictées de 15 min = **6 000 min/mois** |
| **Coût** | **~1 à 36 €/mois** selon le fournisseur |
| **Choix** | Fournisseur **européen** (souveraineté + meilleure qualité en français), repli sur un service standard |
| ⚠️ **RGPD** | Les enregistrements vocaux sont des **données personnelles** → transcrire puis **supprimer l'audio par défaut** |

> Auto-héberger un modèle de transcription pour économiser 30 €/mois serait absurde.

---

## 7. Budget d'infrastructure consolidé

| Poste | Phase 1 (≤75 clients) | Phase 2 (~300 clients) |
|---|---|---|
| LLM (API, routage UE) | 40-200 € | 250-700 € |
| Transcription vocale | 1-36 € | 36-100 € |
| Base de données / auth / stockage (UE) | 25 € | 50 € |
| Hébergement applicatif (UE) | 20-40 € | 60 € |
| Données entreprise (Pappers) | 20 € | 20 € |
| Données locales (DataForSEO) | 15 € | 40 € |
| **TOTAL** | **≈ 120-335 €/mois** | **≈ 455-970 €/mois** |

> À comparer avec le chiffre d'affaires d'abonnement correspondant : **75 clients × 79 € = 5 925 €/mois**.
> **Marge brute logicielle ≈ 94 %.** C'est exactement le profil économique qui justifie la thèse `D0`.

---

## 8. Les 4 actions techniques de cette semaine

| # | Action | Durée |
|---|---|---|
| 1 | 🔴 **Test réel de l'API Meta Ad Library** (`FR` + toutes pubs) — tranche l'architecture `E1` | 10 min |
| 2 | Vérifier sur pages officielles les prix des fournisseurs européens | 30 min |
| 3 | Demander les **contrats de sous-traitance (art. 28)** aux fournisseurs européens retenus | 20 min |
| 4 | ❌ **Ne provisionner aucun GPU** | — |

---

## 9. Décisions à acter

| # | Décision | Recommandation |
|---|---|---|
| **D21** | Hébergement LLM | ✅ **API uniquement. Aucun GPU avant ~300 clients** (seuil démontré §1) |
| **D22** | BYOK | ✅ **Non en phases 1-2.** Option entreprise plus tard |
| **D23** | Souveraineté | ✅ **Fournisseurs européens par défaut** — supprime toute formalité de transfert |
| **D24** | Mise en cache du prompt | ✅ **Dès la v1** — c'est le plus gros levier de coût disponible |
| **D25** | Jeu d'évaluation | ✅ **30-50 briefs français notés** avant tout choix de modèle |

---

> **Suite :** `E4_Idees_Strategiques.md`
