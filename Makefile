# Flip 7 — two modes, one command each.
#   make dev   → local development stack (edit .env.dev)
#   make prod  → production stack with HTTPS (edit .env.prod)
# See docs/development.md and docs/hosting.md.

DEV_COMPOSE  := docker-compose.dev.yml
PROD_COMPOSE := docker-compose.prod.yml

.PHONY: dev prod down clean logs prod-logs test

dev: ## Start the development stack (creates .env.dev from the example if missing).
	@test -f .env.dev || cp .env.dev.example .env.dev
	docker compose --env-file .env.dev -f $(DEV_COMPOSE) up --build

prod: ## Start the production stack (requires a filled-in .env.prod).
	@test -f .env.prod || { echo "Create .env.prod first:  cp .env.prod.example .env.prod  then edit it."; exit 1; }
	docker compose --env-file .env.prod -f $(PROD_COMPOSE) up -d --build

down: ## Stop whichever stack is running.
	-docker compose -f $(DEV_COMPOSE) down
	-docker compose -f $(PROD_COMPOSE) down

clean: ## Stop both stacks and delete all data (volumes: database, Caddy certs).
	-docker compose -f $(DEV_COMPOSE) down -v --remove-orphans
	-docker compose -f $(PROD_COMPOSE) down -v --remove-orphans

logs: ## Tail development logs.
	docker compose -f $(DEV_COMPOSE) logs -f

prod-logs: ## Tail production logs.
	docker compose -f $(PROD_COMPOSE) logs -f

test: ## Run the full test suite (backend + frontend unit + e2e).
	./scripts/regression.sh
