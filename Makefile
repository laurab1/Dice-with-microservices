.PHONY: worker redis run

worker:
	celery -A monolith.celeryapp.celery_worker.celery worker

redis:
	redis-server

run:
	FLASK_APP="monolith.app" flask run
