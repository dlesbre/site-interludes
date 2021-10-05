SHELL := /bin/bash
PYTHON := python3
MANAGER := manage.py
DB := db.sqlite3
SECRET := interludes/secret.py

.PHONY: help
help: ## Show this help
	@echo "make: list of useful targets :"
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install requirements
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: secret
secret: ## Link the secret_example.py to secret.py (only in dev mode)

secret $(SECRET):
	ln -s "$(PWD)/interludes/secret_example.py" interludes/secret.py

.PHONY: migrate
migrate: $(SECRET) ## Make and run migrations
	$(PYTHON) $(MANAGER) makemigrations
	$(PYTHON) $(MANAGER) migrate

.PHONY: serve
serve: $(SECRET) ## Run the django server
	$(PYTHON) $(MANAGER) runserver

.PHONY: host
host: $(SECRET) ## Host localy to access from same netword (make sure to add IP to ALLOWED_HOSTS)
	$(PYTHON) $(MANAGER) runserver 0.0.0.0:8000

.PHONY: start
start: install $(SECRET) migrate serve ## Install requirements, apply migrations, then start development server

.PHONY: clean
clean: ## Remove migrations and delete database
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -delete
	find . -path "*/migrations/*.pyc" -not -path "*/venv/*" -delete
	rm $(DB)

.PHONY:	test
test: $(SECRET) ## Tests all the apps
	$(PYTHON) $(MANAGER) test

.PHONY: adduser
adduser: $(SECRET) ## Create a new superuser
	$(PYTHON) $(MANAGER) createsuperuser

.PHONY: shell
shell: $(SECRET) ## Run django's shell
	$(PYTHON) $(MANAGER) shell

.PHONY: static
static: $(SECRET) ## collect static files
	$(PYTHON) $(MANAGER) collectstatic

.PHONY: preprod
preprod: test static ## Prepare and check production
	$(PYTHON) $(MANAGER) check --deploy
