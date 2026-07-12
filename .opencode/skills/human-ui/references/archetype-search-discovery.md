---
id: search-discovery
kind: archetype
summary: Help users express intent, explore, compare, and recover.
signals: [search, filter, compare, recommendation, explore]
variants: [direct-search, faceted, exploratory, comparator]
compatible: [catalog, publication, landing-story, media-experience]
---

# Search Discovery

## Structural contract

Own query expression, filter visibility, result confidence, comparison, and recovery. Distinguish active constraints from available ones. Preserve context when opening and returning from a result.

## Required states

Cover initial, loading, partial, no-result, corrected-query, offline, and error states. No-result states must explain what happened and offer a useful next move.

## Blend contract

As secondary, add a bounded discovery region without taking over the host shell. Pair with `catalog`, `publication`, or `media-experience` according to result content.

## Anti-patterns

Avoid giant search bars without information architecture, hidden active filters, generic spinners, destructive filter resets, and result cards whose visual weight obscures relevance.
