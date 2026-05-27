.PHONY: setup up down logs restart backend frontend db-shell redis-shell seed

## First-time setup: copy env file
setup:
	copy .env.example .env
	@echo "✅  .env created — open it and add your API keys!"

## Start all services (database, cache, backend, frontend)
up:
	docker compose up --build -d
	@echo "✅  All services started!"
	@echo "   🌐  Dashboard → http://localhost:3000"
	@echo "   🔧  API Docs  → http://localhost:8000/docs"

## Stop all services
down:
	docker compose down

## Stop and remove all data (fresh start)
clean:
	docker compose down -v --remove-orphans

## Stream logs from all services
logs:
	docker compose logs -f

## Stream logs from backend only
logs-backend:
	docker compose logs -f backend

## Restart just the backend (useful after code changes)
restart-backend:
	docker compose restart backend

## Open a PostgreSQL shell
db-shell:
	docker compose exec postgres psql -U postgres -d content_agent

## Open a Redis shell
redis-shell:
	docker compose exec redis redis-cli

## Seed the database with demo data
seed:
	docker compose exec backend python -m app.scripts.seed

## Run backend tests
test:
	docker compose exec backend pytest -v

## Show status of all containers
status:
	docker compose ps
