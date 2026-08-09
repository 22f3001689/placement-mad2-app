.PHONY: clean db-clean db-reset venv activate format install db-init db-migrate db-seed frontend-install frontend-build redis-up redis-down celery-worker celery-beat backend frontend dev dev-full stop
-include .env

##############################################################################
# Environment variables
##############################################################################
VENV_DIR = venv
PYTHON=${VENV_DIR}/bin/python
SYSTEM_PYTHON = python3.11

##############################################################################
# Development set up
##############################################################################
install: venv activate install-dev frontend-install frontend-build

venv: # Create new venv if not exists
	@echo "Creating new virtual environment $(GREEN_ITALIC)$(VENV_DIR)$(DEFAULT) if not exists..."
	@test -d $(VENV_DIR) || $(SYSTEM_PYTHON) -m venv $(VENV_DIR) --upgrade-deps
	@$(PYTHON) --version
	@echo "Done! You may use $(GREEN_ITALIC)source $(VENV_DIR)/bin/activate$(DEFAULT) to activate it and install packages manually, or use Makefile targets for all project setup routines.\n"

activate: # Show activation command
	@echo "To activate the virtual environment, run:"
	@echo "  $(GREEN_ITALIC)source $(VENV_DIR)/bin/activate$(DEFAULT)"

install-dev: # Install dev dependencies
	@echo "Installing dev dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Done.\n"

frontend-install: # Install frontend dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done.\n"

frontend-build: # Build the Vue frontend into app/static/dist
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Done.\n"

##############################################################################
# Run servers
##############################################################################
backend: # Run the Flask backend dev server on :5000
	@echo "Starting Flask backend on :5000..."
	$(PYTHON) -m flask run

frontend: # Run the Vite frontend dev server on :5173 (proxies /api to :5000)
	@echo "Starting Vite frontend dev server on :5173..."
	cd frontend && npm run dev

dev: # Run backend + frontend dev servers together; Ctrl+C stops both
	@trap 'kill 0' INT TERM; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

dev-full: # Run Redis + Celery worker/beat + backend + frontend together; Ctrl+C stops all
	@$(MAKE) redis-up
	@trap '$(MAKE) redis-down' EXIT; \
	trap 'kill 0' INT TERM; \
	$(MAKE) celery-worker & \
	$(MAKE) celery-beat & \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

stop: # Stop backend/frontend/celery worker/beat processes and Redis
	@echo "Stopping local processes..."
	-pkill -f "flask run"
	-pkill -f "vite"
	-pkill -f "celery -A app.celery_app worker"
	-pkill -f "celery -A app.celery_app beat"
	-$(MAKE) redis-down
	@echo "Done.\n"

##############################################################################
# Development process
##############################################################################
format:
	@echo "Running formatters..."

	@echo "\n1. Run $(GREEN_ITALIC)ruff$(DEFAULT) to format code."
	$(PYTHON) -m ruff check --fix-only --exclude migrations .

	@echo "\n2. Run $(GREEN_ITALIC)black$(DEFAULT) to format code."
	$(PYTHON) -m black --exclude migrations --exclude venv .


##############################################################################
# Database operations
##############################################################################
db-init: # Init the db
	@echo "Running Db init..."
	$(PYTHON) -m flask db init
	@echo "Done.\n"

db-migrate: # Run database migrations
	@echo "Running database migrations..."
	$(PYTHON) -m flask db upgrade
	@echo "Done.\n"

db-seed: # Seed database with sample data
	@echo "Seeding database with sample data..."
	cd $(shell pwd) && PYTHONPATH=. $(PYTHON) data-seeds/seed_data.py
	@echo "Done.\n"

db-clean: # Drop database only (keeps migrations)
	@echo "Dropping database..."
	-rm -f app.db
	@echo "Done. Database removed, migrations preserved.\n"


##############################################################################
# Background jobs (Celery + Redis)
##############################################################################
redis-up: # Start local Redis via Docker
	@echo "Starting Redis..."
	docker compose up -d redis
	@echo "Done.\n"

redis-down: # Stop local Redis
	@echo "Stopping Redis..."
	docker compose down redis
	@echo "Done.\n"

celery-worker: # Run the Celery worker
	$(PYTHON) -m celery -A app.celery_app worker --loglevel=info

celery-beat: # Run the Celery Beat scheduler
	$(PYTHON) -m celery -A app.celery_app beat --loglevel=info


clean: # Clean all working folders
	@echo "Removing working folders..."
	-rm -rf $(VENV_DIR)
	-rm -rf dist
	@echo "Done.\n"


##############################################################################
# Output highlights
##############################################################################
DEFAULT = \033[0m
GREEN_ITALIC = \033[32;3;1m