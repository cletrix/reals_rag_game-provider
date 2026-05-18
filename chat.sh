#!/bin/bash
set -e
cd "$(dirname "$0")"

docker compose up -d qdrant
docker compose run --rm -it rag
