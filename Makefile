SHELL := /bin/bash
SOLR_VERSION := 4.5.1
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

all: bootstrap virtualenv

bootstrap:
	@echo "Bootstrap"
	echo $(CURRENT_DIR)
	@if [[ ! -f $(CURRENT_DIR)/downloads/solr-$(SOLR_VERSION).tgz  ]]; then \
		wget -P $(CURRENT_DIR)/downloads http://archive.apache.org/dist/lucene/solr/$(SOLR_VERSION)/solr-$(SOLR_VERSION).tgz; \
	else \
		echo "Skip downloading Solr."; \
	fi;
	@if [[ ! -d $(CURRENT_DIR)/downloads/solr-$(SOLR_VERSION)  ]]; then \
		tar xfvz $(CURRENT_DIR)/downloads/solr-$(SOLR_VERSION).tgz -C $(CURRENT_DIR)/downloads; \
	else \
		echo "Skip extracting Solr."; \
	fi
	@if [[ ! -d $(CURRENT_DIR)/test-solr ]]; then \
		cp -Rv $(CURRENT_DIR)/downloads/solr-$(SOLR_VERSION)/example/ $(CURRENT_DIR)/test-solr; \
	else \
		echo "Skip creating test-solr."; \
	fi

virtualenv:
	@echo "Create Virtual Python Environment"
	@if [[ ! -d $(CURRENT_DIR)/.env ]]; then \
		virtualenv $(CURRENT_DIR)/.env; \
		source $(CURRENT_DIR)/.env/bin/activate; \
		pip install -r requirements.txt; \
	else \
		echo "Skip creating virtualenv."; \
	fi

clean:
	@echo "Clean"
	rm -rf test-solr
test:
	@echo "Run Tests"
	py.test
