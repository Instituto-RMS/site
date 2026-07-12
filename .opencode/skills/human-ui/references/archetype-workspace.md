---
id: workspace
kind: archetype
summary: Support repeated, stateful work with tools and context.
signals: [crud, editor, admin, settings, productivity, devtool]
variants: [editor, operations, configuration, management]
compatible: [dashboard, conversation, guided-flow, search-discovery]
---

# Workspace

## Structural contract

Own persistent navigation, work context, tool placement, selection, and save state. Optimize repeated actions and recognition. Density follows task frequency and expertise, not fashion.

## Required states

Cover unsaved changes, optimistic and failed saves, permissions, bulk actions, destructive confirmation, empty workspaces, keyboard paths, and responsive collapse. Preserve user context across navigation.

## Blend contract

Use `dashboard` for overview regions, `conversation` for collaboration, `guided-flow` for bounded setup, and `search-discovery` for large collections. Secondary archetypes must not replace the workspace shell.

## Anti-patterns

Avoid hiding frequent actions for visual purity, gratuitous dashboards, modal chains, ambiguous save behavior, and wholesale navigation rewrites during cosmetic refinement.
