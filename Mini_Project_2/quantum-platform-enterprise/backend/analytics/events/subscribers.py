from core.events import event_bus, EventTypes
from analytics.metrics.prometheus import EXPERIMENT_CREATED_COUNT, JOB_EXECUTED_COUNT, JOB_FAILED_COUNT
import logging

logger = logging.getLogger(__name__)

async def handle_experiment_created(payload: dict):
    logger.info(f"Analytics captured Experiment Created: {payload.get('experiment_id')}")
    EXPERIMENT_CREATED_COUNT.inc()

async def handle_job_executed(payload: dict):
    provider = payload.get('provider', 'unknown')
    backend = payload.get('backend', 'unknown')
    JOB_EXECUTED_COUNT.labels(provider=provider, backend=backend).inc()

async def handle_job_failed(payload: dict):
    provider = payload.get('provider', 'unknown')
    JOB_FAILED_COUNT.labels(provider=provider).inc()

def setup_analytics_subscriptions():
    event_bus.subscribe(EventTypes.EXPERIMENT_CREATED, handle_experiment_created)
    event_bus.subscribe(EventTypes.EXPERIMENT_QUEUED, handle_job_executed)
    event_bus.subscribe(EventTypes.JOB_FAILED, handle_job_failed)
