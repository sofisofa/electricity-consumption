tests: dockerUp _sleep2 initTestDb _coverage dockerDown

initDb: prodUp _sleep2 initProdDb prodDown

updateDb: prodUp _sleep2 run

initTestDb:
	python3 ./src/electricity_consumption/init_database.py

initProdDb:
	ENV_FILE_PATH='/.env.prod' python3 ./src/electricity_consumption/init_database.py

run:
	ENV_FILE_PATH='/.env.prod' python3 ./src/electricity_consumption/update_database.py

_coverage:
	coverage run -m pytest
	coverage report -m
	coverage erase

prodUp:
	docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod up -d

prodDown:
	docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod down

buildProdGrafana:
	  docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod build

dockerUp:
	docker compose  up -d

dockerDown:
	docker compose down

_sleep2:
	sleep 2