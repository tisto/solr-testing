SHELL := /bin/bash
SOLR_VERSION := 4.5.1

all: bootstrap virtualenv

bootstrap:
	@echo "Bootstrap"
	@if [[ ! -f downloads/solr-$(SOLR_VERSION).tgz  ]]; then \
		wget -P downloads http://archive.apache.org/dist/lucene/solr/$(SOLR_VERSION)/solr-$(SOLR_VERSION).tgz; \
	else \
		echo "Skip downloading Solr."; \
	fi;
	@if [[ ! -d downloads/solr-$(SOLR_VERSION)  ]]; then \
		tar xfvz downloads/solr-$(SOLR_VERSION).tgz -C downloads; \
	else \
		echo "Skip extracting Solr."; \
	fi
	@if [[ ! -d test-solr ]]; then \
		cp -Rv downloads/solr-$(SOLR_VERSION)/example/ test-solr; \
	else \
		echo "Skip creating test-solr."; \
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
