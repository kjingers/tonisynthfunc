"""
Custom Exceptions Module

Defines application-specific exceptions for better error handling.
"""


class ToniSynthError(Exception):
    """Base exception for ToniSynth application"""
    
    def __init__(self, message: str, error_code: str = None, details: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for JSON response"""
        result = {
            "error": self.message,
            "error_code": self.error_code
        }
        if self.details:
            result["details"] = self.details
        return result


class ConfigurationError(ToniSynthError):
    """Raised when configuration is missing or invalid"""
    
    def __init__(self, message: str, missing_vars: list = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=f"Missing: {', '.join(missing_vars)}" if missing_vars else None
        )
        self.missing_vars = missing_vars or []


class ValidationError(ToniSynthError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR"
        )
        self.field = field
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.field:
            result["field"] = self.field
        return result


class SpeechServiceError(ToniSynthError):
    """Raised when Azure Speech Service API call fails"""
    
    def __init__(self, message: str, status_code: int = None, api_response: str = None):
        super().__init__(
            message=message,
            error_code="SPEECH_SERVICE_ERROR",
            details=api_response
        )
        self.status_code = status_code
        self.api_response = api_response


class StorageError(ToniSynthError):
    """Raised when Azure Blob Storage operation fails"""
    
    def __init__(self, message: str, blob_name: str = None, operation: str = None):
        details = []
        if blob_name:
            details.append(f"blob: {blob_name}")
        if operation:
            details.append(f"operation: {operation}")
        
        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            details=", ".join(details) if details else None
        )
        self.blob_name = blob_name
        self.operation = operation


class SynthesisNotFoundError(ToniSynthError):
    """Raised when a synthesis job is not found"""
    
    def __init__(self, synthesis_id: str):
        super().__init__(
            message=f"Synthesis job '{synthesis_id}' not found",
            error_code="SYNTHESIS_NOT_FOUND"
        )
        self.synthesis_id = synthesis_id


class SynthesisFailedError(ToniSynthError):
    """Raised when a synthesis job fails"""
    
    def __init__(self, synthesis_id: str, reason: str = None):
        super().__init__(
            message=f"Synthesis job '{synthesis_id}' failed",
            error_code="SYNTHESIS_FAILED",
            details=reason
        )
        self.synthesis_id = synthesis_id
        self.reason = reason


class SynthesisTimeoutError(ToniSynthError):
    """Raised when synthesis job times out"""
    
    def __init__(self, synthesis_id: str, timeout_seconds: int):
        super().__init__(
            message=f"Synthesis job '{synthesis_id}' timed out after {timeout_seconds} seconds",
            error_code="SYNTHESIS_TIMEOUT"
        )
        self.synthesis_id = synthesis_id
        self.timeout_seconds = timeout_seconds


class TextTooLongError(ValidationError):
    """Raised when text exceeds maximum length"""
    
    def __init__(self, text_length: int, max_length: int):
        super().__init__(
            message=f"Text length ({text_length}) exceeds maximum ({max_length})",
            field="text"
        )
        self.error_code = "TEXT_TOO_LONG"
        self.text_length = text_length
        self.max_length = max_length


class RateLimitError(ToniSynthError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED"
        )
        self.retry_after = retry_after
