#!/usr/bin/env python3
"""Convert a VIA layout backup into a QMK keymap.json that keymap-drawer can parse.

VIA stores each layer as a flat list in matrix order (row * cols + col). QMK keymap.json
expects keys in the order of the LAYOUT macro, so we reorder via the physical layout.
"""

import json
import sys

via_path, info_path, out_path = sys.argv[1:4]

with open(via_path) as f:
    via = json.load(f)
with open(info_path) as f:
    info = json.load(f)

layout_name, layout = next(iter(info["layouts"].items()))
cols = info["matrix_size"]["cols"]

layers = [
    [layer[row * cols + col] for row, col in (key["matrix"] for key in layout["layout"])]
    for layer in via["layers"]
]

with open(out_path, "w") as f:
    json.dump({"keyboard": "neo_ergo", "layout": layout_name, "layers": layers}, f, indent=2)
    f.write("\n")
