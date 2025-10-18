import logging
import sys
from pythonjsonlogger import jsonlogger
from flask import has_request_context, request
import os


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds request context
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add request context if available
        if has_request_context():
            log_record['request_id'] = request.headers.get('X-Request-ID', 'N/A')
            log_record['method'] = request.method
            log_record['path'] = request.path
            log_record['remote_addr'] = request.remote_addr
        
        # Add environment
        log_record['environment'] = os.getenv('FLASK_ENV', 'development')


def setup_logging(app):
    """
    Setup structured JSON logging for the Flask application
    """
    # Get log level from environment or default to INFO
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Use JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(handler)
    
    # Configure Flask app logger
    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    
    # Log startup message
    app.logger.info(
        f"Logging configured - Level: {log_level_name}, Environment: {os.getenv('FLASK_ENV', 'development')}"
    )
