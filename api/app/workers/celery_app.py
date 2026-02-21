from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery('farm_intelligence', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    'weekly-recommendations': {
        'task': 'app.workers.tasks.run_weekly_recommendations_for_all_farms',
        'schedule': 60.0 * 60.0 * 24.0,
    }
}
