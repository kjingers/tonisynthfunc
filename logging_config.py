"""
Logging Module

Provides structured logging with correlation IDs for request tracing.
"""
import logging
import uuid
import json
import functools
from typing import Optional, Any, Callable
from datetime import datetime
from contextvars import ContextVar

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get the current correlation ID"""
    return correlation_id_var.get() or str(uuid.uuid4())[:8]


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set a correlation ID for the current context.
    
    Args:
        correlation_id: Optional ID to use, generates new one if not provided
        
    Returns:
        The correlation ID that was set
    """
    cid = correlation_id or str(uuid.uuid4())[:8]
    correlation_id_var.set(cid)
    return cid


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs with context.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _format_message(
        self,
        message: str,
        level: str,
        **extra
    ) -> str:
        """Format log message as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "correlation_id": get_correlation_id(),
            "message": message
        }
        log_data.update(extra)
        return json.dumps(log_data)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message, "DEBUG", **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, "INFO", **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, "WARNING", **kwargs))
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message"""
        if exception:
            kwargs["exception_type"] = type(exception).__name__
            kwargs["exception_message"] = str(exception)
        self.logger.error(self._format_message(message, "ERROR", **kwargs))
    
    def request_start(self, endpoint: str, method: str, **kwargs):
        """Log the start of a request"""
        self.info(
            f"Request started: {method} {endpoint}",
            event="request_start",
            endpoint=endpoint,
            method=method,
            **kwargs
        )
    
    def request_end(
        self,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """Log the end of a request"""
        level = "info" if status_code < 400 else ("warning" if status_code < 500 else "error")
        getattr(self, level)(
            f"Request completed: {status_code}",
            event="request_end",
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def synthesis_start(self, synthesis_id: str, text_length: int, **kwargs):
        """Log synthesis job start"""
        self.info(
            f"Synthesis started: {synthesis_id}",
            event="synthesis_start",
            synthesis_id=synthesis_id,
            text_length=text_length,
            **kwargs
        )
    
    def synthesis_complete(
        self,
        synthesis_id: str,
        duration_seconds: float,
        size_bytes: int,
        **kwargs
    ):
        """Log synthesis job completion"""
        self.info(
            f"Synthesis completed: {synthesis_id}",
            event="synthesis_complete",
            synthesis_id=synthesis_id,
            duration_seconds=round(duration_seconds, 2),
            size_bytes=size_bytes,
            **kwargs
        )
    
    def synthesis_failed(self, synthesis_id: str, error: str, **kwargs):
        """Log synthesis job failure"""
        self.error(
            f"Synthesis failed: {synthesis_id}",
            event="synthesis_failed",
            synthesis_id=synthesis_id,
            error=error,
            **kwargs
        )


# Default logger instance
logger = StructuredLogger("tonisynthfunc")


def log_request(endpoint_name: str = None) -> Callable:
    """
    Decorator to log request start/end with timing.
    
    Usage:
        @log_request("batch-start")
        def batch_start(req):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            # Generate correlation ID for this request
            correlation_id = set_correlation_id()
            endpoint = endpoint_name or func.__name__
            
            start_time = time.time()
            logger.request_start(endpoint, "HTTP")
            
            try:
                result = func(*args, **kwargs)
                
                # Try to get status code from response
                status_code = 200
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                duration_ms = (time.time() - start_time) * 1000
                logger.request_end(endpoint, status_code, duration_ms)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Request failed: {endpoint}",
                    exception=e,
                    duration_ms=round(duration_ms, 2)
                )
                raise
        
        return wrapper
    return decorator


def configure_logging(level: str = "INFO"):
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(message)s'  # We handle formatting in StructuredLogger
    )
