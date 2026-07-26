# Design Rationale

## The brief this design solves

The product's entire value proposition is that every score is
backed by inspectable evidence — never a black-box number. The UI
had to make that legible at a glance, not just support it
functionally. That's the thing to design *around*.

## Why not the default AI-generated looks

Three patterns show up constantly in generated UIs and were
deliberately avoided:
- **Cream background + serif headings + terracotta accent** — reads
  as "editorial blog," unrelated to an evaluation instrument.
- **Near-black background + neon accent** — reads as "generic dev
  tool," says nothing about explainability.
- **Broadsheet/newspaper column layout** — wrong information
  density for a dashboard people will scan repeatedly.

## What this uses instead: an inspection-instrument aesthetic

Closer to a mechanic's inspection sheet or a lab test readout than a
marketing dashboard — because that's literally what the product does:
measures specific criteria, checks them against a target, reports
pass/fail with the values that produced the verdict.

**Color** (`app/globals.css` `@theme` block):
- `ink` `#14213D` / `paper` `#F3F4F1` — a cool, near-white background
  and deep navy-black ink, not warm cream-on-cream.
- `accent` `#1B6E7A` — a deep teal, evokes "scanner/sensor" rather
  than generic corporate blue.
- `signal-pass` `#1F7A4D` / `signal-fail` `#C1432E` — these aren't
  decorative brand colors. They do real semantic work: every evidence
  row's pass/fail state uses them, mirroring how `Evidence.passed`
  works in the backend domain model.

**Type**: Space Grotesk (display, geometric/technical) + IBM Plex Sans
(body, engineering heritage) + IBM Plex Mono (evidence values —
criterion/found/expected are typeset as data, because that's what
they are).

**Signature element — the ink-stamp badge** (`components/ui/
stamp-badge.tsx`, `.stamp` / `.stamp-pass` / `.stamp-fail` in
globals.css): every piece of evidence gets a rotated, bordered PASS/
FAIL stamp instead of a generic colored pill. This is the one
deliberate, justified risk — a rounded pill would be safer and more
generic; the stamp motif directly embodies "every claim here is
certified by evidence," which is the product's actual value
proposition, not just a stylistic flourish.

**The verdict gauge** (`components/analysis/verdict-gauge.tsx`): a
hand-built semicircular analog meter with tick marks and a sweeping
needle, not a `recharts` donut chart. An analog meter is the more
specific choice for an "instrument panel" — the needle position and
tick marks communicate the score the way a real measuring device
would, and it's rendered as a single self-contained SVG (score number
and label included as `<text>` elements) rather than HTML overlaid on
top of it, so it stays correctly proportioned at any size.

**Motion**: minimal and purposeful — the gauge needle sweeps in on
load, evidence rows stagger in (40ms apart) like items being checked
off a list, stamp badges scale in with a slight overshoot. All of it
respects `prefers-reduced-motion` (see the media query at the top of
`globals.css`), collapsing to instant/no animation for anyone who's
set that preference.

## Verified, not assumed

This design was checked against actual rendered output, not just
written and shipped:
1. Full `tsc --noEmit`, `eslint`, and `next build` all pass with zero
   errors (see frontend/README.md for the two real toolchain bugs
   found and fixed along the way).
2. A Playwright script drove the **real product flow** end to end —
   register → upload a real `.docx` → run a real analysis against the
   real backend → expand the evidence ledger — and captured
   screenshots at each step, which were reviewed directly.
3. One real bug was caught and fixed this way: the verdict gauge
   originally overlaid HTML text on the SVG using a negative-margin
   hack (`-mt-6`), which is fragile across viewport widths and font-
   load timing. Rebuilt to render the score/label as SVG `<text>`
   instead — simpler and robust by construction.
