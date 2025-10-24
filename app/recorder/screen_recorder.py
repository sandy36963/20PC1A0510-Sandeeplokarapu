import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from mss import mss
from PIL import Image


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


@dataclass
class ScreenCaptureConfig:
    output_dir: str
    interval_seconds: float = 1.0
    image_quality: int = 85  # JPEG quality
    prefix: str = "screen"


def capture_screenshots(config: ScreenCaptureConfig, duration_seconds: Optional[int] = None) -> None:
    """
    Capture full-screen screenshots at a fixed interval. Stops after duration_seconds if provided.
    """
    os.makedirs(config.output_dir, exist_ok=True)
    end_time = time.time() + duration_seconds if duration_seconds else None

    with mss() as sct:
        while True:
            if end_time and time.time() >= end_time:
                break
            ts = utc_ts()
            shot = sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", shot.size, shot.rgb)
            out_path = os.path.join(config.output_dir, f"{config.prefix}_{ts}.jpg")
            img.save(out_path, quality=config.image_quality)
            time.sleep(max(0.01, config.interval_seconds))
