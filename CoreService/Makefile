.PHONY: build run rebuild down kafka db app rebapp

# Empty by default, defines specific docker container to work with
CONT ?= 

# Builds container(s)
build:
	poetry export -f requirements.txt --output requirements.txt
	docker compose build $(CONT)
	rm -f requirements.txt

# Runs container(s)
run:
	docker compose up -d $(CONT)

# Delete, build and run container(s)
rebuild:  down build run

down:
	docker compose down $(CONT)

kafka:
	docker compose up -d zookeeper kafka

db:
	docker compose up -d core_db

app:
	docker compose up core

rebapp: down build app
