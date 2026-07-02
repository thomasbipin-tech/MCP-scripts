.PHONY: up down test seed-demo migrate fmt dev-api dev-web

# --- Docker orchestration ---------------------------------------------------

up: ## Build and start the full stack (nginx on :8080)
	docker compose up --build

down: ## Stop and remove the stack
	docker compose down

# --- Backend --------------------------------------------------------------

test: ## Run the backend test suite
	cd backend && python -m pytest -q

seed-demo: ## Regenerate the demo report + source PDFs
	cd backend && python -m app.seeder.export

migrate: ## Apply Alembic migrations
	cd backend && alembic upgrade head

fmt: ## Format the backend with black
	cd backend && black app tests

dev-api: ## Run the API locally (no Docker) with autoreload
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Run the frontend dev server locally (no Docker)
	cd frontend && npm run dev
