.PHONY: worker periodic periodicworker smtpserver redis run debug

# Starts a new celery worker. Necessary for live server testing.
worker:
	celery -A monolith.celeryapp.celery_worker.celery worker --loglevel=INFO

# Starts a new celery scheduler. Necessary for live server testing of periodic task.
# Requires also a worker that runs the task.
periodic:
	celery -A monolith.celeryapp.celery_worker.celery beat --loglevel=INFO

# Starts a new celery worker that acts both as a scheduler and a worker.
# No additional worker are required, however it is suggested to favor launching
# two separate worker and scheduler.
periodicworker:
	celery -A monolith.celeryapp.celery_worker.celery worker -B --loglevel=INFO

# Starts a local SMTP server that echos SMTP messages. Useful for live testing
# the periodic digests.
smtpserver:
	python -m aiosmtpd -n

# Starts a local redis instance.
redis:
	redis-server

# Runs the application, makes no assumption on the state of redis or celery.
run:
	FLASK_APP="monolith.app" flask run

# Runs the application in development mode, makes no assumpion on the state of
# redis or celery.
debug:
	FLASK_APP="monolith.app" FLASK_ENV="development" flask run
