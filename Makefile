.PHONY: init install fmt run clean-cache

all: run

init:
	# curl -fsSL https://pyenv.run | bash
	pyenv local 3.12.3
	python -m venv .venv

install:
	.venv/bin/pip install requests pytest pytest-html diskcache black

fmt:
	.venv/bin/black .

run:
	.venv/bin/pytest main.py -v --html=report.html --log-cli-level=INFO

clean-cache:
	rm -rf .cache
