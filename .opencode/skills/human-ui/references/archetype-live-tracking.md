---
id: live-tracking
kind: archetype
summary: Make changing location or system state trustworthy.
signals: [map, eta, delivery, dispatch, realtime, tracking]
variants: [location, delivery, dispatch, system-status]
compatible: [dashboard, workspace, guided-flow]
---

# Live Tracking

## Structural contract

Own current state, next expected event, time estimate, source freshness, and exceptions. Separate live evidence from prediction. Maps or timelines support status; they do not replace it.

## Required states

Cover acquiring signal, delayed updates, stale data, offline, permission denied, rerouting, cancellation, completion, and unknown ETA. Communicate whether the system is waiting or broken.

## Blend contract

Use `dashboard` for fleet or aggregate monitoring, `workspace` for dispatch actions, and `guided-flow` for booking or issue resolution.

## Anti-patterns

Avoid fake continuous motion, unlabeled pulsing indicators, exact-looking estimates without confidence, map-first layouts with inaccessible status, and color as the only state signal.
