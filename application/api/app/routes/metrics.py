"""
Prometheus-compatible /metrics endpoint.
Uses the prometheus_client library to expose standard metrics.
Prometheus scrapes this endpoint on a schedule to collect time-series data.
"""
from fastapi import APIRouter, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST, REGISTRY
)

router = APIRouter(tags=["metrics"])

# ── Define metrics ────────────────────────────────────────────────────────────

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

tasks_created_total = Counter(
    "tasks_created_total",
    "Total tasks created",
)

tasks_completed_total = Counter(
    "tasks_completed_total",
    "Total tasks completed",
)

tasks_failed_total = Counter(
    "tasks_failed_total",
    "Total tasks failed",
)

tasks_processing_gauge = Gauge(
    "tasks_processing_current",
    "Tasks currently being processed",
)


@router.get("/metrics")
def metrics():
    """Expose all registered Prometheus metrics in text format."""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
