up:
	docker-compose up -d --build

downv:
	docker-compose down -v
	docker-compose -f docker-compose-fill.yaml down -v

down:
	docker-compose down
	docker-compose -f docker-compose-fill.yaml down

fill:
	docker-compose -f docker-compose-fill.yaml up -d

test:
	docker-compose -f tests/docker-compose.yaml up --abort-on-container-exit --exit-code-from tests --attach tests
