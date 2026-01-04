.PHONY: run down up rebuild ps logs test-backend test-backend-docker

run:
	docker compose down
	docker compose up --build -d

up:
	docker compose up --build -d

down:
	docker compose down

rebuild:
	docker compose build

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=200

# Local backend tests (requires Poetry installed)
test-backend:
	cd backend && poetry install && poetry run pytest -q

# Backend tests inside container (uses pip-installed deps from Dockerfile)
test-backend-docker:
	docker compose run --rm backend pytest -q
