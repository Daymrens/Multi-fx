# UI Fix List — Gate Pedal (current build) → Spec-Compliant

For **Daymrens/Multi-fx**. Direct punch-list against the latest
screenshot. Good progress already — shell color, corner screws, 2-column
knob grid, and a real footswitch are all in place. This file is only the
remaining gap, in priority order, with exact numbers so it's not
guesswork.

---

## 0. What's already correct — don't touch

- Shell fill = module tab color (sage green for Gate) ✅
- Corner screws present at all 4 corners ✅
- Knob grid is a proper 2×2 for 4 params (the earlier collision/3+1 bug
  is fixed) ✅
- Footswitch exists as a real circular button, not a checkbox ✅
- Knob size is uniform across all 4 knobs ✅

---

## 1. Critical fixes (functional/visual bugs)

### 1.1 Readout only shows for one knob
Only `Thresh` has a value box (`-40dB`). `Attack`, `Hold`, `Release` show
nothing. Every knob needs its own readout — this isn't a "some knobs get
readouts" case (that's for things like Drive/Tone where a number doesn't
matter); for a **Gate**, every param is precision-critical (thresholds,
timing in ms), so all 4 get a readout box, individually positioned under
their own knob — not one shared box for the whole module.

```python
# gate config — all four need show_readout=True
{ "id": "threshold", "label": "Thresh",  "show_readout": True, ... }
{ "id": "attack",    "label": "Attack",  "show_readout": True, ... }
{ "id": "hold",      "label": "Hold",    "show_readout": True, ... }
{ "id": "release",   "label": "Release", "show_readout": True, ... }
```

### 1.2 Range-dots are misplaced
The red/teal dots on `Thresh` are stacked close together on the left
side of the knob — reads as decoration, not information. Per spec they
mark the **start and end of the rotation sweep** (roughly 7–8 o'clock
and 4–5 o'clock), so they should sit on opposite sides of the knob, not
adjacent to each other on one side.

Also: **decide whether Gate actually needs range-dots at all.** They
were speced as an optional marker for a "special/modulated" parameter —
if Threshold isn't modulated or range-flagged for a specific reason,
remove them from Gate entirely rather than leaving them as unexplained
decoration. Reserve them for a module where they mean something.

### 1.3 Top-edge collision
`Thresh` / `Attack` labels sit almost flush against the top-left corner
screw — no breathing room. Root cause: no panel inset (see 2.1) — once
the dark inset panel exists, labels sit inside it with proper margin
automatically.

---

## 2. Layout fixes (structural)

### 2.1 Missing panel inset
Right now knobs sit directly on the green shell background. Per
`pedal_ui_spec.md` §2.2, there should be a distinct **dark charcoal
inset panel** behind the knob grid (like both source mockups) — this is
what currently makes the module read as "a color with knobs floating on
it" instead of "a pedal." Add:

- Panel rect inset `Spacing.LG` (24px) from shell left/right edges,
  `Spacing.MD` (16px) from top (below the screw row)
- Panel fill: dark charcoal (`#2b2f36`), matches the two other spec docs
- Panel bevel border (1px light top/left, 1px dark bottom/right)

### 2.2 Shell is too tall for its content
There's a large dead gap between the `-40dB` readout and the `Hold`/
`Release` row, and another large gap between the Release row and the
footswitch. The shell should size to content, not stretch to fill
available vertical space. Using the grid constants from
`ui_enhancements.md`:

```python
KNOB_DIAMETER = 72        # GRID * 9
CELL_H = 112               # GRID * 14, includes label + knob + readout
PANEL_PADDING = 24         # Spacing.LG, all sides
NAMEPLATE_ZONE = 32        # Spacing.XL
LED_ZONE = 24              # Spacing.LG
FOOTSWITCH_ZONE = 96       # includes switch + margin

shell_height = (
    Spacing.MD                     # top margin above screws
    + PANEL_PADDING * 2
    + (rows * CELL_H)              # 2 rows for Gate = 224
    + NAMEPLATE_ZONE
    + LED_ZONE
    + FOOTSWITCH_ZONE
    + Spacing.MD                   # bottom margin
)
```

For Gate specifically (2 rows), this should land around **480–520px**
tall, not stretch to fill the whole content area regardless of module
size — a `sizeHint()`-driven fixed height, not a layout stretch factor.

### 2.3 Shell width
Current width looks correct (matches a 2-column knob grid + panel
padding) — just confirm it's computed the same way (`2 * CELL_W +
PANEL_PADDING * 2`), not hardcoded, so 3-column-wide modules (if any
exist later) scale consistently.

### 2.4 Pedal placement in the content area
Right now the pedal sits pinned top-left with a large unused black area
to the right. Two reasonable options — pick one and apply consistently:

- **Center it** in the content area (simplest, reads intentional)
- **Left-align but vertically center** it in the available height
  (matches "one module in focus" framing, less floaty than pure center)

Pinned top-left with dead space reads as unfinished, so this needs a
decision either way.

---

## 3. Missing chassis elements

- **Module nameplate** — no `GATE` text currently rendered. Add per
  `ui_enhancements.md` §4: condensed caps, bold, small, positioned
  between the panel bottom and the LED.
- **Status LED** — not present as its own element (footswitch may be
  absorbing this role visually with its green ring, but that's the
  bypass-state ring, not a dedicated LED). Add a separate small LED
  circle above the footswitch, per the polarity decision already made
  in `pedal_skin_migration.md` §5 (lit = engaged).
- **Footswitch base** — currently a plain circle. Mockups use a
  hex-nut base plate under the button for a more physical read; low
  priority polish, fine to defer.

---

## 4. Per-module checklist — replicate to the other 4 tabs

Everything above was diagnosed on Gate specifically because it's the
only one currently visible/built out. Before considering this "done,"
confirm the same treatment applies uniformly:

- [ ] FilterEQ, Compressor, Delay, Limiter each get the same shell +
      panel + nameplate + LED + footswitch treatment (not just Gate)
- [ ] Every knob in every module gets a readout box (per 1.1's
      reasoning — these are all precision DSP params, not "feel" knobs)
- [ ] Shell height is computed from each module's own param count, not
      copy-pasted from Gate's fixed height (Delay has 6 params → 3 rows
      → taller shell than Gate's 4-param/2-row shell)
- [ ] Range-dots, if used at all, are applied deliberately (per 1.2) to
      only the params where they carry real meaning — not by default
      on every module
- [ ] Nameplate text updates per module (`GATE`, `FILTEREQ`,
      `COMPRESSOR`, `DELAY`, `LIMITER`)

---

## 5. Priority order

1. Fix readout consistency (1.1) — quick, high-visibility bug
2. Add panel inset (2.1) — single biggest visual upgrade, fixes the
   top-edge collision (1.3) as a side effect
3. Fix shell sizing to content (2.2) — removes the dead-space problem
4. Add nameplate + LED (3) — completes the "physical pedal" read
5. Fix/remove range-dots (1.2) — cosmetic, lowest urgency
6. Roll all of the above out to the other 4 modules (4)
7. Decide + apply content-area placement (2.4)
