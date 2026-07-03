# Responsive Chain Layout Spec

For **Daymrens/Multi-fx** — `ui/chain_view.py`. Addresses the current
behavior visible in the latest screenshot: all 5 modules render
side-by-side in a fixed-width row, and once the window isn't wide enough,
the last one (`Limiter`) just gets hard-clipped at the edge with no
scrollbar, no fade, no hint that anything's cut off.

**Key principle:** a physical pedal doesn't stretch when your
pedalboard is bigger — you fit more pedals on, or you need a bigger
board. So "responsive" here means **the chain adapts how many pedals are
visible and how you navigate between them**, not squishing/stretching
individual pedal chassis to fit. Stretching a knob grid to fill leftover
width would break every alignment rule already established in
`ui_enhancements.md`.

---

## 1. Three responsive strategies — pick one as primary

### A. Horizontal scroll (recommended, matches current visual direction)
Wrap the pedal row in a `QScrollArea` (horizontal only). Pedals keep
their fixed chassis size; the window just reveals more or fewer of them.
This is the natural fit since the row layout already exists — it just
needs a scroll container instead of clipping.

### B. Wrap to multiple rows
When window width can't fit all pedals in one row, wrap remaining
pedals to a second row below. Works, but breaks the "one continuous
signal chain read left-to-right" mental model — a second row reads as
"which one comes after Limiter, top row or bottom?" Only worth it as a
**fallback at very narrow widths** (see §3), not the primary strategy.

### C. Uniform zoom/scale
A single scale factor applied to *all* pedals at once (never
per-pedal) so more fit on screen. Useful as a supplementary control, not
a replacement for scrolling — even scaled down, 8 full modules likely
won't fit most windows, so scroll is still needed eventually.

**Recommendation: A as primary, C as an optional user-facing zoom
control, B never (or only as last-resort ultra-narrow fallback).**

---

## 2. Horizontal scroll — implementation

```python
# chain_view.py
class ChainView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.strip = QWidget()          # the actual row of pedals
        self.strip_layout = QHBoxLayout(self.strip)
        self.strip_layout.setSpacing(Spacing.MD)
        self.strip_layout.setContentsMargins(Spacing.LG, Spacing.SM,
                                              Spacing.LG, Spacing.SM)
        self.scroll_area.setWidget(self.strip)
```

- Each `PedalWidget` reports a fixed `sizeHint()` (per
  `pedal_skin_migration.md` §4) — the `QHBoxLayout` respects that, no
  stretch factor on the pedals themselves.
- `setWidgetResizable(True)` lets the *scroll area* fill available
  space; it does **not** resize the child pedals — that's the whole
  point.

### Scroll affordances (fixing the current silent-clip problem)
- **Edge fade**: a ~24px gradient fade at the right edge of the visible
  area whenever content is scrollable further right (and left edge once
  scrolled). Cheap `QLinearGradient` overlay, transparent → background
  color. This alone fixes "is Limiter cut off or is that the end of the
  chain?"
- **Scroll-by-wheel**: map vertical wheel delta to horizontal scroll
  (common desktop-app pattern for horizontal strips) — no window
  resizing required, users can wheel-scroll to see hidden modules
  immediately.
- **Optional nav arrows**: small `‹` `›` buttons at the strip's far
  left/right edges, only visible when scroll is available in that
  direction, jump one pedal-width at a time.
- **Scroll-to-selected**: clicking a module in the top tab strip
  (`Gate`/`FilterEQ`/etc.) scrolls that pedal into view (`ensureWidgetVisible()`),
  since the tab strip and the chain row need to stay in sync — right now
  they're visually two separate things showing overlapping information
  (tab strip has its own little status dot; chain row has full pedals).

---

## 3. Breakpoints

Since pedal chassis width is fixed (not fluid), "breakpoints" here mean
*behavior* changes, not size changes:

| Window width | Behavior |
|---|---|
| ≥ all pedals' total width + margins | No scrollbar needed, row fits, scroll area is inert |
| < total width | Horizontal scroll active, edge fade appears on the clipped side(s) |
| < 1 pedal width + margins (extreme minimum) | This is the floor — see §5, don't design below this |

No wrap-to-second-row breakpoint needed if scroll is implemented
correctly — strategy B stays optional/unused unless there's a strong
reason to add it later (e.g. a "grid view" toggle for seeing the whole
chain at a glance, which is a different feature, not a responsive
fallback).

---

## 4. Optional zoom control (strategy C, supplementary)

If you want a way to see more of the chain at once without scrolling
(useful once someone has 6-8 modules loaded):

```python
class ChainView(QWidget):
    ZOOM_LEVELS = [1.0, 0.85, 0.7]   # 100%, 85%, 70%

    def set_zoom(self, level: float):
        self.zoom = level
        for pedal in self.pedals:
            pedal.setFixedSize(pedal.sizeHint() * level)  # uniform scale, applied to ALL pedals
        self.strip_layout.invalidate()
```

Rules if this is built:
- Zoom applies to **every pedal simultaneously**, never one at a time —
  a chain with some pedals at 100% and others shrunk would look broken,
  not responsive.
- Don't auto-zoom based on window size by default (surprising, makes
  pedals feel unstable while resizing). If auto-zoom is wanted later,
  it should snap to one of a few fixed levels, not continuously scale.
- A simple `100% / 85% / 70%` dropdown or +/- buttons near the tab strip
  is enough; this doesn't need to be continuous/draggable.

---

## 5. Minimum window size

Set `self.setMinimumWidth(...)` on the main window to roughly one pedal
width + margins + the transport bar's minimum content width (Start /
Load Preset / Save / Clear buttons need to stay readable) —
whichever is larger. Don't let the window shrink to a point where
transport buttons start clipping; that's worse than a scrollable pedal
strip.

---

## 6. What does NOT change

- Individual pedal chassis dimensions — fixed per module, per
  `pedal_skin_migration.md` §4 math. Responsiveness lives entirely in
  the **container** (scroll/zoom), never in the pedal widget itself.
- Knob grid, panel inset, footswitch, LED — none of these get relative/
  percentage sizing. They stay in fixed `Spacing.*`/`GRID` units
  regardless of window size, exactly per `ui_enhancements.md` §2.
- Tab strip at the top — stays fixed height, doesn't participate in the
  scroll area (it's chrome, scrolls independently if needed, likely
  never will since 5-8 tabs fit most window widths even when the pedal
  *bodies* below don't).

---

## 7. Checklist for opencode

- [ ] Wrap `chain_view.py`'s pedal row in a horizontal `QScrollArea`
      instead of letting the layout clip
- [ ] Add edge-fade overlay, shown conditionally based on scroll
      position vs. content width
- [ ] Map mouse wheel (vertical delta) to horizontal scroll on the strip
- [ ] Sync tab-strip clicks to `ensureWidgetVisible()` on the
      corresponding pedal
- [ ] Set a sane `setMinimumWidth()` on the main window so transport
      controls never clip
- [ ] (Optional) Add a 3-level uniform zoom control near the tab strip
- [ ] Confirm no pedal widget has a layout stretch factor — every
      `PedalWidget` must report and keep a fixed `sizeHint()`
