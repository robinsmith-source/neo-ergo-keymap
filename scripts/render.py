#!/usr/bin/env python3
"""Render the VIA backup into build/keymap.svg with keymap-drawer.

    uv run scripts/render.py

VIA stores each layer as a flat list in matrix order (row * cols + col). QMK keymap.json
expects keys in the order of the LAYOUT macro, so we reorder via the physical layout before
handing it to keymap-drawer.
"""

import json
from pathlib import Path
from typing import Any

import yaml
from keymap_drawer.config import Config
from keymap_drawer.draw import KeymapDrawer
from keymap_drawer.parse import QmkJsonParser

ROOT = Path(__file__).resolve().parent.parent
VIA_BACKUP = ROOT / "via/neo_ergo.layout.json"
INFO_JSON = ROOT / "keymap-drawer/neo_ergo.json"
CONFIG = ROOT / "keymap-drawer/config.yaml"
BUILD = ROOT / "build"
LAYERS = ["Base", "Fn", "Mac", "Nav"]  # names for VIA layers 0..3


def via_to_qmk(via: dict[str, Any], info: dict[str, Any]) -> dict[str, Any]:
    layout_name, layout = next(iter(info["layouts"].items()))
    cols = info["matrix_size"]["cols"]
    layers = [
        [layer[row * cols + col] for row, col in (key["matrix"] for key in layout["layout"])]
        for layer in via["layers"]
    ]
    return {"keyboard": "neo_ergo", "layout": layout_name, "layers": layers}


def main() -> None:
    config = Config.model_validate(yaml.safe_load(CONFIG.read_text()))
    BUILD.mkdir(exist_ok=True)

    qmk_path = BUILD / "keymap.json"
    qmk = via_to_qmk(json.loads(VIA_BACKUP.read_text()), json.loads(INFO_JSON.read_text()))
    qmk_path.write_text(json.dumps(qmk, indent=2) + "\n")
    with qmk_path.open() as f:
        keymap = QmkJsonParser(config.parse_config, None, layer_names=LAYERS).parse(f)

    svg_path = BUILD / "keymap.svg"
    with svg_path.open("w") as f:
        KeymapDrawer(
            config=config,
            out=f,
            layers=keymap["layers"],
            layout={"qmk_info_json": INFO_JSON, "layout_name": qmk["layout"]},
            combos=keymap.get("combos", []),
        ).print_board()
    print(f"rendered {svg_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
