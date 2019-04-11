export PG_USERNAME=waldo
export PG_PASSWORD=1234
export PG_DATABASE=waldo
export PG_CONNECTION_URI=postgres://$(PG_USERNAME):$(PG_PASSWORD)@postgres/$(PG_DATABASE)

export AMQP_USERNAME=rabbitmq
export AMQP_PASSWORD=1234
export AMQP_URI=amqp://$(AMQP_USERNAME):$(AMQP_PASSWORD)@rabbitmq:5672/%2f

start:
	docker-compose up --build

db-schema:
	docker exec -i postgres psql $(PG_CONNECTION_URI) -t < scripts/db-schema.sql

psql:
	docker exec -it postgres psql $(PG_CONNECTION_URI)

list_pending:
	docker exec -i waldo-app python /app/src/list_pending.py

process:
	docker exec -i waldo-app python /app/src/process_all.py

show_data:
	docker exec -i postgres psql $(PG_CONNECTION_URI) -c "select * from photos;"
	docker exec -i postgres psql $(PG_CONNECTION_URI) -c "select * from photos_thumbnails;"
	docker exec -i waldo-app ls -l /waldo-app-thumbs
