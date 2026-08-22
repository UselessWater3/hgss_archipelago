# Makefile
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

.PHONY: default patches

Q ?= @

ROM_SOURCES := roms/hg_us.nds roms/ss_us.nds roms/hg_us.xMAP roms/ss_us.xMAP rom_gen.py
SOURCES := __init__.py \
	client.py \
	items.py \
	locations.py \
	options.py \
	regions.py \
	rules.py \
	species.py \
	rom/__init__.py \
	rom/encounterdata.py \
	rom/eventdata.py \
	rom/itemdata.py \
	rom/movedata.py \
	rom/speciesdata.py \
	rom/trainerdata.py \
	.apignore \
	LICENSE
DATA := data_gen/encounters.toml \
       data_gen/event_checks.toml \
       data_gen/items.toml \
       data_gen/locations.toml \
       data_gen/moves.toml \
       data_gen/regions.toml \
       data_gen/misc_data.toml \
       data_gen/rules.toml \
       data_gen/species.toml \
       data_gen/trainers.toml \
       data_gen/rom_info.toml \
       data_gen_templates/__init__.py \
       data_gen_templates/charmap.py \
       data_gen_templates/encounters.py \
       data_gen_templates/event_checks.py \
       data_gen_templates/items.py \
       data_gen_templates/locations.py \
       data_gen_templates/moves.py \
       data_gen_templates/regions.py \
       data_gen_templates/rules.py \
       data_gen_templates/species.py \
       data_gen_templates/trainers.py \
       data_gen.py \
       data_gen_rules.py

PATCHES := $(ROMS:%=patches/base_patch_%.bsdiff4)

APNDS_VERSION := $(shell cat apnds_version.txt)

default: pokemon_hgss.apworld

data_gen/rom_info.toml: $(ROM_SOURCES)
	@echo ROM GEN
	$Qpython rom_gen.py

data/__init__.py: $(DATA)
	@echo DATA GEN
	$Qpython data_gen.py

apnds/__init__.py: apnds_version.txt
	@echo UDPATE APNDS
	$Qcurl -LSso apnds.tar.gz "https://github.com/ljtpetersen/apnds/releases/download/v$(APNDS_VERSION)/apnds-$(APNDS_VERSION).tar.gz"
	$Qrm -r apnds >/dev/null 2>&1 || true
	$Qtar xzf apnds.tar.gz apnds-$(APNDS_VERSION)/apnds apnds-$(APNDS_VERSION)/LICENSE
	$Qmv apnds-$(APNDS_VERSION)/LICENSE apnds-$(APNDS_VERSION)/apnds
	$Qmv apnds-$(APNDS_VERSION)/apnds apnds
	$Qrm -r apnds.tar.gz apnds-$(APNDS_VERSION)
	$Qtouch apnds/__init__.py

patches: $(PATCHES)
	@:

pokemon_hgss.apworld: data/__init__.py apnds/__init__.py $(SOURCES) $(PATCHES)
	@echo MAKE APWORLD
	$Qcd ../..; python Launcher.py "Build APWorlds" "Pokemon HeartGold and SoulSilver" >/dev/null 2>&1
	$Qcp ../../build/apworlds/pokemon_hgss.apworld .

