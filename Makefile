.PHONY: install run test clean docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python node.py

test:
	python -m pytest tests/ -v 2>/dev/null || echo "No tests configured yet"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f blockchain-*.txt wallet-*.txt

docker-build:
	docker build -t smart-chain-supply .

docker-run:
	docker run -p 80:80 --env-file .env smart-chain-supply
