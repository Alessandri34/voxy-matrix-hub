# Manuel Opérationnel Élève : OUTBOUND HYBRIDE (Performance)

> [!IMPORTANT]
> **L'Intelligence Vocale au service de la vente :** Ce niveau transforme votre infrastructure en une force de frappe autonome. Votre IA ne se contente plus de capturer des leads, elle les appelle, les qualifie et gère les objections comme un humain le ferait.

---

## MODULE 5 : Programmation de la Voix & Synthèse

- [ ] **Sélection du Timbre de Voix (Vapi/Bland)**
  Choisissez une voix avec un accent neutre et une intonation chaleureuse. Testez la latence : elle doit être inférieure à 800ms pour une conversation naturelle.

- [ ] **Paramétrage du SSML (Pauses et Souffles)**
  Injectez des balises de respiration et d'hésitation pour briser le côté robotique.

```xml
<speak>
  Bonjour, je suis... <break time="200ms"/> l'assistant de [Entreprise]... 
</speak>
```

---

## MODULE 6 : Injection de Base de Connaissances (RAG)

- [ ] **Scraping et Injection de Documentation**
  Uploadez vos PDFs de tarifs, vos FAQs et l'historique de vos meilleures ventes dans la "Vector Database" du robot.

- [ ] **Test d'Objection**
  Appelez votre propre robot et posez une question complexe. Ajustez ses réponses si nécessaire.

---

## MODULE 7 : L'Appel Intentionnel de Qualification

> **Cinématique de l'Appel :** Décrochage Patient → Hook 3s → Validation Intention → Questions Clés → Qualifié ? → Oui (Booking RDV Humain) / Non (Désengagement Poli).

- [ ] **Configuration du Master Prompt**
  Injectez le script de qualification. Le robot doit poser les 3 questions bloquantes : Budget, Besoins, Timing.

---

## MODULE 8 : Le Pré-cadre Nurturing Silencieux

- [ ] **Séquence de Relance Automatique**
  Configurez une séquence de 3 emails dans votre CRM ou outil d'envoi. Focus sur la preuve sociale pour chauffer le prospect.

- [ ] **Liaison Call -> Email**
  Si le statut de l'appel est "No Answer", déclenchez immédiatement le premier email de la séquence via Make.com.
  > *(Espace prévu pour capture : Flux d'automatisation)*
