SHELL := /bin/bash
export LIQUIBASE_IMAGE := "liquibase/liquibase:4.16.0"
export POSTGRESQL_DSN := "jdbc:postgresql://trademark-db:5432/trademark"

migrate:
	docker run -it --rm \
		-v $(shell pwd)/migrations:/liquibase/changelog \
		--network trdmrk \
		$(LIQUIBASE_IMAGE) \
		--driver=org.postgresql.Driver \
		--url="${POSTGRESQL_DSN}" \
		--changeLogFile=changelog.xml \
		--username=trademark \
		--password=trademark \
		--logLevel=DEBUG \
		update

start:
	docker-compose up -d

stop:
	docker-compose down

validate:
	mypy .; \
	flake8 .
