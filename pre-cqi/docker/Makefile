BUILD_MODE=-O2
SYNAPSE_ARCHIVE=synapse.tar.gz
SYNAPSE_DIR=synapse

.PHONY: build prereq

build: main

main: *.pas $(SYNAPSE_ARCHIVE) $(SYNAPSE_DIR)
	fpc $(BUILD_MODE) -Fu=./$(SYNAPSE_DIR) $@

prereq: $(SYNAPSE_ARCHIVE)

$(SYNAPSE_ARCHIVE) $(SYNAPSE_DIR):
	curl -L https://github.com/geby/synapse/archive/refs/tags/Migrated.SVN.tar.gz --output $(SYNAPSE_ARCHIVE)
	mkdir -p $(SYNAPSE_DIR)
	tar -xf $(SYNAPSE_ARCHIVE) -C . --transform s/synapse-Migrated.SVN/$(SYNAPSE_DIR)/
