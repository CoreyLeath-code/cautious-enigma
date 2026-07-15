.PHONY: install quality test benchmark run docker-build docker-run

install:
	python -m pip install -r requirements-dev.txt

quality:
	ruff check app benchmarks tests *.py
	bandit -q -r app benchmarks
	pip-audit -r Requirements.txt

test:
	pytest

benchmark:
	python benchmarks/run_benchmark.py --output artifacts/benchmark.json

run:
	uvicorn app.api:app --host 127.0.0.1 --port 8000

docker-build:
	docker build --tag cautious-enigma:local .

docker-run:
	docker run --rm --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges -p 127.0.0.1:8000:8000 cautious-enigma:local
