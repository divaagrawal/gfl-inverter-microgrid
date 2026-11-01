# Design

## Visual world

An operations-room event recorder: dark graphite field, electric cyan signal paths, restrained amber warnings, and a single high-salience red fault interval. The dashboard operates like an engineer's post-event review, not a generic analytics template.

## Surface

The dashboard opens with the disturbance timeline and a control-mode selector. Event cards, KPI readouts, and the synchronized traces answer: did the microgrid stay energized, how far did frequency move, and when did the inverter hit its current limit?

## Tokens

- Background: `#07111f`; surface: `#0d1b2d`; ink: `#e6f3ff`; muted: `#8ba5be`.
- Nominal/healthy: `#36d7c4`; grid-forming: `#53a7ff`; warning: `#f6bd60`; fault: `#ff5c77`.
- Typography: Avenir/system sans with monospaced tabular measurements.

## Interaction and responsiveness

- Selecting GFL, droop GFM, or VSM redraws all four linked traces and the operating readout from the saved CSV data.
- The event rail is a cursor-controlled time reference; hovering it reports the active phase without obscuring the traces.
- At narrow widths, the control rail, operating readout, and four plots collapse in a declared order rather than being squeezed into unreadable columns.

