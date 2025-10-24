import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from pynput import mouse, keyboard


def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


@dataclass
class EventLoggerConfig:
    output_path: str  # JSONL file


def log_events(config: EventLoggerConfig, duration_seconds: Optional[int] = None) -> None:
    """
    Log mouse and keyboard events to a JSONL file. Stops after duration_seconds if provided.
    """
    os.makedirs(os.path.dirname(config.output_path) or ".", exist_ok=True)
    stop_flag = threading.Event()

    f = open(config.output_path, "a", buffering=1)

    def write_event(event: dict) -> None:
        event_with_ts = {"ts": utc_ts(), **event}
        f.write(json.dumps(event_with_ts) + "\n")

    def on_click(x, y, button, pressed):
        write_event({"kind": "mouse", "type": "click", "x": x, "y": y, "button": str(button), "pressed": pressed})

    def on_move(x, y):
        write_event({"kind": "mouse", "type": "move", "x": x, "y": y})

    def on_scroll(x, y, dx, dy):
        write_event({"kind": "mouse", "type": "scroll", "x": x, "y": y, "dx": dx, "dy": dy})

    def on_press(key):
        write_event({"kind": "key", "type": "press", "key": str(key)})

    def on_release(key):
        write_event({"kind": "key", "type": "release", "key": str(key)})

    ml = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)
    kl = keyboard.Listener(on_press=on_press, on_release=on_release)
    ml.start(); kl.start()

    try:
        if duration_seconds is None:
            while not stop_flag.is_set():
                time.sleep(0.25)
        else:
            end_time = time.time() + duration_seconds
            while time.time() < end_time:
                time.sleep(0.25)
    finally:
        ml.stop(); kl.stop(); f.flush(); f.close()
