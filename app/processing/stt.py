from typing import Dict
from faster_whisper import WhisperModel

_model = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        # base.en is small and fast; change as needed
        _model = WhisperModel("base.en", compute_type="int8")
    return _model


def transcribe(audio_path: str) -> Dict:
    model = _get_model()
    segments, info = model.transcribe(audio_path)
    text = " ".join([seg.text.strip() for seg in segments])
    return {"path": audio_path, "language": info.language, "text": text}
