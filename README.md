## Local AI Dashcam MVP (Observe → Understand → Act)

This repo contains a minimal end-to-end scaffold for a privacy-first desktop assistant that:

- Captures screenshots, microphone audio, and input events locally
- Transcribes audio offline (Whisper via faster-whisper)
- OCRs screenshots (Tesseract)
- Summarizes recent activity using a local LLM via Ollama
- Detects simple repeated patterns
- Replays a learned workflow using desktop automation

Everything runs locally. No cloud calls required.

### Prerequisites (Linux)
- Python 3.10+
- FFmpeg (optional), Tesseract OCR
- Ollama (for local LLM). Install from `https://ollama.com/download` and pull a small model, e.g. `ollama pull llama3.2:3b`.

Install OS packages (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y ffmpeg tesseract-ocr libtesseract-dev python3-venv
```

### Setup
```bash
./setup.sh
# or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Ollama separately:
```bash
ollama pull llama3.2:3b
```

### Project layout
```
app/
  recorder/          # screenshot, audio, event logging
  processing/        # OCR, STT, summarize, patterns
  automation/        # workflow executor
  orchestrator.py    # CLI entrypoint
data/
  raw/               # captured artifacts
  processed/         # summaries, patterns
  workflows/         # workflow JSON files
```

### Quickstart (CLI)
1) Observe for 30s (screenshots 1 fps, audio chunks 15s):
```bash
source .venv/bin/activate
python -m app.orchestrator observe --seconds 30 --fps 1 --audio-chunk 15
```

2) Summarize artifacts (requires Ollama running):
```bash
python -m app.orchestrator summarize
# Outputs:
# - data/processed/summary.txt
# - data/processed/patterns.json
```

3) Run an example workflow (edit `data/workflows/example.json` for your system):
```bash
python -m app.orchestrator run data/workflows/example.json
```

Make targets:
```bash
make install
make run-observe
make run-summarize
make run-workflow
```

### Notes
- Desktop automation uses PyAutoGUI; ensure the target window is visible and focused.
- OCR relies on Tesseract; UI high contrast improves accuracy.
- STT uses faster-whisper `base.en` by default for speed.
- Storage lives under `data/`. Raw artifacts can be pruned safely.

### Disclaimer
Automation will move your mouse and type. Save your work and test on a safe desktop session.