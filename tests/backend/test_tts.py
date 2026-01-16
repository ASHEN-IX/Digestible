# Backend Unit Tests
from unittest.mock import MagicMock, patch

import pytest

from backend.tts import generate_article_audio, get_tts_service


class TestTTSService:
    """Unit tests for TTS service functions"""

    def test_get_tts_service_singleton(self):
        """Test TTS service singleton pattern"""
        with patch('backend.tts.TTSService') as mock_service_class:
            mock_instance = MagicMock()
            mock_service_class.return_value = mock_instance

            # First call
            service1 = get_tts_service()
            # Second call
            service2 = get_tts_service()

            # Should be the same instance
            assert service1 is service2
            assert service1 is mock_instance

            # TTSService should only be instantiated once
            mock_service_class.assert_called_once()

    @patch('backend.tts.get_tts_service')
    @patch('backend.tts.Path')
    def test_generate_article_audio_success(self, mock_path, mock_get_service):
        """Test article audio generation"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.generate_audio.return_value = "/path/to/audio.wav"

        mock_audio_dir = MagicMock()
        mock_path.return_value = mock_audio_dir
        mock_audio_dir.__truediv__ = MagicMock(return_value="/audio/article_article123.wav")
        mock_audio_dir.mkdir = MagicMock()

        result = generate_article_audio("article123", "Test summary")

        assert result == "/path/to/audio.wav"
        mock_service.generate_audio.assert_called_once_with("Test summary", "/audio/article_article123.wav")
        mock_audio_dir.mkdir.assert_called_once_with(exist_ok=True)

    @patch('backend.tts.get_tts_service')
    def test_generate_article_audio_failure(self, mock_get_service):
        """Test article audio generation handles exceptions"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.generate_audio.side_effect = Exception("Audio generation failed")

        with pytest.raises(Exception, match="Audio generation failed"):
            generate_article_audio("article123", "Test summary")