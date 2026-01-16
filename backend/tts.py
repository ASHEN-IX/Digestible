"""
Text-to-Speech functionality using Google TTS
"""

import tempfile
from pathlib import Path

from gtts import gTTS


class TTSService:
    """Text-to-Speech service using Google TTS"""

    def __init__(self):
        # Google TTS doesn't need initialization
        pass

    def generate_audio(self, text: str, output_path: str = None) -> str:
        """
        Generate audio from text using Google TTS

        Args:
            text: Text to convert to speech
            output_path: Optional output path, defaults to temp file

        Returns:
            Path to generated audio file
        """
        if output_path is None:
            # Create temp file
            temp_dir = Path(tempfile.gettempdir()) / "digestible_audio"
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"tts_{hash(text)}.mp3"

        try:
            # Generate speech using Google TTS
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(str(output_path))

            return str(output_path)

        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            raise


# Global TTS service instance
_tts_service = None


def get_tts_service() -> TTSService:
    """Get or create TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


def generate_article_audio(article_id: str, summary_text: str) -> str:
    """
    Generate audio for article summary

    Args:
        article_id: Article ID for filename
        summary_text: Summary text to convert to speech

    Returns:
        Path to generated audio file
    """
    try:
        tts = get_tts_service()

        # Create output path
        audio_dir = Path("audio")
        audio_dir.mkdir(exist_ok=True)
        output_path = audio_dir / f"article_{article_id}.wav"

        # Generate audio
        audio_path = tts.generate_audio(summary_text, output_path)

        print(f"✅ Generated audio for article {article_id}: {audio_path}")
        return audio_path

    except Exception as e:
        print(f"❌ Failed to generate audio for article {article_id}: {e}")
        raise
