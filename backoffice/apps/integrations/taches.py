"""Expose les taches de l'integration a la racine de l'application.

`autodiscover_tasks` ne regarde que `<application>.taches` : il ne descend
pas dans les sous-paquets. Sans ce fichier, `apps.integrations.meta.taches`
ne serait jamais importe, et ses taches resteraient inconnues du worker.
"""

from apps.integrations.meta.taches import traiter_reception

__all__ = ["traiter_reception"]
