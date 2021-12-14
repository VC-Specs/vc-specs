rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
SOURCES := $(call rwildcard,./,*.json)

.PHONY: generate

generate: $(SOURCES)
	echo $(SOURCES)
    #python3 tools/convert_jsonschema_to_jsonld.py common/Common.json
	python3 tools/convert_jsonschema_to_jsonld.py --type-map ./type_map.yaml $(SOURCES)
