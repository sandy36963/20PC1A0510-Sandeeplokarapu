import argparse
import glob
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import List, Dict

from app.recorder.screen_recorder import ScreenCaptureConfig, capture_screenshots
from app.recorder.audio_recorder import AudioCaptureConfig, record_audio_chunks
from app.recorder.event_logger import EventLoggerConfig, log_events
from app.processing.ocr import ocr_image
from app.processing.stt import transcribe
from app.processing.summarize import llm_summarize
from app.processing.patterns import frequent_ngrams
from app.automation.executor import run_workflow

DATA_RAW_SCREENS = "data/raw/screens"
DATA_RAW_AUDIO = "data/raw/audio"
DATA_PROCESSED = "data/processed"
DATA_EVENTS = os.path.join(DATA_PROCESSED, "events.jsonl")
WORKFLOWS_DIR = "data/workflows"


@dataclass
class ObserveConfig:
    screenshot_fps: float = 1.0
    audio_chunk_seconds: int = 15
    observe_seconds: int = 60


def observe(cfg: ObserveConfig) -> None:
    os.makedirs(DATA_RAW_SCREENS, exist_ok=True)
    os.makedirs(DATA_RAW_AUDIO, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_EVENTS), exist_ok=True)

    th_s = threading.Thread(
        target=capture_screenshots,
        kwargs={
            "config": ScreenCaptureConfig(output_dir=DATA_RAW_SCREENS, interval_seconds=1.0 / cfg.screenshot_fps),
            "duration_seconds": cfg.observe_seconds,
        },
        daemon=True,
    )
    th_a = threading.Thread(
        target=record_audio_chunks,
        kwargs={
            "config": AudioCaptureConfig(output_dir=DATA_RAW_AUDIO, chunk_seconds=cfg.audio_chunk_seconds),
            "total_seconds": cfg.observe_seconds,
        },
        daemon=True,
    )
    th_e = threading.Thread(
        target=log_events,
        kwargs={
            "config": EventLoggerConfig(output_path=DATA_EVENTS),
            "duration_seconds": cfg.observe_seconds,
        },
        daemon=True,
    )

    th_s.start(); th_a.start(); th_e.start()
    th_s.join(); th_a.join(); th_e.join()


def process_and_summarize() -> None:
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    # OCR latest N screenshots
    screen_paths = sorted(glob.glob(os.path.join(DATA_RAW_SCREENS, "*.jpg")))[-20:]
    ocr_results: List[Dict] = [ocr_image(p) for p in screen_paths]

    # STT latest N audio chunks
    audio_paths = sorted(glob.glob(os.path.join(DATA_RAW_AUDIO, "*.wav")))[-10:]
    stt_results: List[Dict] = []
    for p in audio_paths:
        try:
            stt_results.append(transcribe(p))
        except Exception as e:
            print(f"[stt] error on {p}: {e}")

    # Load events
    events: List[Dict] = []
    if os.path.exists(DATA_EVENTS):
        with open(DATA_EVENTS, "r") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass

    # LLM summary
    summary = llm_summarize(events, ocr_results, stt_results)
    with open(os.path.join(DATA_PROCESSED, "summary.txt"), "w") as f:
        f.write(summary)

    # Pattern mining
    event_types = [f"{e.get('kind','')}.{e.get('type','')}" for e in events]
    patterns = frequent_ngrams(event_types, n=5, min_count=2)
    with open(os.path.join(DATA_PROCESSED, "patterns.json"), "w") as f:
        json.dump({"patterns": patterns}, f, indent=2)

    print("Summary written to data/processed/summary.txt")
    print("Patterns written to data/processed/patterns.json")


def run_workflow_file(path: str) -> None:
    with open(path, "r") as f:
        wf = json.load(f)
    run_workflow(wf)


def main():
    parser = argparse.ArgumentParser(description="Local AI Dashcam MVP")
    sub = parser.add_subparsers(dest="cmd")

    p_obs = sub.add_parser("observe", help="Capture screen/audio/events for a period")
    p_obs.add_argument("--seconds", type=int, default=60)
    p_obs.add_argument("--fps", type=float, default=1.0)
    p_obs.add_argument("--audio-chunk", type=int, default=15)

    sub.add_parser("summarize", help="Process artifacts and summarize")

    p_run = sub.add_parser("run", help="Run a workflow JSON")
    p_run.add_argument("path", type=str)

    args = parser.parse_args()

    if args.cmd == "observe":
        observe(ObserveConfig(
            screenshot_fps=args.fps,
            audio_chunk_seconds=args.audio_chunk,
            observe_seconds=args.seconds,
        ))
    elif args.cmd == "summarize":
        process_and_summarize()
    elif args.cmd == "run":
        run_workflow_file(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
