#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright Chromium quietly (optional)
python - <<'PY'
try:
    import playwright  # noqa: F401
    from playwright.__main__ import main as pw_main
    pw_main(["install", "chromium"])  # installs browser
except Exception as e:
    print("[setup] Playwright install skipped or failed:", e)
PY

echo "Setup complete. Activate with: source .venv/bin/activate"
