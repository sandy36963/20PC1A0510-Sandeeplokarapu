import subprocess
import time
from typing import Dict, List, Any

import pyautogui
from mss import mss
from PIL import Image


def open_app(cmd: str) -> None:
    subprocess.Popen(cmd.split())


def wait_for_text(text: str, timeout_sec: int = 10) -> bool:
    """Wait until OCR over the current screen contains the given text.

    Uses mss for screenshots to avoid external screenshot dependencies (e.g., scrot).
    Falls back to pyautogui.screenshot if mss fails for any reason.
    """
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        try:
            with mss() as sct:
                shot = sct.grab(sct.monitors[1])
                img = Image.frombytes("RGB", shot.size, shot.rgb)
        except Exception:
            # Fallback to pyautogui if mss isn't available on this system at runtime
            img = pyautogui.screenshot()

        try:
            import pytesseract

            ocr_text = pytesseract.image_to_string(img)
        except Exception:
            ocr_text = ""

        if text.lower() in ocr_text.lower():
            return True
        time.sleep(0.5)
    return False


def type_text(text: str) -> None:
    pyautogui.typewrite(text, interval=0.02)


def press(key: str) -> None:
    pyautogui.press(key)


def hotkey(keys: List[str]) -> None:
    pyautogui.hotkey(*keys)


ACTIONS = {
    "open_app": open_app,
    "wait_for_text": wait_for_text,
    "type_text": type_text,
    "press": press,
    "hotkey": hotkey,
}


def run_workflow(workflow: Dict[str, Any]) -> None:
    for step in workflow.get("steps", []):
        action = step["action"]
        fn = ACTIONS.get(action)
        if fn is None:
            raise ValueError(f"Unknown action: {action}")
        args = step.get("args", {})
        result = fn(**args)
        if action.startswith("wait_") and not result:
            raise RuntimeError(f"Wait failed: {step}")
        time.sleep(0.3)
