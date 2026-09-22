#!/usr/bin/env bash
# Render the VIA backup into build/keymap.svg with keymap-drawer.
set -euo pipefail

cd "$(dirname "$0")/.."
KEYMAP_DRAWER="keymap-drawer==0.23.0"
LAYERS=(Base Fn Mac Nav) # names for VIA layers 0..3

mkdir -p build
python3 scripts/via2qmk.py via/neo_ergo.layout.json keymap-drawer/neo_ergo.json build/keymap.json
uvx --from "$KEYMAP_DRAWER" keymap -c keymap-drawer/config.yaml \
    parse -q build/keymap.json -l "${LAYERS[@]}" -o build/keymap.yaml
uvx --from "$KEYMAP_DRAWER" keymap -c keymap-drawer/config.yaml \
    draw build/keymap.yaml -j keymap-drawer/neo_ergo.json -o build/keymap.svg
echo "rendered build/keymap.svg"
