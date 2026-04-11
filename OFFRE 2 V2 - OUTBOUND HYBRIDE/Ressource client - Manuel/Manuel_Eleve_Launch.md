# Manuel Opérationnel Élève : OUTBOUND HYBRIDE (Launch)

> [!IMPORTANT]
> **Objectif du niveau 기초 :** Ce premier niveau pose les fondations de votre machine à prospects. L'objectif est de mettre en place les capteurs (Tracking), d'activer la capture d'intention sur Google et d'extraire vos 2000 premiers contacts parfaits.

---

## MODULE 1 : Stratégie d'Acquisition Intentionniste

- [ ] **Configuration Google Ads "Search Intent"**
  Créez votre compte publicitaire. Définissez vos 10 mots-clés "Achat immédiat" (ex: "expert fiscalité b2b marseille").
  > *(Espace prévu pour capture Écran : Liste des mots-clés Google Ads)*

- [ ] **Définition du Budget & CPA Cible**
  Paramétrez votre budget quotidien. Commencez avec un test de 20€/jour et surveillez votre coût par lead.

---

## MODULE 2 : Ingénierie de Tracking (GTM / Pixel)

> **Flux de Données :** Visiteur → Clic → GTM → Trigger → Pixel Meta & Conversion Google Analytics 4.

- [ ] **Installation de Google Tag Manager (GTM)**
  Copiez le script GTM et injectez-le dans le `<head>` de votre site web.

- [ ] **Configuration du Pixel de Conversion**
  Créez un "Trigger" qui se déclenche uniquement sur la page "Merci" ou "Confirmation de RDV". Vérifiez avec l'extension Tag Assistant.

---

## MODULE 3 : Extraction & Enrichissement Data (Apollo)

- [ ] **Matrice Persona (Ciblage)**
  Dans Apollo.io, entrez vos critères : Taille d'entreprise, Poste précis, Secteur, Chiffre d'affaires.

- [ ] **Extraction & Nettoyage des Emails**
  Exportez la liste en CSV. Passez-la dans un outil de vérification (NeverBounce) pour éliminer les adresses invalides et protéger votre réputation d'envoi.

---

## MODULE 4 : Speed-to-Lead (Automatisation Make)

- [ ] **Configuration du Webhook**
  Créez un scénario Make.com. Connectez votre formulaire de site (Typeform/WPForms) au Webhook d'entrée.

- [ ] **Alerte Immédiate**
  Ajoutez un module Slack ou Email à la fin du scénario pour être prévenu sur votre téléphone à la milliseconde près dès qu'un prospect s'inscrit.
  > *(Espace prévu pour capture : Scénario Make complet)*
