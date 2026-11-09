"""Application Celery.

⚠️ `autodiscover_tasks()` cherche par defaut un module nomme **`tasks`** dans
chaque application installee. Les notres s'appellent `taches`, selon la
convention de langue du projet — sans `related_name`, AUCUNE tache n'etait
enregistree. Le symptome en production aurait ete silencieux : la tache part
dans Redis, un worker la recoit, leve `KeyError: <nom de la tache>` et
l'abandonne. Pas d'erreur visible cote application, juste des leads dont le
SIREN n'est jamais resolu et des webhooks jamais traites.

La decouverte ne regarde que la RACINE de chaque application : elle trouve
`apps.crm.taches`, mais pas `apps.integrations.meta.taches`, qui est dans un
sous-paquet. D'ou `apps/integrations/taches.py`, qui les expose a la racine.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

app = Celery("backoffice")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(related_name="taches")
