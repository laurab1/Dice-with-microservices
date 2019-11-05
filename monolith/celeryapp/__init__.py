from celery import Celery


celery = None


def create_celery_app(app=None):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=['monolith.task'])
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Overrides regular context of celery task to use also the provided
        application context.
        """
        def __call__(self, *args, **kwargs):
            if not celery.conf.CELERY_ALWAYS_EAGER:
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
