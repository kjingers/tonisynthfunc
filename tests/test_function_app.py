"""
Unit tests for function_app.py HTTP endpoints

Uses mocking to avoid actual Azure service calls.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import azure.functions as func


# Mock environment variables before importing function_app
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up required environment variables for all tests"""
    monkeypatch.setenv("SPEECH_SERVICE_KEY", "test-speech-key")
    monkeypatch.setenv("SPEECH_SERVICE_REGION", "eastus")
    monkeypatch.setenv("STORAGE_ACCOUNT_NAME", "teststorage")
    monkeypatch.setenv("STORAGE_ACCOUNT_KEY", "dGVzdC1rZXk=")
    monkeypatch.setenv("STORAGE_CONTAINER_NAME", "audio-files")


def create_mock_request(body: dict, method: str = "POST", params: dict = None) -> Mock:
    """Create a mock HTTP request"""
    req = Mock(spec=func.HttpRequest)
    req.get_json.return_value = body
    req.method = method
    req.params = params or {}
    req.url = "https://test.azurewebsites.net/api/batch-start"
    return req


class TestBatchStartEndpoint:
    """Tests for /api/batch-start endpoint"""
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_successful_synthesis_start(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """Successfully start a batch synthesis"""
        from function_app import batch_start
        
        # Mock Azure Speech API response
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "Once upon a time, there was a brave little dragon.",
            "voice": "en-US-GuyNeural",
            "style": "friendly"
        })
        
        response = batch_start(req)
        
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["status"] == "started"
        assert "synthesis_id" in body
        assert "audio_url" in body
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_missing_text_returns_400(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """Return 400 when text is missing"""
        from function_app import batch_start
        
        req = create_mock_request({"voice": "en-US-GuyNeural"})
        
        response = batch_start(req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert "error" in body
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_character_voices_enabled(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """Test with character voices enabled"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": '"Hello," said Mary. "Hi," replied John.',
            "enable_character_voices": True
        })
        
        response = batch_start(req)
        
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["enable_character_voices"] is True
    
    @patch("function_app.requests.put")
    def test_azure_api_failure(self, mock_put, mock_env_vars):
        """Handle Azure Speech API failure"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=500,
            text="Internal Server Error"
        )
        
        req = create_mock_request({"text": "Test text"})
        
        response = batch_start(req)
        
        assert response.status_code == 500


class TestBatchCheckEndpoint:
    """Tests for /api/batch-check endpoint"""
    
    @patch("function_app.requests.get")
    def test_missing_synthesis_id(self, mock_get, mock_env_vars):
        """Return 400 when synthesis_id is missing"""
        from function_app import batch_check
        
        req = Mock(spec=func.HttpRequest)
        req.params = {}
        
        response = batch_check(req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert "synthesis_id" in body["error"].lower()
    
    @patch("function_app.requests.get")
    def test_synthesis_not_found(self, mock_get, mock_env_vars):
        """Return 404 when synthesis job not found"""
        from function_app import batch_check
        
        mock_get.return_value = Mock(status_code=404)
        
        req = Mock(spec=func.HttpRequest)
        req.params = {"synthesis_id": "nonexistent-id"}
        
        response = batch_check(req)
        
        assert response.status_code == 404


class TestSyncTtsEndpoint:
    """Tests for /api/sync-tts endpoint"""
    
    @patch("function_app.requests.post")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_successful_sync_synthesis(self, mock_sas, mock_blob, mock_post, mock_env_vars):
        """Successfully synthesize short text"""
        from function_app import sync_tts
        
        mock_post.return_value = Mock(
            status_code=200,
            content=b"fake-audio-data"
        )
        mock_sas.return_value = "test-sas-token"
        mock_blob.return_value.get_blob_client.return_value.upload_blob = Mock()
        
        req = create_mock_request({
            "text": "Hello, this is a short test."
        })
        
        response = sync_tts(req)
        
        assert response.status_code == 200
        body = json.loads(response.get_body())
        assert body["status"] == "success"
        assert "url" in body
    
    def test_text_too_long(self, mock_env_vars):
        """Return 400 when text exceeds limit"""
        from function_app import sync_tts
        
        long_text = "a" * 6000  # Over 5000 char limit
        req = create_mock_request({"text": long_text})
        
        response = sync_tts(req)
        
        assert response.status_code == 400
        body = json.loads(response.get_body())
        assert "too long" in body["error"].lower()
    
    def test_missing_text_returns_400(self, mock_env_vars):
        """Return 400 when text is missing"""
        from function_app import sync_tts
        
        req = create_mock_request({})
        
        response = sync_tts(req)
        
        assert response.status_code == 400


class TestAdventureModeDetection:
    """Tests for automatic adventure/story mode detection"""
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_story_in_title_enables_character_voices(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """'story' in first words should enable character voices"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "A Bedtime Story About Dragons. Once upon a time..."
        })
        
        response = batch_start(req)
        body = json.loads(response.get_body())
        
        # Should auto-enable character voices
        assert body.get("enable_character_voices") is True
        assert body.get("adventure_mode_auto_detected") is True
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_adventure_in_title_enables_character_voices(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """'adventure' in first words should enable character voices"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "The Great Adventure Begins Here. Chapter 1..."
        })
        
        response = batch_start(req)
        body = json.loads(response.get_body())
        
        assert body.get("enable_character_voices") is True
        assert body.get("adventure_mode_auto_detected") is True
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_once_upon_a_time_enables_character_voices(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """'Once upon a time' opening should enable character voices"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "Once upon a time, in a land far away, there lived a princess."
        })
        
        response = batch_start(req)
        body = json.loads(response.get_body())
        
        assert body.get("enable_character_voices") is True
        assert body.get("adventure_mode_auto_detected") is True
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_explicit_false_overrides_detection(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """Explicit enable_character_voices=False should override auto-detection"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "A Story About Dragons. Once upon a time...",
            "enable_character_voices": False
        })
        
        response = batch_start(req)
        body = json.loads(response.get_body())
        
        # User explicitly disabled, should respect that
        assert body.get("enable_character_voices") is False
        assert body.get("adventure_mode_auto_detected") is False
    
    @patch("function_app.requests.put")
    @patch("function_app.BlobServiceClient")
    @patch("function_app.generate_blob_sas")
    def test_non_story_text_no_auto_detection(self, mock_sas, mock_blob, mock_put, mock_env_vars):
        """Regular text should not auto-enable character voices"""
        from function_app import batch_start
        
        mock_put.return_value = Mock(
            status_code=201,
            json=lambda: {"status": "NotStarted"}
        )
        mock_sas.return_value = "test-sas-token"
        
        req = create_mock_request({
            "text": "Today we will learn about the solar system. The sun is at the center."
        })
        
        response = batch_start(req)
        body = json.loads(response.get_body())
        
        # Should not auto-enable for educational content
        assert body.get("adventure_mode_auto_detected") is False
