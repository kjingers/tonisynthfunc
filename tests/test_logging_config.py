"""
Unit tests for logging_config.py
"""
import pytest
import json
from logging_config import (
    get_correlation_id,
    set_correlation_id,
    StructuredLogger,
    log_request,
    configure_logging
)


class TestCorrelationId:
    """Tests for correlation ID functions"""
    
    def test_get_generates_id_if_not_set(self):
        """Should generate an ID if none is set"""
        cid = get_correlation_id()
        assert cid is not None
        assert len(cid) > 0
    
    def test_set_correlation_id(self):
        """Should set and return the correlation ID"""
        cid = set_correlation_id("test-123")
        assert cid == "test-123"
    
    def test_get_returns_set_id(self):
        """Should return the ID that was set"""
        set_correlation_id("my-id")
        assert get_correlation_id() == "my-id"
    
    def test_set_generates_id_if_none(self):
        """Should generate an ID if None is passed"""
        cid = set_correlation_id(None)
        assert cid is not None
        assert len(cid) == 8  # First 8 chars of UUID


class TestStructuredLogger:
    """Tests for StructuredLogger class"""
    
    def test_logger_creation(self):
        """Should create a logger with the given name"""
        logger = StructuredLogger("test-logger")
        assert logger.name == "test-logger"
    
    def test_format_message_includes_required_fields(self):
        """Formatted message should include all required fields"""
        set_correlation_id("test-cid")
        logger = StructuredLogger("test")
        
        msg = logger._format_message("Test message", "INFO", extra_key="extra_value")
        data = json.loads(msg)
        
        assert data["message"] == "Test message"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["correlation_id"] == "test-cid"
        assert "timestamp" in data
        assert data["extra_key"] == "extra_value"
    
    def test_info_logging(self, caplog):
        """Info method should log at INFO level"""
        logger = StructuredLogger("test")
        with caplog.at_level("INFO"):
            logger.info("Test info message")
        
        assert len(caplog.records) == 1
        assert "INFO" in caplog.records[0].message
    
    def test_error_logging_with_exception(self, caplog):
        """Error method should include exception info"""
        logger = StructuredLogger("test")
        exc = ValueError("Test error")
        
        with caplog.at_level("ERROR"):
            logger.error("Error occurred", exception=exc)
        
        assert len(caplog.records) == 1
        msg_data = json.loads(caplog.records[0].message)
        assert msg_data["exception_type"] == "ValueError"
        assert msg_data["exception_message"] == "Test error"
    
    def test_request_start_logging(self, caplog):
        """request_start should log with correct event"""
        logger = StructuredLogger("test")
        
        with caplog.at_level("INFO"):
            logger.request_start("batch-start", "POST")
        
        msg_data = json.loads(caplog.records[0].message)
        assert msg_data["event"] == "request_start"
        assert msg_data["endpoint"] == "batch-start"
        assert msg_data["method"] == "POST"
    
    def test_synthesis_logging(self, caplog):
        """Synthesis-specific logging methods"""
        logger = StructuredLogger("test")
        
        with caplog.at_level("INFO"):
            logger.synthesis_start("synth-123", text_length=1000)
            logger.synthesis_complete("synth-123", duration_seconds=5.5, size_bytes=102400)
        
        assert len(caplog.records) == 2
        
        start_data = json.loads(caplog.records[0].message)
        assert start_data["event"] == "synthesis_start"
        assert start_data["synthesis_id"] == "synth-123"
        
        complete_data = json.loads(caplog.records[1].message)
        assert complete_data["event"] == "synthesis_complete"
        assert complete_data["duration_seconds"] == 5.5


class TestLogRequestDecorator:
    """Tests for log_request decorator"""
    
    def test_decorator_preserves_function_name(self):
        """Decorator should preserve function metadata"""
        @log_request("test-endpoint")
        def my_function():
            return "result"
        
        assert my_function.__name__ == "my_function"
    
    def test_decorator_sets_correlation_id(self):
        """Decorator should set a new correlation ID for each request"""
        @log_request("test")
        def handler():
            return get_correlation_id()
        
        cid1 = handler()
        cid2 = handler()
        
        # Each call should get a new correlation ID
        assert cid1 != cid2
    
    def test_decorator_returns_function_result(self):
        """Decorator should return the wrapped function's result"""
        @log_request("test")
        def handler():
            return {"status": "ok"}
        
        result = handler()
        assert result == {"status": "ok"}


class TestConfigureLogging:
    """Tests for configure_logging function"""
    
    def test_configure_with_level(self):
        """Should configure logging without error"""
        # This shouldn't raise
        configure_logging("DEBUG")
        configure_logging("INFO")
        configure_logging("WARNING")
        configure_logging("ERROR")
