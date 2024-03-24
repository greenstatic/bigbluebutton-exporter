DOCS_BUILD_DIR=./html

.PHONY: docker
docker:
	bash build-docker.sh

.PHONY: docs
docs:
	mkdocs build -d $(DOCS_BUILD_DIR)

.PHONY: docs-dev
docs-dev:
	mkdocs serve -a 0.0.0.0:8000 --no-strict
