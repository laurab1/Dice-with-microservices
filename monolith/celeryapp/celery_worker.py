"""Entry point for celery workers."""

from monolith.app import celeryapp, create_app

app = create_app()
celery = celeryapp.create_celery_app(app)
celeryapp.celery = celery
