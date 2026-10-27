# Automatisation Leads Meta → WhatsApp → SMS

Chaque lead qui remplit ton formulaire Meta Lead Ads reçoit **en quelques secondes** un message WhatsApp personnalisé selon ses réponses. Si le WhatsApp échoue (pas de compte WhatsApp, numéro invalide...), un **SMS** part automatiquement à la place.

```
Formulaire Meta ──webhook──▶ VPS (ce service) ──▶ WhatsApp Cloud API
                                    ▲                    │ échec (statut "failed")
                                    └──webhook statut────┘
                                    └──────────▶ SMS (ton téléphone via httpSMS, ou Twilio)
```

## Pourquoi pas n8n ?
Le fallback SMS dépend d'un webhook de statut qui arrive **après** l'envoi WhatsApp : il faut mémoriser chaque message envoyé et vérifier la signature Meta. Un service Node de ~250 lignes sans dépendance le fait de façon fiable, testée, et consomme ~40 Mo de RAM sur le VPS. Un n8n pourra cohabiter plus tard sur le même VPS si besoin.

## Ce que tu dois préparer (checklist)

### 1. Le VPS Hostinger
- [ ] IP du VPS + accès SSH root
- [ ] Un sous-domaine (ex. `leads.tondomaine.fr`) avec un enregistrement DNS **A** vers l'IP du VPS (HTTPS automatique via Caddy, obligatoire pour Meta)
- [ ] Ports 80 et 443 ouverts (pare-feu Hostinger)

### 2. Meta — Leads
- [ ] App sur developers.facebook.com (type Business) → récupérer la **Clé secrète** (`META_APP_SECRET`)
- [ ] **Token de Page** avec `leads_retrieval`, `pages_manage_metadata`, `pages_show_list` (`META_PAGE_ACCESS_TOKEN`) — idéalement via un *utilisateur système* du Business Manager (token sans expiration)
- [ ] Dans l'app > Webhooks > objet **Page** : URL `https://leads.tondomaine.fr/webhook`, token de vérification = `META_VERIFY_TOKEN`, cocher **leadgen**
- [ ] Abonner la page à l'app :
  `curl -X POST "https://graph.facebook.com/v21.0/PAGE_ID/subscribed_apps?subscribed_fields=leadgen&access_token=PAGE_TOKEN"`

### 3. Meta — WhatsApp Business
- [ ] Ajouter le produit **WhatsApp** à l'app, créer/relier un compte WhatsApp Business
- [ ] Enregistrer un numéro. ⚠️ Un numéro utilisé par l'API **ne peut plus être utilisé dans l'appli WhatsApp classique**. Prends un 2ᵉ numéro (SIM ou numéro virtuel) — ou utilise la *coexistence* de l'appli WhatsApp Business si ton pays/compte y a accès
- [ ] Récupérer **ID du numéro** (`WA_PHONE_NUMBER_ID`) et un token d'utilisateur système avec `whatsapp_business_messaging` (`WA_ACCESS_TOKEN`)
- [ ] Webhooks > objet **WhatsApp Business Account** : même URL / même token, cocher **messages** (sert au fallback SMS)
- [ ] Créer le modèle de message `lead_bienvenue`, langue **Français**, catégorie *Marketing* ou *Utility*, corps :

  > Bonjour {{1}}, merci pour {{2}} ! {{3}} Répondez directement à ce message pour qu'on échange.

  Attendre l'approbation Meta (quelques minutes à 24 h). D'ici là, tu peux mettre `SMS_ONLY=true`.

### 4. SMS de secours
- **Avec TON numéro (recommandé pour toi)** : installer l'appli Android **httpSMS** (httpsms.com) sur ton téléphone, se connecter, copier la clé API → `SMS_PROVIDER=httpsms`, `HTTPSMS_API_KEY`, `HTTPSMS_FROM=+336...`. Les SMS partent de ta SIM et les réponses arrivent sur ton téléphone. (iPhone : pas possible, utiliser Twilio.)
- **Twilio** : numéro ou expéditeur alphanumérique (ex. « PIERRE ») → `SMS_PROVIDER=twilio` + identifiants.

## Personnaliser les messages
Tout se passe dans `config/messages.json`, sans toucher au code :
- `regles` : testées dans l'ordre, la 1ʳᵉ qui correspond gagne. `champ` = nom technique de la question du formulaire, `contient` / `egal` = réponse attendue (accents/majuscules ignorés).
- `defaut` : message si aucune règle ne correspond.
- `sms` : texte du SMS, variables `{prenom}`, `{sujet}`, `{message}` et tout champ du formulaire.

Pour connaître les noms techniques des champs de ton formulaire :
`curl "https://graph.facebook.com/v21.0/FORM_ID?fields=questions&access_token=PAGE_TOKEN"`

Après modification sur le VPS : `docker compose restart leads`.

## Déploiement
```bash
cd automation-leads
cp .env.example .env      # puis remplir
./deploy.sh root@IP_DU_VPS
```

## Tester de bout en bout
1. Outil de test Meta : https://developers.facebook.com/tools/lead-ads-testing → choisir page + formulaire → « Créer un lead »
2. Regarder les logs : `docker compose logs -f leads` (sur le VPS, dans `/opt/automation-leads`)

## Légal (France)
- Le formulaire Meta doit mentionner que le lead sera recontacté par WhatsApp/SMS (case ou texte de consentement + politique de confidentialité).
- SMS commercial : mention STOP obligatoire (déjà dans le texte par défaut) ; éviter les envois dimanche/jours fériés et hors 8 h–20 h.

## Tests
`npm test`
