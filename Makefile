.PHONY: setup
setup:
	pyenv exec python -m venv venv && . venv/bin/activate && pip install --upgrade pip && python -m pip install pip-tools

.PHONY: update
update:
	. venv/bin/activate && pip-compile --generate-hashes requirements.in

.PHONY: install
install:
	. venv/bin/activate && pip-sync
	. venv/bin/activate && pre-commit install && pre-commit autoupdate

.PHONY: lint
lint:
	. venv/bin/activate && black app.py
	. venv/bin/activate && isort .
