import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import sounddevice as sd
import soundfile as sf


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


@dataclass
class AudioCaptureConfig:
    output_dir: str
    chunk_seconds: int = 15
    samplerate: int = 16000
    channels: int = 1
    prefix: str = "mic"


def record_audio_chunks(config: AudioCaptureConfig, total_seconds: Optional[int] = None) -> None:
    """
    Record microphone audio in fixed-size chunks. Stops after total_seconds if provided.
    """
    os.makedirs(config.output_dir, exist_ok=True)
    remaining = total_seconds
    try:
        while True:
            if remaining is not None and remaining <= 0:
                break
            ts = utc_ts()
            path = os.path.join(config.output_dir, f"{config.prefix}_{ts}.wav")
            duration = config.chunk_seconds if remaining is None else min(config.chunk_seconds, remaining)
            frames = int(duration * config.samplerate)
            audio = sd.rec(frames, samplerate=config.samplerate, channels=config.channels, dtype="float32")
            sd.wait()
            sf.write(path, audio, config.samplerate)
            if remaining is not None:
                remaining -= duration
            time.sleep(0.05)
    except Exception as e:
        # Log and continue (e.g., no audio device available)
        print(f"[audio] recording error: {e}")
