up:
	docker-compose up -d --build

down:
	docker-compose down -v

fill:
	docker-compose -f docker-compose-fill.yaml up -d
