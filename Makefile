.PHONY: black lint isort run-local stop-local

black:
	python -m black .

lint:
	pylint -E -d C0301 src/waterbowl-api tests

isort:
	isort **/*.py

run-local:
	docker compose up -d

stop-local:
	docker compose down

