# This makefile wraps around django commands
# for faster integrations

# See 'make help' for a list of useful targets

# ==================================================
# Constants
# ===================================================

SHELL := /bin/bash
PYTHON := python3 -Wa
PIP := pip3
MANAGER := manage.py
DB := db.sqlite3

PRECOMMIT = pre-commit
MYPY = mypy

DJANGO_PROJECT = interludes
COVERAGE_OMIT = --omit=**/__init__.py,**/migrations/*,manage.py,$(DJANGO_PROJECT)/asgi.py,$(DJANGO_PROJECT)/wsgi.py

# set to ON/OFF to toggle ANSI escape sequences
COLOR := ON

HELP_PADDING := 15

# Uncomment to show commands
# VERBOSE = TRUE

# ==================================================
# Make code and variable setting
# ==================================================

ifeq ($(COLOR),ON)
	color_yellow = \033[93;1m
	color_orange = \033[33m
	color_red    = \033[31m
	color_green  = \033[32m
	color_blue   = \033[34;1m
	color_reset  = \033[0m
endif

define print
	@echo -e "$(color_yellow)$(1)$(color_reset)"
endef

# =================================================
# Default target
# =================================================

default: serve
.PHONY: default

# =================================================
# Special Targets
# =================================================

# No display of executed commands
# Unless VERBOSE is set
$(VERBOSE).SILENT:

.PHONY: help
help: ## Show this help
	@echo -e "$(color_yellow)make:$(color_reset) list of useful targets:"
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(color_blue)%-$(HELP_PADDING)s$(color_reset) %s\n", $$1, $$2}'

.PHONY: migrate
migrate: ## Make and run migrations
	$(call print,Migrating database)
	$(PYTHON) $(MANAGER) makemigrations
	$(PYTHON) $(MANAGER) migrate

.PHONY: serve
serve: ## Run the django server (blocking)
	$(call print,Running server (accessible from http://localhost:8000))
	$(PYTHON) $(MANAGER) runserver

.PHONY: host
host: ## Host locally to access from same network (make sure to add IP to ALLOWED_HOSTS)
	$(call print,Hosting server locally (accessible from http://localhost:8000))
	$(PYTHON) $(MANAGER) runserver 0.0.0.0:8000

.PHONY: clean
clean: ## Delete database
	$(call print,Removing database)
	rm -f $(DB)

.PHONY: clean-all
clean-all: clean ## Delete database and migration files
	$(call print,Removing migration files)
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -delete
	find . -path "*/migrations/*.pyc" -not -path "*/venv/*" -delete

.PHONY: adduser
adduser: ## Create a new superuser
	$(call print,Creating a new superuser)
	$(PYTHON) $(MANAGER) createsuperuser

.PHONY: shell
shell: ## Run django's shell
	$(call print,Starting django's shell)
	$(PYTHON) $(MANAGER) shell

# =================================================
# Tests and checks
# =================================================

.PHONY: precommit
precommit: ## run precommit
	$(call print,Running precommit)
	$(PRECOMMIT) run

.PHONY: precommit-all
precommit-all: ## run precommit on all files
	$(call print,Running precommit on all files)
	$(PRECOMMIT) run --all-files

.PHONY: static
static: compressed ## collect static files
	$(call print,Collecting static files)
	$(PYTHON) $(MANAGER) collectstatic

.PHONY: test
test: ## Tests all the apps with django's tests
	$(call print,Running django tests)
	$(PYTHON) -m coverage run --source='.' $(MANAGER) test --noinput
	$(call print,Coverage report)
	rm -rf htmlcov
	coverage report $(COVERAGE_OMIT)
	coverage html $(COVERAGE_OMIT)

.PHONY: preprod
preprod: test static ## Prepare and check production
	$(PYTHON) $(MANAGER) check --deploy

.PHONY: mypy
mypy: $(SETTINGS) ## Typecheck all python files
	$(call print,Typechecking python with mypy)
	$(MYPY) . --exclude /migrations/

.PHONY: format
format: ## Format files with black and isort
	$(call print,Running ruff format)
	ruff format --exclude migrations
	$(call print,Running ruff check and fix)
	ruff check --exclude migrations --fix

.PHONY: format-check
format-check: ## Check that all files are formatted and lint
	$(call print,Running ruff format)
	ruff format --exclude migrations --check
	$(call print,Running ruff check)
	ruff check --exclude migrations

# =================================================
# Installation
# =================================================

.PHONY: install
install:
	$(call print,Installing dependencies)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: setup
setup: install migrate ## Install dependencies and make migrations

.PHONY: start
start: setup serve ## Install requirements, apply migrations, then start development server
