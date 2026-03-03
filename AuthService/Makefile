.PHONY: build run rebuild down

# Empty by default, defines specific docker container to work with
CONT ?= 

# Builds container(s)
build:
	docker compose build $(CONT)
	rm -f requirements.txt

# Runs container(s)
run:
	docker compose up -d $(CONT)

# Delete, build and run container(s)
rebuild:  down build run

down:
	docker compose down $(CONT)
