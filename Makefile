tests: _testUp _sleep2 _initTestDb _coverage _testDown

initDb: prodUp _sleep2 initProdDb prodDown

updateDb: prodUp _sleep2 run

initProdDb:
	ENV_FILE_PATH='/.env.prod' poetry run python ./src/electricity_consumption/init_database.py

run:
	ENV_FILE_PATH='/.env.prod' poetry run python ./src/electricity_consumption/update_database.py

prodUp:
	docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod up -d

prodDown:
	docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod down

buildProdGrafana:
	  docker compose -f './docker-compose-prod.yml' --env-file ./.env.prod build

_testUp:
	docker compose  up -d

_testDown:
	docker compose down

_initTestDb:
	poetry run python ./src/electricity_consumption/init_database.py

_coverage:
	coverage run -m pytest
	coverage report -m
	coverage erase

_sleep2:
	sleep 2