SHELL := /bin/bash
SOLR_VERSION = 4.5.1

all: bootstrap virtualenv

bootstrap:
	@echo "Bootstrap"
	@if [[ ! -f solr-4.5.1.tgz  ]]; then \
		wget http://archive.apache.org/dist/lucene/solr/4.5.1/solr-4.5.1.tgz; \
	else \
		echo "Skip downloading Solr."; \
	fi;
	@if [[ ! -d solr-4.5.1  ]]; then \
		tar xfvz solr-4.5.1.tgz; \
	else \
		echo "Skip extracting Solr."; \
	fi

virtualenv:
	@echo "Create Virtual Python Environment"
	@if [[ ! -d .env ]]; then \
		virtualenv .env; \
		source .env/bin/activate; \
		pip install -r requirements.txt; \
	else \
		echo "Skip creating virtualenv."; \
	fi


test:
	@echo "Run Tests"
	py.test
