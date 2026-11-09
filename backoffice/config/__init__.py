# Celery doit etre charge au demarrage de Django pour que le decorateur
# @shared_task trouve son application.
from .celery import app as celery_app

__all__ = ("celery_app",)
