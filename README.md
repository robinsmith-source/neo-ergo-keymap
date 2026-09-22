# neo-ergo-keymap

My keymap for the Neo Ergo tri-mode (Alice layout), configured with
[VIA](https://usevia.app) and drawn with [keymap-drawer](https://github.com/caksoylar/keymap-drawer).

![keymap](https://raw.githubusercontent.com/robinsmith-source/neo-ergo-keymap/images/keymap.svg)

| Layer | How | What |
| --- | --- | --- |
| **Base** | default | QWERTY, `Space` (right) holds **Fn**, `Caps` holds **Nav** |
| **Fn** | hold right `Space` | F1–F12, media, RGB, Bluetooth/2.4G/USB switching |
| **Mac** | – | Base with `Alt`/`GUI` swapped |
| **Nav** | hold `Caps` | F13–F24, arrows on `WASD`, volume |

## Restore

1. Open [usevia.app](https://usevia.app) → Settings → enable **Show Design tab**
2. Design → load the Neo Ergo VIA definition (`neo_ergo_v3.json` from the vendor)
3. Configure → **Save + Load** → load [`via/neo_ergo.layout.json`](via/neo_ergo.layout.json)

## Update

Change the keymap in VIA, then **Save + Load → Save** over `via/neo_ergo.layout.json` and push.
CI re-renders the image to the `images` branch.

Render locally (needs [uv](https://docs.astral.sh/uv/)):

```bash
scripts/render.sh   # → build/keymap.svg
```

## How the drawing works

1. [`keymap-drawer/neo_ergo.json`](keymap-drawer/neo_ergo.json) is the physical layout: key positions,
   sizes and the 10° rotation of each half. It was generated once from the VIA definition with
   `scripts/via_layout.py`, which also picks the layout options in use (split backspace, etc.).
2. [`scripts/via2qmk.py`](scripts/via2qmk.py) reorders the VIA backup (stored in matrix order) into
   a QMK `keymap.json`.
3. keymap-drawer parses that into readable labels using
   [`keymap-drawer/config.yaml`](keymap-drawer/config.yaml) and draws the SVG.
