# Stompbox / Pedal UI — Component Spec

For **Daymrens/Multi-fx** (github.com/Daymrens/Multi-fx). Reference spec
derived from two pedal mockups, adapted to the actual repo structure:

```
ui/
├── main_window.py      # Main application window
├── chain_view.py        # Drag-and-drop effect chain
├── effect_panel.py      # Per-effect parameter controls  <- this spec mostly targets this
├── knob.py              # Custom rotary knob widget       <- and this
├── meter.py             # Peak level meter
└── theme.py             # Design system tokens
pedal/                    # UI design references (this file + mockups belong here)
```

Stack: **PyQt6**, so all drawing below should be read as `QPainter` /
`QWidget` guidance, not tkinter/canvas. Each of the 8 DSP modules (Gate,
FilterEQ, Compressor, Distortion, Modulation, Delay, Reverb, Limiter)
gets rendered as one pedal instance inside `effect_panel.py`, using
`knob.py` for every parameter and `theme.py` for the per-module skin.

---

## 1. Anatomy (top → bottom)

1. **Top jack nub** (optional, decorative) — small dark rounded rectangle
   centered at the very top edge of the shell.
2. **Outer shell** — the pedal body. Rounded-rect, portrait orientation,
   roughly a **1 : 1.9 width\:height** ratio. Solid color per pedal "skin".
3. **Control panel** — a recessed dark panel (rounded-rect, inset from the
   shell edges) that houses the knobs. Two styles seen:
   - *Flush inset* (Image 1): dark charcoal panel, no border, soft shadow.
   - *Framed inset* (Image 2): black panel with a thin light border/bevel,
     more "engraved plate" look.
4. **Knob grid** — 2 columns × N rows (2×2 in Image 1, 2×3 in Image 2).
   Each knob has a **label above** and, optionally, a **value readout
   below**.
5. **Side lugs** (optional decorative) — small barrel-shaped bumps on the
   left/right edges of the shell, roughly at the panel/body seam. Cosmetic
   only (evokes rack ears / knob shafts on the side of a stomp enclosure).
6. **Mode control** (optional) — toggle switch OR none, sits in the body
   area between the panel and the LED.
7. **Status LED** — small circle, centered, red when active.
8. **Footswitch** — large circular button at the bottom, on a hex-nut-style
   base, used for bypass/on-off.
9. **I/O jack** (optional, Image 1 only) — a large chrome jack socket at
   the very bottom, used when the pedal is a literal audio-in/audio-out
   node rather than a plugin-style effect.

---

## 2. Component specs

### 2.1 PedalShell
| Property | Value |
|---|---|
| shape | rounded rectangle, corner radius ~ 6–8% of width |
| aspect ratio | width : height ≈ 1 : 1.9 |
| fill | flat color (theme-driven, see §4) |
| shadow | soft drop shadow, offset down-right, ~15–20% opacity |
| border | 2–4 px darker shade of fill, or none |

### 2.2 ControlPanel
| Property | Value |
|---|---|
| shape | rounded rect, inset ~8% from shell's left/right edges |
| fill | dark charcoal / near-black (`#2b2f36`–`#1c1c1c`) |
| border | none (flush) or 2px light stroke (framed) |
| padding | enough for label + knob + optional readout per cell |

### 2.3 Knob
| Property | Value |
|---|---|
| shape | circle, radial gradient dark-gray → near-black (top-lit) |
| indicator | single white bar from center to ~80% radius, rotates to show value |
| range mapping | rotation sweeps ~270° (7–8 o'clock to 4–5 o'clock), 0.0 → min angle, max → max angle |
| min-dot / max-dot (optional) | small colored dot at each end of the sweep arc, used to mark min/max range visually (seen in Image 2 — red pair on one knob, teal pair on another). Use sparingly to flag a "special" or modulated parameter. |
| label | plain white text, centered above knob, e.g. `Label1` |
| value readout (optional) | small bordered rect below knob showing current value, e.g. `10.0` — only include when precision matters (not needed for every knob) |

