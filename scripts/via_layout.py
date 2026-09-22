#!/usr/bin/env python3
"""Turn the VIA definition's KLE layout into a QMK-style info.json for keymap-drawer.

    via_layout.py <via-definition.json> <via-backup.json> > keymap-drawer/neo_ergo.json

VIA layouts contain every layout option (split backspace, split shift, ...). The option
actually in use is picked by checking which variant has keys mapped in the backup.
"""

import json
import sys
from collections import defaultdict

definition_path, backup_path = sys.argv[1:3]
with open(definition_path) as f:
    definition = json.load(f)
with open(backup_path) as f:
    base_layer = json.load(f)["layers"][0]

cols = definition["matrix"]["cols"]


def parse_kle(rows):
    """Minimal KLE parser: yields keys with absolute position, size and rotation."""
    x = y = r = rx = ry = 0.0
    w = h = 1.0
    for row in rows:
        for item in row:
            if isinstance(item, dict):
                if "r" in item:
                    r = item["r"]
                if "rx" in item:
                    rx = item["rx"]
                    x, y = rx, ry
                if "ry" in item:
                    ry = item["ry"]
                    x, y = rx, ry
                x += item.get("x", 0)
                y += item.get("y", 0)
                w, h = item.get("w", w), item.get("h", h)
                continue
            labels = item.split("\n")
            row_, col = map(int, labels[0].split(","))
            option = tuple(map(int, labels[3].split(","))) if len(labels) > 3 and labels[3] else None
            yield {"matrix": [row_, col], "x": x, "y": y, "w": w, "h": h, "r": r, "rx": rx, "ry": ry, "option": option}
            x += w
            w = h = 1.0
        y += 1
        x = rx


keys = list(parse_kle(definition["layouts"]["keymap"]))

# Group option keys: group -> choice -> keys
options = defaultdict(lambda: defaultdict(list))
for key in keys:
    if key["option"]:
        group, choice = key["option"]
        options[group][choice].append(key)


def mapped(key):
    row, col = key["matrix"]
    return base_layer[row * cols + col] not in ("KC_NO", "")


selected = []
for group, choices in sorted(options.items()):
    choice = max(sorted(choices), key=lambda c: sum(map(mapped, choices[c])))
    chosen = choices[choice]
    # VIA draws alternative choices off to the side; move them onto choice 0's position.
    ref = choices[0]
    dx = min(k["x"] for k in ref) - min(k["x"] for k in chosen)
    dy = min(k["y"] for k in ref) - min(k["y"] for k in chosen)
    for key in chosen:
        selected.append({**key, "x": key["x"] + dx, "y": key["y"] + dy})

layout = [k for k in keys if not k["option"]] + selected
layout.sort(key=lambda k: (k["matrix"][0], k["x"]))


def clean(key):
    out = {"matrix": key["matrix"], "x": round(key["x"], 4), "y": round(key["y"], 4)}
    if key["w"] != 1:
        out["w"] = key["w"]
    if key["h"] != 1:
        out["h"] = key["h"]
    if key["r"]:
        out |= {"r": key["r"], "rx": key["rx"], "ry": key["ry"]}
    return out


json.dump(
    {
        "keyboard_name": definition["name"],
        "matrix_size": {"rows": definition["matrix"]["rows"], "cols": cols},
        "layouts": {"LAYOUT": {"layout": [clean(k) for k in layout]}},
    },
    sys.stdout,
    indent=2,
)
print()
