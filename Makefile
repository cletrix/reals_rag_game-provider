.PHONY: build rebuild index chat web web-bg psql reset

build:
	ollama pull $$(grep EMBED_MODEL .env | cut -d= -f2)
	ollama pull $$(grep LLM_MODEL   .env | cut -d= -f2)
	docker compose up -d qdrant
	docker compose build rag
	docker compose run --rm rag python ingest.py

rebuild:
	docker compose build rag
	docker compose build web

index:
	docker compose up -d qdrant
	docker compose run --rm rag python ingest.py

chat:
	docker compose up -d qdrant
	docker compose run --rm -it rag

web:
	docker compose up -d qdrant postgres
	docker compose up web

web-bg:
	docker compose up -d qdrant postgres web
	@echo "UI disponível em http://localhost:2468"

psql:
	docker compose exec postgres psql -U rag -d ragdb

reset:
	docker compose down
	rm -rf qdrant_data/* data/indexed.json
