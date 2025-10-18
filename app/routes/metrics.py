from flask import Blueprint, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import text
from app.db import SessionContext
import time

bp = Blueprint("metrics", __name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'loan_api_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'loan_api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

LOAN_COUNT = Gauge(
    'loan_api_total_loans',
    'Total number of loans in database'
)

LOAN_AMOUNT_TOTAL = Gauge(
    'loan_api_total_amount',
    'Total loan amount in database'
)

DATABASE_CONNECTIONS = Gauge(
    'loan_api_database_connections',
    'Number of active database connections'
)


@bp.route("/metrics", methods=["GET"])
def metrics():
    """
    Prometheus metrics endpoint
    Exposes application metrics in Prometheus format
    """
    try:
        # Update loan metrics from database
        with SessionContext() as session:
            # Get total loans count
            result = session.execute(text("SELECT COUNT(*) FROM loans"))
            loan_count = result.scalar()
            LOAN_COUNT.set(loan_count or 0)
            
            # Get total loan amount
            result = session.execute(text("SELECT COALESCE(SUM(amount), 0) FROM loans"))
            total_amount = result.scalar()
            LOAN_AMOUNT_TOTAL.set(float(total_amount or 0))
            
            # Get active connections (PostgreSQL specific)
            result = session.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ))
            active_connections = result.scalar()
            DATABASE_CONNECTIONS.set(active_connections or 0)
        
    except Exception as e:
        # If database query fails, still return metrics (just without DB stats)
        pass
    
    # Generate and return Prometheus metrics
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def record_request_metrics(method, endpoint, status_code, duration):
    """
    Helper function to record request metrics
    Call this from middleware or after each request
    """
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
