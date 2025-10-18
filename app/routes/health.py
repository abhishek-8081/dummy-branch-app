from flask import Blueprint, jsonify
from sqlalchemy import text
from app.db import SessionContext
import logging

bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)


@bp.route("/health", methods=["GET"])
def health():
    """
    Enhanced health check that verifies:
    1. API is running
    2. Database connectivity
    3. Database can execute queries
    """
    health_status = {
        "status": "healthy",
        "checks": {
            "api": "ok",
            "database": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        with SessionContext() as session:
            # Try to execute a simple query
            result = session.execute(text("SELECT 1"))
            result.fetchone()
        
        health_status["checks"]["database"] = "ok"
        logger.info("Health check passed - all systems operational")
        return jsonify(health_status), 200
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "failed"
        health_status["error"] = str(e)
        logger.error(f"Health check failed - database error: {str(e)}")
        return jsonify(health_status), 503
