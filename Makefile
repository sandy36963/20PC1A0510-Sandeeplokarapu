PY:=python3
VENV?=.venv

.PHONY: venv install run-observe run-summarize run-workflow lint

venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	@. $(VENV)/bin/activate; pip install --upgrade pip

install: venv
	@. $(VENV)/bin/activate; pip install -r requirements.txt

run-observe:
	@. $(VENV)/bin/activate; $(PY) -m app.orchestrator observe --seconds 30 --fps 1 --audio-chunk 15

run-summarize:
	@. $(VENV)/bin/activate; $(PY) -m app.orchestrator summarize

run-workflow:
	@. $(VENV)/bin/activate; $(PY) -m app.orchestrator run data/workflows/example.json
