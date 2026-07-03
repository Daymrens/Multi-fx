# UI Enhancements — Precision Alignment & Hardware-Grade Polish

For **Daymrens/Multi-fx**. Builds on `pedal_ui_spec.md` (component anatomy)
— this file is about making the *whole* GUI (all 8 modules in
`chain_view.py`, each rendered via `effect_panel.py`) read as one
cohesive, precisely-aligned hardware multi-fx unit rather than 8
independently-eyeballed panels bolted together.

---

## 1. The core problem this fixes

Right now each `PedalWidget` can size/space itself independently. A real
multi-fx floor unit (Boss GT / Line6 Helix / Zoom G-series) never looks
like that — every module shares the *exact same* grid, knob pitch, label
baseline, and margin, so the eye reads it as one manufactured object, not
a row of separately-drawn boxes. Everything below exists to enforce that.

---

## 2. Base grid system

All layout in `theme.py` should be derived from **one base unit**, not
ad-hoc pixel values scattered across widgets.

```python
# theme.py
GRID = 8  # px, base unit — every margin/padding/size is a multiple of this

class Spacing:
    XS = GRID // 2      # 4
    SM = GRID           # 8
    MD = GRID * 2        # 16
    LG = GRID * 3        # 24
    XL = GRID * 4         # 32
```

Rule: **no raw pixel numbers in widget code.** Every `setContentsMargins`,
`setSpacing`, knob diameter, panel inset, etc. references `Spacing.*` or
`GRID * n`. This is what makes multi-module alignment possible — if two
modules both round to the grid, they line up, full stop.

---

## 3. Knob grid — exact positioning

Currently knobs are placed by "2 columns, rows = ceil(params/2)" — correct
as a rule, but needs pixel-precise cell geometry so every module's knob
grid shares the same pitch:

| Element | Value |
|---|---|
| Knob diameter | `GRID * 9` (72px) — fixed across **all** modules, regardless of param count |
| Cell size (knob + label + readout) | `GRID * 12` wide × `GRID * 14` tall (96 × 112px) |
| Column gutter | `Spacing.MD` (16px) between cell centers' edges |
| Row gutter | `Spacing.MD` (16px) |
| Label baseline | fixed `Spacing.SM` above knob top edge, **every** label in the whole chain sits on the same relative baseline |
| Readout box baseline | fixed `Spacing.SM` below knob bottom edge |
| Panel inset (shell edge → panel edge) | `Spacing.LG` (24px) on all sides, identical for every module |

Consequence: a 4-knob module (2×2) and a 6-knob module (2×3) will have
**identical column width and knob size** — only row count differs. This
is what makes a mixed-size chain look manufactured instead of improvised.

```python
# effect_panel.py
class PedalWidget(QWidget):
    KNOB_DIAMETER = Spacing.XL + GRID  # 72px, constant across all modules
    CELL_W = GRID * 12
    CELL_H = GRID * 14

    def _layout_grid(self):
        cols = 2
        rows = math.ceil(len(self.config.params) / cols)
        for i, knob in enumerate(self.knobs):
            col, row = i % cols, i // cols
            x = self.panel_x + col * self.CELL_W
            y = self.panel_y + row * self.CELL_H
            knob.setGeometry(x, y, self.KNOB_DIAMETER, self.KNOB_DIAMETER)
```

---

## 4. Shell chassis polish (per-module "hardware" detail)

To read as real hardware rather than flat mockup rectangles, add these —
all cheap to draw, high impact:

- **Corner screws** — 4 small circles (Phillips-head or hex, ~6px)
  inset `Spacing.SM` from each shell corner. Draw as a dark ring +
  lighter cross/hex notch. This single detail sells "physical object"
  more than anything else.
- **Brushed/matte texture** — subtle diagonal noise or linear gradient
  overlay on the shell fill (very low opacity, 3–5%) instead of a flat
  color. Cheap `QLinearGradient` with 2–3 stops does this.
- **Top highlight edge** — 1–2px lighter stroke along the top edge of
  the shell only, simulating light catching the enclosure lip (seen
  faintly in both source mockups).
- **Panel bevel** — 1px light stroke on panel top/left, 1px dark stroke
  on panel bottom/right (classic inset-engrave look), instead of a flat
  border.