### 2.4 ToggleSwitch (optional, body-mounted)
| Property | Value |
|---|---|
| shape | chrome cylindrical toggle, small oval base plate |
| states | 2 or 3-position, mechanical look |
| use case | switches pedal mode/algorithm, not a continuous parameter |

### 2.5 StatusLED
| Property | Value |
|---|---|
| shape | small circle, ~1.5–2% of shell width |
| color | red when engaged, dim/dark red or gray when bypassed |
| glow | optional soft radial highlight when lit |

### 2.6 Footswitch
| Property | Value |
|---|---|
| base | hexagonal or octagonal nut plate, metallic/light |
| button | circular cap, slightly domed, tan/cream or dark, centered on base |
| position | bottom third of shell, centered horizontally |
| behavior | click toggles bypass; LED reflects state |

### 2.7 IOJack (optional)
| Property | Value |
|---|---|
| shape | concentric circles — chrome hex nut ring, then dark socket hole |
| position | below footswitch if present, or omit entirely for plugin-only pedals |
| use case | only needed if you're visually representing physical audio routing; skip for FX that are purely FL Studio plugin params |

---

## 3. Layout rules

- Knob grid is **2 columns wide**, rows = `ceil(num_params / 2)`.
- Panel height grows with row count; shell height grows with panel height
  (footswitch/LED zone stays a fixed proportion at the bottom).
- Labels are always short, single word or short code (`Label1`, `Mix`,
  `Rate`, `Depth`...) — keep to ≤ 8 characters so they don't wrap.
- Value readout boxes are optional per-knob — use them for parameters
  where the user needs an exact number (delay time, semitone shift), skip
  them for "feel" parameters (drive, tone) where the knob position alone
  is enough.

---

## 4. Theming (per-effect skin)

Each pedal ("effect") gets its own color theme, applied to shell fill +
accent (LED/footswitch trim). Panel stays dark/neutral across all themes
so labels/knobs stay legible.

```json
{
  "theme": {
    "shell_fill": "#8FA888",
    "shell_border": "#5f6f5c",
    "panel_fill": "#2b2f36",
    "panel_style": "flush",       // "flush" | "framed"
    "accent": "#c0392b",          // LED / footswitch highlight color
    "background": "#e8a876"       // scene backdrop, not part of pedal itself
  }
}
```

Two reference styles already captured:

| Style | Shell | Panel | Notes |
|---|---|---|---|
| **"Studio" skin** (Image 1) | sage green, matte | flush dark panel, no border | side lugs, top jack, bottom I/O jack — reads as a real physical pedal |
| **"Stomp" skin** (Image 2) | orange, flat cel-shaded | framed panel with bevel border | toggle switch, glossy highlight streaks, hex-nut footswitch — more cartoon/vintage stompbox |

---

## 5. Data model (drives the UI generically)

Mapped directly from the actual DSP Chain table in the README — one
config per module, one pedal per config. `Delay` shown here since it maps
cleanly onto the Image-2 (6-knob) mockup, with `Ping-Pong` as the toggle:

```json
{
  "id": "delay",
  "name": "Delay",
  "theme": "stomp_orange",
  "has_toggle": true,
  "toggle_label": "Ping-Pong",
  "has_io_jack": false,
  "params": [
    { "id": "time",      "label": "Time",   "min": 10,  "max": 2000,  "default": 350, "unit": "ms", "show_readout": true },
    { "id": "feedback",  "label": "Fbk",    "min": 0,   "max": 95,    "default": 35,  "unit": "%",  "show_readout": false },
    { "id": "lp_cutoff", "label": "LP Cut", "min": 200, "max": 20000, "default": 8000,"unit": "Hz", "show_readout": true },
    { "id": "mix",       "label": "Mix",    "min": 0,   "max": 100,   "default": 50,  "unit": "%",  "show_readout": false }
  ]
}
```

Other modules follow the same shape, params pulled straight from the
README spec table, e.g.:

