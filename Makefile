SHELL := /bin/bash
export LIQUIBASE_IMAGE := "liquibase/liquibase:4.20"
export POSTGRESQL_USERNAME := "trademark-catalog"
export POSTGRESQL_PASSWORD := "trademark-catalog"
export POSTGRESQL_DSN := "jdbc:postgresql://trademark-db:5432/trademark-catalog"
export IMAGE_NAME := "trademark-catalog:latest"
export NETWORK_NAME := "trademark"
export LOAD_DATA_FROM := $(shell pwd)/trademark_data

migrate:
	docker run -it --rm \
		-v $(shell pwd)/migrations:/liquibase/changelog \
		--network $(NETWORK_NAME) \
		$(LIQUIBASE_IMAGE) \
		--driver=org.postgresql.Driver \
		--url="${POSTGRESQL_DSN}" \
		--changeLogFile=changelog.xml \
		--username="${POSTGRESQL_USERNAME}" \
		--password="${POSTGRESQL_PASSWORD}" \
		update

create-network:
	docker network create -d bridge $(NETWORK_NAME)

build:
	docker build --no-cache -f docker/Dockerfile -t $(IMAGE_NAME) .

start:
	docker-compose up -d

stop:
	docker-compose down

validate:
	poetry run mypy . || true
	poetry run flake8 . || true

safety:
	poetry export | safety --disable-optional-telemetry-data check --disable-audit-and-monitor --stdin
