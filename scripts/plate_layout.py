#!/usr/bin/env python3
"""Write the Neo Ergo's physical layout as a QMK-style info.json for keymap-drawer.

    uv run scripts/plate_layout.py > keymap-drawer/neo_ergo.json

The VIA definition's layout is only an approximation of the board (wrong stagger, key sizes and
half offsets), so key positions are measured from an orthographic top-down render of the plate
instead: https://divinikey.com/products/qwertykeys-neo-ergo-plate (first image, 1200x1200).
Switch cutouts there are 57 px apart, i.e. 57 px = 1u = 19.05 mm, with the plate's top-left
corner at (70, 447) px. Each key is centered on its switch cutout.
"""

import json
import math
import sys
from typing import Any

PX_PER_U = 57.0
PLATE_ORIGIN = (70.0, 447.0)
ROTATION = 10  # degrees, left half clockwise, right half counter-clockwise

# matrix -> (cutout center x, y in px, width in u, half rotation sign)
KEYS = {
    # macro column
    (1, 0): (119.5, 478.6, 1, 0),
    (2, 0): (112.4, 535.6, 1, 0),
    (3, 0): (105.4, 592.6, 1, 0),
    (4, 0): (98.4, 649.5, 1, 0),
    # left, flat
    (0, 0): (204.9, 478.6, 1, 0),
    (0, 1): (261.9, 478.6, 1, 0),
    (0, 2): (318.6, 473.0, 1, 0),
    (1, 1): (212.1, 535.7, 1.5, 0),
    (1, 2): (283.4, 535.7, 1, 0),
    (2, 1): (290.4 - 1.375 * PX_PER_U, 592.6, 1.75, 0),  # 1.75u, left of A
    (2, 2): (290.4, 592.6, 1, 0),
    (3, 1): (311.6 - 1.625 * PX_PER_U, 649.5, 2.25, 0),  # 2.25u, left of Z
    (3, 2): (311.6, 649.5, 1, 0),
    (4, 1): (183.5, 706.4, 1.5, 0),
    (4, 2): (254.8, 706.5, 1, 0),
    # left, rotated
    (0, 3): (379.4, 482.6, 1, 1),
    (0, 4): (435.5, 492.5, 1, 1),
    (0, 5): (491.6, 502.4, 1, 1),
    (0, 6): (547.6, 512.4, 1, 1),
    (1, 3): (344.7, 534.3, 1, 1),
    (1, 4): (400.7, 544.2, 1, 1),
    (1, 5): (456.8, 554.1, 1, 1),
    (1, 6): (512.8, 564.1, 1, 1),
    (2, 3): (351.6, 593.3, 1, 1),
    (2, 4): (407.6, 603.3, 1, 1),
    (2, 5): (463.7, 613.1, 1, 1),
    (2, 6): (519.8, 623.0, 1, 1),
    (3, 3): (373.2, 654.9, 1, 1),
    (3, 4): (429.2, 664.8, 1, 1),
    (3, 5): (485.3, 674.7, 1, 1),
    (3, 6): (541.3, 684.5, 1, 1),
    (4, 3): (384.3, 714.6, 1, 1),  # cutouts for 1u and 1.5u merge
    (4, 6): (489.6, 731.7, 2.75, 1),  # cutouts for 2.25u and 2.75u merge
    # right, rotated
    (0, 8): (667.5, 507.4, 1, -1),
    (0, 9): (723.6, 497.5, 1, -1),
    (0, 10): (779.6, 487.6, 1, -1),
    (0, 11): (835.6, 477.7, 1, -1),
    (1, 7): (646.0, 569.0, 1, -1),
    (1, 8): (702.1, 559.0, 1, -1),
    (1, 9): (758.1, 549.2, 1, -1),
    (1, 10): (814.2, 539.4, 1, -1),
    (2, 7): (667.5, 623.0, 1, -1),
    (2, 8): (723.6, 613.0, 1, -1),
    (2, 9): (779.6, 603.2, 1, -1),
    (2, 10): (835.7, 593.3, 1, -1),
    (3, 7): (646.0, 684.6, 1, -1),
    (3, 8): (702.0, 674.7, 1, -1),
    (3, 9): (758.1, 664.7, 1, -1),
    (3, 10): (814.1, 654.9, 1, -1),
    (4, 7): (697.7, 731.7, 2.25, -1),  # cutouts for 2.25u and 2.5u merge
    (4, 10): (803.0, 714.6, 1.5, -1),  # cutouts for 1.25u and 1.5u merge
    # right, flat
    (0, 12): (896.9, 473.2, 1, 0),
    (0, 13): (953.9, 478.7, 1, 0),
    (0, 14): (953.9 + 1.5 * PX_PER_U, 478.9, 2, 0),  # 2u, right of =
    (1, 11): (875.5, 532.5, 1, 0),
    (1, 12): (932.4, 535.6, 1, 0),
    (1, 13): (989.4, 535.6, 1, 0),
    (2, 13): (1060.5, 535.6, 1.5, 0),
    (2, 11): (897.0, 592.7, 1, 0),
    (2, 12): (953.8, 592.7, 1, 0),
    (2, 14): (953.8 + 1.625 * PX_PER_U, 593.9, 2.25, 0),  # 2.25u, right of '
    (3, 11): (875.5, 649.5, 1, 0),
    (3, 12): (932.5, 649.5, 1, 0),
    (3, 13): (932.5 + PX_PER_U, 649.5, 1, 0),  # right of /
    (3, 14): (932.5 + 2.375 * PX_PER_U, 649.5, 1.75, 0),  # 1.75u, right of up
    (4, 12): (989.2 - PX_PER_U, 706.5, 1, 0),  # the three arrow cutouts merge
    (4, 13): (989.2, 706.5, 1, 0),
    (4, 14): (989.2 + PX_PER_U, 706.5, 1, 0),
}

# Where merged cutouts don't pin a key down, shift it along its rotated row (in u) to the chosen option.
MERGED_SHIFT = {(4, 7): -0.0625, (4, 10): -0.0625}


def key(matrix: tuple[int, int], cx: float, cy: float, w: float, side: int) -> dict[str, Any]:
    r = ROTATION * side
    shift = MERGED_SHIFT.get(matrix, 0) * PX_PER_U
    cx += shift * math.cos(math.radians(r))
    cy += shift * math.sin(math.radians(r))
    x, y = (round((c - o) / PX_PER_U, 3) for c, o in zip((cx, cy), PLATE_ORIGIN, strict=True))
    out: dict[str, Any] = {"matrix": list(matrix), "x": round(x - w / 2, 3), "y": round(y - 0.5, 3)}
    if w != 1:
        out["w"] = w
    if r:
        out |= {"r": r, "rx": x, "ry": y}  # rotate around the key's own center
    return out


def main() -> None:
    layout = sorted((key(m, *v) for m, v in KEYS.items()), key=lambda k: (k["matrix"][0], k["x"]))
    json.dump(
        {
            "keyboard_name": "Neo Ergo",
            "matrix_size": {"rows": 5, "cols": 15},
            "layouts": {"LAYOUT": {"layout": layout}},
        },
        sys.stdout,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
