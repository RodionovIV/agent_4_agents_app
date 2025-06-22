DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker-compose.yml
APP_CONTAINER = gradio_container

.PHONY: up
up:
	${DC} -f ${APP_FILE} ${ENV} up --build

.PHONY: down
down:
	${DC} -f ${APP_FILE} down

.PHONY: logs
logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: shell
shell:
	${EXEC} ${APP_CONTAINER} bash