.PHONY: build rebuild index chat web web-bg run psql reset deploy deploy-full test test-cov test-docker test-auth create-user backup-db restore-db fix-postgres

build:
	ollama pull $$(grep EMBED_MODEL .env | cut -d= -f2)
	ollama pull $$(grep LLM_MODEL   .env | cut -d= -f2)
	docker compose up -d qdrant
	docker compose build rag
	docker compose run rag python ingest.py

rebuild:
	docker compose build rag
	docker compose build web

index:
	docker compose up -d qdrant
	docker compose run rag python ingest.py

chat:
	docker compose up -d qdrant
	docker compose run -it rag

web:
	docker compose up -d qdrant postgres
	docker compose up web

web-bg:
	docker compose up -d qdrant postgres web
	@echo "UI disponível em http://localhost:2468"

run:
	$(MAKE) test-auth
	docker compose up -d
	@echo "Sistema iniciado! Acesse http://localhost:2468"

psql:
	docker compose exec postgres psql -U rag -d ragdb

reset:
	docker compose down
	rm -rf qdrant_data/* data/indexed.json

deploy:
	./deploy.sh

deploy-full:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "Deploy completo! Acesse http://localhost:2468"

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=web --cov-report=html --cov-report=term

test-docker:
	docker compose build web
	docker compose run web pytest /app/tests/ -v

test-auth:
	docker compose build web
	docker compose run web pytest /app/tests/test_auth.py -v


create-user:
	@echo "Uso: make create-user EMAIL=... PASSWORD=... NAME=... DEPARTMENT=... [ROLE=...]"
	@echo "Exemplo: make create-user EMAIL=user@example.com PASSWORD=senha123 NAME="João Silva" DEPARTMENT=TI ROLE=admin"
	@if [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ] || [ -z "$(NAME)" ] || [ -z "$(DEPARTMENT)" ]; then echo "❌ Erro: EMAIL, PASSWORD, NAME e DEPARTMENT são obrigatórios"; exit 1; fi
	docker compose run web python /app/scripts/create_user.py "$(EMAIL)" "$(PASSWORD)" "$(NAME)" "$(DEPARTMENT)" "$(ROLE)"

fix-postgres:
	docker compose stop postgres
	docker compose run --user postgres postgres pg_resetwal -f /var/lib/postgresql/data
	docker compose up -d postgres
	@echo "PostgreSQL recuperado com sucesso"
backup-db:
	./scripts/backup-postgres.sh

restore-db:
	./scripts/restore-postgres.sh