```json
{ "id": "gate", "name": "Gate", "theme": "stomp_green", "has_toggle": false,
  "params": [
    { "id": "threshold", "label": "Thresh",  "min": -80, "max": 0,   "unit": "dB" },
    { "id": "attack",    "label": "Attack",  "min": 0.1, "max": 50,  "unit": "ms" },
    { "id": "hold",      "label": "Hold",    "min": 0,   "max": 200, "unit": "ms" },
    { "id": "release",   "label": "Release", "min": 5,   "max": 500, "unit": "ms" }
  ]
}
```

Modules with a **Type/Mode selector** (FilterEQ's 7 types, Distortion's 4
types, Modulation's 3 modes) should use the `ToggleSwitch`/rotary-select
element from §2.4 rather than a knob — a knob implies a continuous
range, and these are discrete enum choices.

Render logic: `rows = ceil(len(params)/2)` → resize panel → resize shell →
place knobs in reading order (left-to-right, top-to-bottom). This should
live as a `PedalConfig` dataclass or JSON loaded by `effect_panel.py`,
consumed by one `PedalWidget(QWidget)` class shared across all 8 modules.

---

## 6. Implementation notes (PyQt6)

Matches the repo as-is — no new dependency needed, this is all native
`QPainter`.

### `ui/knob.py` — `Knob(QWidget)`

```python
class Knob(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, label: str, vmin: float, vmax: float, default: float,
                 unit: str = "", show_readout: bool = False,
                 range_dots: bool = False, parent=None): ...

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 1. radial gradient fill for the knob body (QRadialGradient,
        #    dark-gray center -> near-black edge, light source top-left)
        # 2. white indicator bar, rotated via QPainter.rotate() to
        #    angle_for_value()
        # 3. optional range_dots at sweep start/end (QPainterPath, small
        #    filled circles in accent color)
        # 4. label text above, readout box below (if show_readout)

    def angle_for_value(self) -> float:
        # maps self._value in [vmin, vmax] to sweep range, e.g. -135° to +135°
        ...

    def mousePressEvent(self, event): self._drag_start_y = event.position().y()
    def mouseMoveEvent(self, event):
        # vertical drag: up = increase, down = decrease
        # this is the standard pedal-knob UX, avoids fiddly circular dragging
        dy = self._drag_start_y - event.position().y()
        ...
        self.valueChanged.emit(self._value)
```

### `ui/effect_panel.py` — `PedalWidget(QWidget)`

One class, reused for all 8 modules — differs only by the `PedalConfig`
passed in (§5) and the `theme.py` skin key.

```python
class PedalWidget(QWidget):
    def __init__(self, config: PedalConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.knobs = [Knob(p.label, p.min, p.max, p.default, p.unit,
                            p.show_readout, p.range_dots)
                      for p in config.params]
        self._layout_grid()   # 2 columns, rows = ceil(len(params)/2)

    def paintEvent(self, event):
        # shell: rounded rect via QPainterPath.addRoundedRect(), themed fill
        # panel: inset rounded rect, flush or framed border per theme
        # footswitch: QPainterPath ellipse + hex-nut path underneath
        # LED: small filled circle, accent color, lit/dim per bypass state
        ...

    def sizeHint(self) -> QSize:
        # derives shell size from knob grid, per §3 layout rules
        ...
```

### `ui/theme.py` — design tokens

Extend the existing token system with a `PedalSkin` per module, matching
the JSON shape in §4 (`shell_fill`, `panel_style`, `accent`, etc.) so
`chain_view.py` can request "give me the Delay pedal in its skin" without
`effect_panel.py` knowing color values directly.

### `pedal/` folder

Good spot for this file plus the two source mockups (`image-1.png`
"Studio" skin, `image-3.png` "Stomp" skin) as living design references
opencode can re-check against while implementing `knob.py`/`effect_panel.py`.

---

## 7. Open questions for the next design pass

- Do "no instrument" utility pedals (e.g. gain/utility trims) need the
  I/O jack element at all, or should that be reserved only for pedals
  that represent an actual audio-routing node?
- Should `range_dots` (the small colored min/max markers) be reserved for
  a specific meaning — e.g. "this parameter is currently modulated/
  automated" — rather than pure decoration?
