SHELL := /bin/bash
export LIQUIBASE_IMAGE := "liquibase/liquibase:4.16.0"
export POSTGRESQL_DSN := "jdbc:postgresql://trademark-db:5432/trademark"
export POSTGRESQL_DSN_WITH_AUTH := "postgres://trademark:trademark@trademark-db:5432/trademark"
export IMAGE_NAME := "trademark-backend:latest"
export NETWORK_NAME := "trdmrk"

create-network:
	docker network create -d bridge $(NETWORK_NAME)

migrate:
	docker run -it --rm \
		-v $(shell pwd)/migrations:/liquibase/changelog \
		--network $(NETWORK_NAME) \
		$(LIQUIBASE_IMAGE) \
		--driver=org.postgresql.Driver \
		--url="${POSTGRESQL_DSN}" \
		--changeLogFile=changelog.xml \
		--username=trademark \
		--password=trademark \
		--logLevel=DEBUG \
		update

load-data:
	docker run -it --rm \
		-v $(shell pwd)/trademark-data:/data \
		--network $(NETWORK_NAME) \
		$(IMAGE_NAME) \
		populate_db.py /data $(POSTGRESQL_DSN_WITH_AUTH)

build:
	docker build --no-cache -f docker/Dockerfile -t $(IMAGE_NAME) .

start:
	docker-compose up -d

stop:
	docker-compose down

validate:
	@echo " --- Type checker --- "; mypy . || true; \
	echo " --- Linter --- "; flake8 . || true;
