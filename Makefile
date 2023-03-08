tests: initTestDb coverage dockerDown

initTestDb:
	python3 ./electricity_consumption/init_database.py

coverage:
	coverage run -m pytest
	coverage report -m
	coverage erase

prod:
	docker compose -f './docker-compose-prod.yml' --env-file ./.env_prod up

dockerUp:
	docker compose up

dockerDown:
	docker compose down