SHELL := /bin/bash
PYTHON := python3
MANAGER := manage.py
DB := db.sqlite3

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install requirements
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: migrate
migrate: ## Make and run migrations
	$(PYTHON) $(MANAGER) makemigrations
	$(PYTHON) $(MANAGER) migrate

.PHONY: serve
serve: ## Run the django server
	$(PYTHON) $(MANAGER) runserver

.PHONY: host
host: ## Host localy to access from same netword (make sure to add IP to ALLOWED_HOSTS)
	$(PYTHON) $(MANAGER) runserver 0.0.0.0:8000

.PHONY: start
start: install migrate serve ## Install requirements, apply migrations, then start development server

.PHONY: clean
clean: ## Remove migrations and delete database
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	rm $(DB)

.PHONY:	test
test: ## Tests all the apps
	$(PYTHON) $(MANAGER) test

.PHONY: adduser
adduser: ## Create a new superuser
	$(PYTHON) $(MANAGER) createsuperuser

.PHONY: shell
shell: ## Run django's shell
	$(PYTHON) $(MANAGER) shell

.PHONY: static
static: ## collect static files
	$(PYTHON) $(MANAGER) collectstatic

.PHONY: preprod
preprod: test static ## Prepare and check production
	$(PYTHON) $(MANAGER) check --deploy
