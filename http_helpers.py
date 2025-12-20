"""
HTTP Response Helpers

Standardized HTTP response creation for Azure Functions.
"""
import json
import logging
from typing import Optional, Any, Dict
import azure.functions as func


def json_response(
    data: Dict[str, Any],
    status_code: int = 200
) -> func.HttpResponse:
    """
    Create a JSON HTTP response.
    
    Args:
        data: Dictionary to serialize as JSON
        status_code: HTTP status code (default 200)
        
    Returns:
        Azure Functions HttpResponse
    """
    return func.HttpResponse(
        json.dumps(data),
        status_code=status_code,
        mimetype="application/json"
    )


def error_response(
    message: str,
    status_code: int = 500,
    details: Optional[str] = None,
    error_code: Optional[str] = None
) -> func.HttpResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        error_code: Machine-readable error code
        
    Returns:
        Azure Functions HttpResponse
    """
    body = {"error": message}
    
    if details:
        body["details"] = details
    if error_code:
        body["error_code"] = error_code
    
    # Log errors
    log_level = logging.WARNING if status_code < 500 else logging.ERROR
    logging.log(log_level, f"Error response {status_code}: {message}")
    
    return json_response(body, status_code)


def validation_error(message: str, field: Optional[str] = None) -> func.HttpResponse:
    """
    Create a 400 validation error response.
    
    Args:
        message: Validation error message
        field: Optional field name that failed validation
        
    Returns:
        Azure Functions HttpResponse with 400 status
    """
    body = {"error": message, "error_code": "VALIDATION_ERROR"}
    if field:
        body["field"] = field
    return json_response(body, 400)


def not_found_error(
    resource: str,
    identifier: Optional[str] = None
) -> func.HttpResponse:
    """
    Create a 404 not found error response.
    
    Args:
        resource: Type of resource not found
        identifier: Optional identifier that was searched
        
    Returns:
        Azure Functions HttpResponse with 404 status
    """
    message = f"{resource} not found"
    if identifier:
        message = f"{resource} '{identifier}' not found"
    
    return error_response(
        message,
        status_code=404,
        error_code="NOT_FOUND"
    )


def service_unavailable_error(
    service: str,
    details: Optional[str] = None
) -> func.HttpResponse:
    """
    Create a 503 service unavailable error response.
    
    Args:
        service: Name of the unavailable service
        details: Additional details about the outage
        
    Returns:
        Azure Functions HttpResponse with 503 status
    """
    return error_response(
        f"{service} is temporarily unavailable",
        status_code=503,
        details=details,
        error_code="SERVICE_UNAVAILABLE"
    )


def success_response(
    data: Dict[str, Any],
    message: Optional[str] = None
) -> func.HttpResponse:
    """
    Create a success response with optional message.
    
    Args:
        data: Response data
        message: Optional success message
        
    Returns:
        Azure Functions HttpResponse with 200 status
    """
    if message:
        data["message"] = message
    return json_response(data, 200)
