"""
Unit tests for exceptions.py
"""
import pytest
from exceptions import (
    ToniSynthError,
    ConfigurationError,
    ValidationError,
    SpeechServiceError,
    StorageError,
    SynthesisNotFoundError,
    SynthesisFailedError,
    SynthesisTimeoutError,
    TextTooLongError,
    RateLimitError
)


class TestToniSynthError:
    """Tests for base ToniSynthError"""
    
    def test_basic_error(self):
        error = ToniSynthError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code == "UNKNOWN_ERROR"
        assert error.details is None
    
    def test_error_with_code_and_details(self):
        error = ToniSynthError("Test", error_code="TEST_ERROR", details="More info")
        assert error.error_code == "TEST_ERROR"
        assert error.details == "More info"
    
    def test_to_dict(self):
        error = ToniSynthError("Test", error_code="CODE", details="Details")
        result = error.to_dict()
        assert result["error"] == "Test"
        assert result["error_code"] == "CODE"
        assert result["details"] == "Details"


class TestConfigurationError:
    """Tests for ConfigurationError"""
    
    def test_basic_config_error(self):
        error = ConfigurationError("Missing config")
        assert error.error_code == "CONFIGURATION_ERROR"
    
    def test_with_missing_vars(self):
        error = ConfigurationError("Missing vars", missing_vars=["VAR1", "VAR2"])
        assert "VAR1" in error.details
        assert "VAR2" in error.details
        assert error.missing_vars == ["VAR1", "VAR2"]


class TestValidationError:
    """Tests for ValidationError"""
    
    def test_basic_validation_error(self):
        error = ValidationError("Invalid input")
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field is None
    
    def test_with_field(self):
        error = ValidationError("Invalid", field="text")
        assert error.field == "text"
    
    def test_to_dict_includes_field(self):
        error = ValidationError("Invalid", field="text")
        result = error.to_dict()
        assert result["field"] == "text"


class TestSpeechServiceError:
    """Tests for SpeechServiceError"""
    
    def test_basic_speech_error(self):
        error = SpeechServiceError("API failed")
        assert error.error_code == "SPEECH_SERVICE_ERROR"
    
    def test_with_status_code(self):
        error = SpeechServiceError("Failed", status_code=500, api_response="Server error")
        assert error.status_code == 500
        assert error.api_response == "Server error"


class TestStorageError:
    """Tests for StorageError"""
    
    def test_basic_storage_error(self):
        error = StorageError("Upload failed")
        assert error.error_code == "STORAGE_ERROR"
    
    def test_with_blob_and_operation(self):
        error = StorageError("Failed", blob_name="test.mp3", operation="upload")
        assert error.blob_name == "test.mp3"
        assert error.operation == "upload"
        assert "test.mp3" in error.details


class TestSynthesisNotFoundError:
    """Tests for SynthesisNotFoundError"""
    
    def test_error_message(self):
        error = SynthesisNotFoundError("my-synthesis-id")
        assert "my-synthesis-id" in error.message
        assert error.error_code == "SYNTHESIS_NOT_FOUND"
        assert error.synthesis_id == "my-synthesis-id"


class TestSynthesisFailedError:
    """Tests for SynthesisFailedError"""
    
    def test_basic_failure(self):
        error = SynthesisFailedError("job-123")
        assert "job-123" in error.message
        assert error.error_code == "SYNTHESIS_FAILED"
    
    def test_with_reason(self):
        error = SynthesisFailedError("job-123", reason="Out of quota")
        assert error.reason == "Out of quota"
        assert error.details == "Out of quota"


class TestSynthesisTimeoutError:
    """Tests for SynthesisTimeoutError"""
    
    def test_timeout_error(self):
        error = SynthesisTimeoutError("job-123", timeout_seconds=180)
        assert "job-123" in error.message
        assert "180" in error.message
        assert error.error_code == "SYNTHESIS_TIMEOUT"
        assert error.synthesis_id == "job-123"
        assert error.timeout_seconds == 180


class TestTextTooLongError:
    """Tests for TextTooLongError"""
    
    def test_text_too_long(self):
        error = TextTooLongError(text_length=6000, max_length=5000)
        assert "6000" in error.message
        assert "5000" in error.message
        assert error.error_code == "TEXT_TOO_LONG"
        assert error.field == "text"


class TestRateLimitError:
    """Tests for RateLimitError"""
    
    def test_basic_rate_limit(self):
        error = RateLimitError()
        assert "Rate limit" in error.message
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
    
    def test_with_retry_after(self):
        error = RateLimitError(retry_after=60)
        assert "60 seconds" in error.message
        assert error.retry_after == 60
