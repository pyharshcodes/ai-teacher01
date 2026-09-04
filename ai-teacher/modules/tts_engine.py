"""
tts_engine.py
--------------
Converts lesson text into spoken audio.

Default:  gTTS (Google Text-to-Speech) - free, no API key, decent quality,
          supports Hindi/English/many Indian + international languages.
Upgrade:  set ELEVENLABS_API_KEY in .env for much more natural voice.
"""

import os
import uuid
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # default demo voice

# Maps friendly language names -> gTTS language codes.
LANGUAGE_CODES = {
    "english": "en",
    "hindi": "hi",
    "hinglish": "hi",  # gTTS has no hinglish code; hi is the closest
    "tamil": "ta",
    "telugu": "te",
    "marathi": "mr",
    "bengali": "bn",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    "urdu": "ur",
    "spanish": "es",
    "french": "fr",
}


def synthesize(text: str, language: str, out_dir: str) -> str:
    """Generates an mp3 file for `text` and returns its path."""
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp3"
    out_path = os.path.join(out_dir, filename)

    if ELEVENLABS_API_KEY:
        try:
            return _synthesize_elevenlabs(text, out_path)
        except Exception:
            pass  # fall through to free gTTS

    lang_code = LANGUAGE_CODES.get(language.strip().lower(), "en")
    tts = gTTS(text=text, lang=lang_code)
    tts.save(out_path)
    return out_path


def _synthesize_elevenlabs(text: str, out_path: str) -> str:
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return out_path
