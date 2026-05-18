.PHONY: build rebuild index chat reset

build:
	ollama pull $$(grep EMBED_MODEL .env | cut -d= -f2)
	ollama pull $$(grep LLM_MODEL   .env | cut -d= -f2)
	docker compose up -d qdrant
	docker compose build rag
	docker compose run --rm rag python ingest.py

rebuild:
	docker compose build rag

index:
	docker compose up -d qdrant
	docker compose run --rm rag python ingest.py

chat:
	docker compose up -d qdrant
	docker compose run --rm -it rag

reset:
	docker compose down
	rm -rf qdrant_data/* data/indexed.json
