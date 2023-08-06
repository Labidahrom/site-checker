from django.test.runner import DiscoverRunner


class TestRunnerWithCeleryEagerSet(DiscoverRunner):

    def setup_test_environment(self, *args, **kwargs):
        super().setup_test_environment(*args, **kwargs)

        from django.conf import settings
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
