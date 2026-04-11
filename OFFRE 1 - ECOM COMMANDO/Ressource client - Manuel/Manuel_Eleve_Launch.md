# Manuel Opérationnel Élève : E-COM COMMANDO (Launch)

> [!IMPORTANT]
> **Objectif de ce Cahier :** Ce document est votre feuille de route. Il vous permet de refaire exactement les manipulations montrées par votre expert. Ne passez à l'étape suivante que si la case précédente est cochée de façon certaine. Votre fondation technique en dépend.

---

## MODULE 1 : Ingénierie & Déploiement CMS Premium

- [ ] **Création de l'Espace d'Hébergement**
  Rendez-vous sur Shopify.com et créez un compte sécurisé. Validez votre adresse email commerciale.
  > *(Espace prévu pour capture d'écran "Paramètres > Détails du compte")*

- [ ] **Liaison des Serveurs DNS & HTTPS**
  Allez dans `Paramètres > Domaines`. Entrez le nom de domaine acheté et modifiez les enregistrements A et CNAME chez votre hébergeur (OVH/Hostinger).
  > *(Espace prévu pour capture d'écran "Serveurs DNS")*

- [ ] **Génération des Pages Légales obligatoires**
  Allez dans `Paramètres > Politiques`. Utilisez le générateur automatique, relisez-les et rendez-les visibles dans la navigation Footer de la boutique.

---

## MODULE 2 : Intégration des Flux Financiers (Stripe)

> **Cinématique des transferts :** Acheteur (Carte Bancaire) → Stripe API → Confirmation CMS Shopify + Virement 3 Jours en Banque Entreprise.

- [ ] **Ouverture et Vérification Stripe**
  Créez votre compte sur Stripe.com. Soumettez votre Kbis, Pièce d'Identité et RIB d'entreprise pour lever les limites de blocage (KYC).

- [ ] **Liaison API Caisse**
  Sur Shopify : allez dans `Paramètres > Fournisseurs de paiement > Activer Shopify Payments ou Stripe`.
  > *(Espace prévu pour capture d'écran "Fournisseurs de Paiement")*

---

## MODULE 3 : Création Produit (Neuro-Copywriting IA)

L'objectif est d'injecter dans la base de données 5 produits hyper-optimisés émotionnellement. Nous utiliserons ChatGPT.

- [ ] **Génération du Copywriting (Bénéfice Émotionnel)**
  Ouvrez ChatGPT-4 et collez l'ingénierie de prompt suivante en modifiant les variables :

```text
Agis comme un copywriter e-commerce expert en science comportementale.
Rédige une fiche produit pour mon article : [Nom du Produit].
Ma cible principale est : [Décrire le client, ex: Femmes de 40 ans cherchant le confort].

Règles de rédaction :
1. Crée un Titre (Titre 1) captivant centré sur le résultat émotionnel, non pas l'objet.
2. Introduction : Appuie sur la douleur actuelle du client.
3. Corps : Explique comment le produit résout la douleur grâce à 3 listes à puces dynamiques.
4. N'utilise pas de mots génériques. Utilise des mots viscéraux.
```

- [ ] **Intégration Sémantique & Média**
  Dans Shopify (`Produits > Ajouter`), collez le résultat. Appliquez les balises **Titre 2 (H2)** sur vos sous-titres. Importez vos images compressées (moins de 200ko).

- [ ] **Accessibilité Balises ALT**
  Cliquez sur chaque image produit, naviguez vers "Modifier le texte alternatif" et décrivez physiquement l'image pour l'algorithme SEO de Google.

---

## MODULE 4 : Transfert de Compétence & Pilotage Quotidien

Le "Run" quotidien de votre boutique. Vous êtes maintenant prêt à opérer de manière autonome.

- [ ] **Traitement Logistique (Fulfillment)**
  À la réception d'une commande (Onglet Commandes), sélectionnez la commande, préparez le colis, et cliquez sur le bouton "Traiter la commande" (Fulfill) pour informer automatiquement le client de l'expédition et fournir le n° de suivi.
  > *(Espace prévu pour capture d'écran "Traiter la commande")*

- [ ] **Autonomie SAV : Le Remboursement Total/Partiel**
  Pour rembourser un client (annulation avant envoi) : Ouvrez la commande > Bouton "Rembourser" > Sélectionnez le montant > Cochez l'envoi de l'email de notification automatique. Ce bouton donne directement l'ordre à Stripe sans login bancaire.
