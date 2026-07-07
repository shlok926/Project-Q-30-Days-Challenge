from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

EXPERIMENT_CREATED_COUNT = Counter('quantum_experiments_created_total', 'Total number of created experiments')
JOB_EXECUTED_COUNT = Counter('quantum_jobs_executed_total', 'Total number of executed jobs', ['provider', 'backend'])
JOB_FAILED_COUNT = Counter('quantum_jobs_failed_total', 'Total number of failed jobs', ['provider'])

API_LATENCY = Histogram('api_latency_seconds', 'Latency of API responses in seconds', ['endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users in the system')

def get_metrics_response():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
