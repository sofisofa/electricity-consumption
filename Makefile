tests: dockerup coverage dockerdown

coverage:
	coverage run -m pytest
	coverage report -m
	coverage erase

#prod:
#	docker compose -f './docker-compose-prod.yml' up

dockerup:
	docker compose up
dockerdown:
	docker compose down