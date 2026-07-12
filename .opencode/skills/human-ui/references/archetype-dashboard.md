---
id: dashboard
kind: archetype
summary: Turn changing data into decisions and drill-down paths.
signals: [metrics, analytics, reporting, monitoring, executive]
variants: [operational, analytical, executive, financial]
compatible: [workspace, live-tracking, publication]
---

# Dashboard

## Structural contract

Own decision hierarchy: what changed, whether it matters, why, and where to investigate. Give one decision-critical region priority; keep supporting metrics comparable. Trends must encode domain meaning, not arithmetic alone.

## Required states

Cover loading, partial data, stale data, empty ranges, errors, permissions, export, and dense mobile fallback. Use stable numeric alignment and explicit units.

## Blend contract

Pair with `workspace` when users act on findings and `live-tracking` when state changes continuously. `technical-dense` increases information density; `restrained-premium` increases calm and executive authority.

## Anti-patterns

Avoid KPI-card wallpaper, decorative charts, green-up/red-down shortcuts, animation that implies unstable values, and visual hierarchy based only on card size.
