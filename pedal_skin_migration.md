# Pedal-Skin Migration — From Rack Panel to Physical Stompbox

For **Daymrens/Multi-fx**. Takes the current screenshot (functional rack
panel: tab strip + flat knob row + checkbox bypass) and maps it to the
full pedal anatomy from `pedal_ui_spec.md` + the grid rules from
`ui_enhancements.md`. This is a migration doc, not a rewrite — most of
the app chrome stays exactly as-is.

---

## 1. What stays untouched (app chrome, not part of the pedal)

These are already working and are **not** pedal elements — leave them:

- Title bar / window controls
- `+ Add Effect` button, `Stopped` status label
- Module tab strip (Gate / FilterEQ / Compressor / Delay / Limiter) —
  the color-coded top-bar strip is good and stays as the module switcher
- IN/OUT jack visualization block (bottom-left)
- Routing panel (Input/Output device selectors, bottom-right)
- Transport bar (Start / Load Preset / Save / Clear, latency readout)

**Only the big content area** — currently "Gate" title + flat knob row +
`Bypass` checkbox — becomes the actual rendered pedal.

---

## 2. Before → after, element by element

| Current element | Becomes |
|---|---|
| `Gate` title, top-left, plain text | Module **nameplate**, moved to the bottom of the shell per §4 of `ui_enhancements.md` — condensed caps, e.g. `GATE` |
| `☐ Bypass` checkbox, top-right | Removed as a checkbox. Replaced by the **footswitch** at the bottom of the shell — click toggles bypass, `Bypass` state still exists in code, just driven by footswitch click instead of checkbox. (Optional: keep a tiny checkbox somewhere in a settings/accessibility view, but it's no longer the primary control.) |
| Flat dark background behind knobs | **Shell + panel** — shell fill = module color (already established via tab strip color, e.g. Gate = green), panel = dark charcoal inset per §2.2 of `pedal_ui_spec.md` |
| Knobs already circular w/ arc + indicator line | Keep as-is — this part is already close to spec, see §3 |
| Label above / value below, currently colliding | Fixed via the grid system in §3 of `ui_enhancements.md` |
| (nothing currently) | Add **LED** (lit = bypassed off / engaged — decide polarity, see §5) |
| (nothing currently) | Add **corner screws + panel bevel** per §4 of `ui_enhancements.md` |

---

## 3. Fixing the current knob issues in-place first

Before adding the shell, fix what's visible now — these bugs will just
get worse once a shell/footswitch is added around them:

- **Label/value collision** (`Thresh` overlapping `1.0ms`): give every
  knob cell a fixed height (`CELL_H = GRID * 14`, see enhancements §3)
  so label, knob, and readout each get a reserved band — no float/wrap.
- **Uneven column grid**: current layout looks like knobs are placed by
  content-flow (auto-wrap) rather than a fixed 2-column grid. Force
  `cols = 2` always, per `_layout_grid()` in the enhancements doc, so a
  4-param module (Gate: Thresh/Attack/Hold/Release) renders as a clean
  2×2, not 3-then-1.
- **Arc progress ring**: nice touch already present that wasn't in the
  original mockups — keep it, just make sure the arc's start/end angle
  matches the same indicator-line sweep range so they stay visually in
  sync (arc fill = 0 → current value, line = current value position).

---

## 4. New `Gate` pedal layout (worked example, using real values from the screenshot)

```
┌─────────────────────────────────┐  <- shell (green fill, Gate's tab color)
│ ●                             ● │  <- corner screws
│  ┌───────────────────────────┐  │
│  │  Thresh    Attack   Hold  │  │  <- panel (dark, bevel border)
│  │   (-40dB)   (1.0ms) (20ms)│  │
│  │   ◉         ◉        ◉    │  │
│  │                            │  │
│  │  Release                   │  │
│  │  (50ms)                    │  │
│  │   ◉                        │  │
│  └───────────────────────────┘  │
│                                  │
│           GATE                  │  <- nameplate
│                                  │
│            ●  <- LED             │
│           ( )  <- footswitch     │
│ ●                             ● │
└─────────────────────────────────┘
```

Note: 4 params still renders as **2 columns × 2 rows**, not 3+1 — fixing
the grid issue from §3 also fixes this layout naturally once `cols = 2`
is enforced.

```python
# effect_panel.py
class PedalWidget(QWidget):
    def __init__(self, config: PedalConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.bypassed = False
        self.knobs = [Knob(p) for p in config.params]
        self.footswitch = FootswitchButton()
        self.footswitch.clicked.connect(self.toggle_bypass)
        self.led = StatusLED()
        self._layout_grid()  # forces cols=2, uses fixed CELL_W/CELL_H

    def toggle_bypass(self):
        self.bypassed = not self.bypassed
        self.led.set_lit(not self.bypassed)   # see §5 for polarity decision
        self.bypassChanged.emit(self.bypassed)
        self.update()

    def paintEvent(self, event):
        # 1. shell: rounded rect, module theme color, corner screws, top highlight
        # 2. panel: inset rounded rect, bevel border
        # 3. knobs: already positioned by _layout_grid()
        # 4. nameplate: module name, bottom of shell above LED
        # 5. LED + footswitch: bottom of shell
        ...
```

---

## 5. LED / bypass polarity — pick one and use it everywhere

Real stompboxes vary on this, so it needs to be a deliberate, consistent
choice across all 8 modules rather than left ambiguous:

- **Option A (most common on real pedals):** LED lit = effect **engaged**
  (processing), dark = bypassed. Matches the mockups' red LED reading as
  "on."
- **Option B:** LED lit = bypassed/muted, matching how `Bypass` currently
  reads as a positive checkbox state in the existing UI (`☑ Bypass` = on
  means bypassed = true).

Recommend **Option A** — it matches physical pedal convention and is
less confusing than "lit LED = effect is off." If Option A is chosen,
`toggle_bypass()` inverts the `Bypass` boolean's meaning relative to the
LED, which is fine — LED tracks `not bypassed`, as shown in the code
snippet above.

---

## 6. Migration checklist for opencode

- [ ] Fix knob grid to strict 2-column layout (`cols = 2` always) —
      do this first, independently of the shell work, since it fixes a
      visible bug right now
- [ ] Fix label/readout vertical collision using fixed per-cell height
- [ ] Wrap the existing knob grid in a `PedalWidget` shell (rounded rect,
      module tab color as fill, per `pedal_ui_spec.md` §2.1)
- [ ] Add dark inset panel with bevel border around the knob grid
      (§2.2)
- [ ] Replace `☐ Bypass` checkbox with `FootswitchButton` at shell
      bottom, wire to the same `bypassed` state
- [ ] Add `StatusLED`, decide + implement polarity per §5 above, apply
      consistently to all 8 modules
- [ ] Add module nameplate text (module name, condensed caps) between
      panel and footswitch
- [ ] Add corner screws + top highlight edge + panel bevel (cheap paint
      additions, §4 of `ui_enhancements.md`)
- [ ] Confirm all 8 modules share identical shell height for the same
      param count, and identical footswitch/LED row position regardless
      of shell color (grid discipline from `ui_enhancements.md` §5)
- [ ] Re-check `chain_view.py` — once modules have footswitches drawn
      *inside* their own widget instead of a shared checkbox, confirm
      the drag-and-drop chain still reads left-to-right sensibly with
      each module now a taller, self-contained pedal graphic
