---
id: guided-flow
kind: archetype
summary: Complete a bounded multi-step task with confidence.
signals: [onboarding, booking, checkout, application, upload]
variants: [booking, checkout, setup, application]
compatible: [catalog, search-discovery, landing-story, workspace]
---

# Guided Flow

## Structural contract

Own progress, current step, validation, review, primary action, and recovery. Ask only for information needed at the current stage. Make consequences and commitments explicit.

## Required states

Cover inline validation, server errors, back navigation, resumability, optional steps, loading, confirmation, cancellation, and narrow screens. Preserve entered data whenever safe.

## Blend contract

As primary, own the full task. As secondary, occupy one bounded region inside a catalog, workspace, or landing story. Domain overlays determine legal, safety, and payment language.

## Anti-patterns

Avoid decorative split screens that weaken form focus, progress indicators unrelated to real steps, disabled actions without explanation, surprise totals, and motion that makes the flow feel slower.