- **Module nameplate** — small text strip at the bottom of the shell
  (below the knob panel, above the footswitch) printing the module name
  in a condensed caps font, e.g. `DISTORTION`, `DELAY`. This is what
  actual multi-fx units do to identify modules in a chain, and it fixes
  the "which pedal is this" problem when 8 are lined up.

---

## 5. Alignment across the full chain (`chain_view.py`)

The biggest visual tell of an unpolished multi-pedal UI is modules that
don't share a **common baseline**. Enforce:

| Rule | Implementation |
|---|---|
| All shells share one **footswitch centerline** | footswitch Y-position is measured from the *bottom* of the shell, fixed offset, regardless of panel height — so 4-knob and 6-knob modules' footswitches still sit on one horizontal line when placed side by side |
| All shells share one **LED row** | same logic — LED Y fixed relative to shell bottom |
| Chain gutter | fixed `Spacing.MD` between adjacent shells, no variable gaps |
| Chain baseline | all shells bottom-align to the same Y in `chain_view.py`'s layout, even though top edges vary with knob-row count — i.e. taller modules grow *upward*, not downward |

```python
# chain_view.py
class ChainView(QWidget):
    def _layout_chain(self):
        baseline_y = self.height() - Spacing.XL
        x = Spacing.LG
        for pedal in self.pedals:
            shell_h = pedal.sizeHint().height()
            pedal.move(x, baseline_y - shell_h)   # bottom-aligned, grows upward
            x += pedal.width() + Spacing.MD
```

---

## 6. Interaction polish

| State | Treatment |
|---|---|
| Knob hover | subtle outer glow ring, accent color at ~20% opacity |
| Knob drag (active) | indicator bar brightens to pure white + glow; readout box border switches to accent color |
| Footswitch press | button depresses 2px (translate down), LED flips to lit instantly (no fade-in — real stomp switches are instant) |
| Module bypass | whole shell desaturates ~40% + LED goes dark red/dim, knobs stay interactive but visually "off" |
| Drag-reorder in chain | dragged module lifts with a stronger drop shadow (`Spacing.SM` blur → `Spacing.LG` blur) and 4% scale-up, others slide with eased animation to open a gap |
| Value readout edit | click-to-type should swap the readout `QLabel` for a `QLineEdit` in-place, same geometry, no layout shift |

---

## 7. Typography

| Role | Spec |
|---|---|
| Knob label | Bold, 11px, letter-spacing +0.5px, all as-given case (`Time`, not `TIME`) — matches source mockups |
| Module nameplate (§4) | Bold condensed, 10px, uppercase, letter-spacing +1px — distinct from knob labels so the eye doesn't confuse "what parameter" with "what module" |
| Value readout | Monospace or tabular-figure font, 11px, centered — numbers must not jitter horizontally as digits change |
| Units (`ms`, `Hz`, `dB`) | Same size as value, 60% opacity, no separate baseline shift |

---

## 8. Color discipline

Keep the **panel + knob + LED + footswitch** palette identical across
every module (dark charcoal panel, black knob, red/accent LED) — only the
**shell fill color** changes per module (per `theme.py` skin). This is
exactly how real multi-fx units differentiate module "pages" — one
consistent control language, color-coded outer housing only. Resist the
temptation to re-theme knobs or panels per module; that's what makes
mockup-style UIs look like a disconnected component library instead of
one product.

---

## 9. Checklist for opencode

- [ ] Replace all raw pixel literals in `knob.py`, `effect_panel.py`,
      `chain_view.py` with `Spacing.*` / `GRID` references
- [ ] Fix `KNOB_DIAMETER` as a class constant, not computed per-module
- [ ] Implement bottom-aligned chain layout (§5) so footswitch/LED rows
      line up across modules of different knob-row counts
- [ ] Add corner screws + panel bevel + nameplate to `PedalWidget.paintEvent`
- [ ] Add hover/drag/bypass visual states per §6
- [ ] Audit label vs. nameplate font usage — don't let them collapse to
      the same style
- [ ] Verify: place a 4-knob module (Gate) next to a 6-knob module (Delay)
      in `chain_view.py` and confirm footswitches + LEDs align on one
      horizontal line
