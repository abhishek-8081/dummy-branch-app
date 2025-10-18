from flask import Flask, request
from .config import Config
import time
import logging

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config())
    
    # Setup structured JSON logging
    from .logging_config import setup_logging
    setup_logging(app)
    
    logger = logging.getLogger(__name__)
    
    # Register blueprints
    from .routes.health import bp as health_bp
    from .routes.loans import bp as loans_bp
    from .routes.stats import bp as stats_bp
    from .routes.metrics import bp as metrics_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(loans_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")
    app.register_blueprint(metrics_bp)
    
    # Middleware to record request metrics
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        try:
            # Calculate request duration
            duration = time.time() - request.start_time
            
            # Record metrics
            from .routes.metrics import record_request_metrics
            record_request_metrics(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status_code=response.status_code,
                duration=duration
            )
            
            # Log request
            logger.info(
                f"{request.method} {request.path} {response.status_code}",
                extra={
                    'duration_ms': round(duration * 1000, 2),
                    'status_code': response.status_code
                }
            )
            
        except Exception as e:
            logger.error(f"Error in after_request: {str(e)}")
        
        return response
    
    return app
