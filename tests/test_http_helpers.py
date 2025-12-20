"""
Unit tests for http_helpers.py
"""
import pytest
import json
from http_helpers import (
    json_response,
    error_response,
    validation_error,
    not_found_error,
    service_unavailable_error,
    success_response
)


class TestJsonResponse:
    """Tests for json_response function"""
    
    def test_basic_response(self):
        response = json_response({"key": "value"})
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["key"] == "value"
    
    def test_custom_status_code(self):
        response = json_response({"data": "test"}, status_code=201)
        assert response.status_code == 201
    
    def test_content_type(self):
        response = json_response({"test": True})
        assert response.mimetype == "application/json"


class TestErrorResponse:
    """Tests for error_response function"""
    
    def test_basic_error(self):
        response = error_response("Something went wrong")
        assert response.status_code == 500
        body = json.loads(response.get_body())
        assert body["error"] == "Something went wrong"
    
    def test_custom_status_code(self):
        response = error_response("Bad request", status_code=400)
        assert response.status_code == 400
    
    def test_with_details(self):
        response = error_response("Failed", details="More info")
        body = json.loads(response.get_body())
        assert body["details"] == "More info"
    
    def test_with_error_code(self):
        response = error_response("Failed", error_code="CUSTOM_ERROR")
        body = json.loads(response.get_body())
        assert body["error_code"] == "CUSTOM_ERROR"


class TestValidationError:
    """Tests for validation_error function"""
    
    def test_basic_validation_error(self):
        response = validation_error("Invalid input")
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert body["error"] == "Invalid input"
        assert body["error_code"] == "VALIDATION_ERROR"
    
    def test_with_field(self):
        response = validation_error("Required field", field="text")
        body = json.loads(response.get_body())
        assert body["field"] == "text"


class TestNotFoundError:
    """Tests for not_found_error function"""
    
    def test_basic_not_found(self):
        response = not_found_error("Synthesis job")
        assert response.status_code == 404
        body = json.loads(response.get_body())
        assert "not found" in body["error"].lower()
    
    def test_with_identifier(self):
        response = not_found_error("Synthesis job", identifier="abc-123")
        body = json.loads(response.get_body())
        assert "abc-123" in body["error"]


class TestServiceUnavailableError:
    """Tests for service_unavailable_error function"""
    
    def test_basic_unavailable(self):
        response = service_unavailable_error("Speech Service")
        assert response.status_code == 503
        body = json.loads(response.get_body())
        assert "Speech Service" in body["error"]
        assert "unavailable" in body["error"].lower()


class TestSuccessResponse:
    """Tests for success_response function"""
    
    def test_basic_success(self):
        response = success_response({"data": "value"})
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["data"] == "value"
    
    def test_with_message(self):
        response = success_response({"data": "value"}, message="Operation completed")
        body = json.loads(response.get_body())
        assert body["message"] == "Operation completed"
