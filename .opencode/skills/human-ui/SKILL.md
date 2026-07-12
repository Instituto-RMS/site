---
name: human-ui
description: Use when creating, replicating, or refining web and app interfaces where visual direction, product archetypes, brand fidelity, responsive behavior, or a non-generic human finish materially affects the result.
---

<human-ui>
  <mission>
    Build the interface, not a design lecture. Read the product, resolve material unknowns, select a visual grammar from evidence, implement in the existing stack, inspect the rendered result, and explain the final decisions precisely.
  </mission>

  <core-contract>
    - Explicit requirements, reference fidelity, accessibility, domain safety, and an existing design system outrank every archetype.
    - Preserve working behavior, product language, brand, content intent, and unrelated user changes unless structural change is explicit.
    - Human character comes from meaningful composition, rhythm, and at most one authored gesture. Never impose universal radius, shadow, gradient, texture, font, density, card, or motion minimums.
    - Inspect code and the rendered surface before modifying an existing UI. Render and compare before completion.
    - Report only references actually opened, decisions actually applied, and behavioral or visual changes actually verified.
  </core-contract>

  <task-model>
    - `act`: create | modify
    - `source`: brief | image-reference | existing-ui
    - `fidelity`: exact | adapted | open
    - `surface`: target screen or flow
    - `audience`: primary user
    - `primary-archetype`: exactly one when direction is classified; inherited or not reclassified for a local repair
    - `secondary-archetypes`: zero to two, each with bounded ownership
    - `style`: one when direction is classified; inherited or not reclassified for a local repair
    - `domains`: relevant semantic and safety overlays
    - `dna`: zero to two signature capsules
    - `invariants`: behavior, brand, language, content, accessibility, technology
    - `signature-move`: zero or one product-specific recurring gesture
    - `motion`: none | functional | expressive
    - `change-scope`: repair | refine | reimagine
  </task-model>

  <workflow>
    <checkpoint-observe>
      1. Read the prompt, product description, supplied context, previous answers, image references, existing UI, and project evidence.
      2. For existing projects, locate tokens, shared components, breakpoints, assets, routes, interaction states, copy language, and current behavior.
      3. Mark every conclusion as observed, user-confirmed, or inferred. Never silently promote an inference into fact.

      <infer-product>
        - primary user and immediate job
        - dominant content and primary action
        - conversion or completion goal
        - critical states, trust level, urgency, density, and motion needs
        - brand, language, behavior, content, accessibility, and technical invariants
      </infer-product>

      <jump-points-observe>
        - Existing UI: inspect and render before proposing meaningful changes.
        - Image reference with unclear fidelity: resolve exact replication versus adapted interpretation before implementation.
      </jump-points-observe>
    </checkpoint-observe>

    <checkpoint-resolve-context>
      Combine prompt, product description, supplied context, questionnaire answers, inspected evidence, and user corrections into product hypotheses.

      <materiality-test>
        Would a different answer materially change hierarchy, conversion, trust, content, behavior, visual direction, or what must be preserved?
      </materiality-test>

      <question-policy>
        - If yes and evidence does not answer it, stop before meaningful implementation and ask one focused question generated from the actual gap.
        - Do not use a fixed questionnaire.
        - State in one short clause which design decision the answer unlocks.
        - Ask product and outcome questions before aesthetic controls.
        - Use product vocabulary. Offer contextual options only when they reduce effort or ambiguity.
        - Never ask what code, content, UI, references, or prior answers already reveal.
        - Ask one material question at a time, then recompute remaining gaps from the answer.
      </question-policy>

      <jump-points-context>
        - No material gap: continue without asking.
        - Local repair that cannot alter product intent: proceed without a product question.
        - New material gap found later: return here before deciding.
      </jump-points-context>
    </checkpoint-resolve-context>

    <checkpoint-classify-load>
      1. For create, reimagine, or meaningful refinement, read `references/catalog.md` after material context is resolved.
      2. Infer the smallest coherent blend from all evidence, not from prompt keywords alone.
      3. Load only selected reference files after the catalog. A local repair with unchanged direction may skip this checkpoint.

      <selection-contract>
        - Primary archetype: exactly one; owns shell, hierarchy, and main interaction.
        - Secondary archetypes: zero to two; each owns one named region, capability, or flow; record `none` when empty.
        - Style: exactly one; guides relationships and tone without replacing brand tokens.
        - Domains: all relevant overlays; add semantics, trust, formatting, and safety, never aesthetics alone; record `none` when empty.
        - DNA: zero to two; each adds one recognizable behavior or treatment to a bounded region; record `none` when empty.
      </selection-contract>

      <reference-record>
        For every loaded reference file, record path, role, selection evidence, owned surface, and concrete influence. Record the catalog as a routing reference when opened. Never report a reference that was not opened.
      </reference-record>

      <jump-points-reference>
        - Reference conflicts with design system: keep the design system; use the reference only for unresolved decisions.
        - Three archetypes appear equally important: choose the shell owner as primary; demote or discard the others.
      </jump-points-reference>
    </checkpoint-classify-load>

    <checkpoint-design-system>
      Search for documented design-system files and undocumented system evidence: tokens, themes, typography, shared components, icons, spacing, motion, content rules, and component states.

      <design-system-policy>
        <existing-design-system>
          - Treat it as a high-priority invariant unless redesign or migration is explicit.
          - Adapt archetypes, styles, domains, and DNA to it. Do not abruptly reskin the product.
          - Preserve document language, UI language, token names, terminology, and component conventions. Never translate them to English because this skill is written in English.
          - During every implementation iteration, update the design-system file with only decisions and components actually changed in that iteration.
        </existing-design-system>

        <implicit-design-system>
          - Treat repeated product patterns as an implicit design system and preserve them.
          - Use those patterns as the baseline if documentation is later created.
        </implicit-design-system>

        <missing-design-system>
          - Use resolved direction, selected references, accessibility needs, and project constraints as the working system.
          - If requested at any point before the final report, create a Markdown design-system file during the task.
          - If not requested, implement and verify first; then ask once in the final response whether to persist it.
          - After explicit consent, follow project documentation conventions. If none exist, create `docs/design-system.md`.
          - If the user declines, do not create the file or ask again during the same task.
          - Write it in the product language, or the user's language for a new product. Do not default to English.
        </missing-design-system>
      </design-system-policy>

      <design-system-document>
        - product principles and audience
        - reference blend with ownership
        - color and surface tokens
        - typography roles, scale, weights, and rhythm
        - spacing, grid, density, radius, border, and elevation
        - icons, imagery, and data visualization
        - CTA, forms, signup, navigation, feedback, and states
        - motion, responsive behavior, accessibility, and content language
        - iteration notes containing only implemented changes
      </design-system-document>

      <jump-points-design-system>
        - Existing system lacks a needed rule: extend it minimally in its current language and grammar.
        - Existing design-system file: after every implementation iteration, reconcile and update affected sections plus iteration notes using only implemented changes.
      </jump-points-design-system>
    </checkpoint-design-system>

    <checkpoint-compose>
      Create a compact direction record before implementation.

      <precedence>
        1. accessibility, semantics, and domain safety
        2. explicit request, image fidelity, existing design system, and product language
        3. confirmed product context and invariants
        4. domain overlays
        5. primary archetype
        6. bounded secondary archetypes
        7. style and DNA for unresolved details
      </precedence>

      <direction-record>
        - evidence and resolved context
        - primary archetype and shell ownership
        - secondary archetypes and bounded ownership
        - style, domains, DNA, and loaded reference paths
        - product-specific promise
        - preserved invariants
        - planned typography, CTA, signup, interaction, and content decisions
        - signature move, or explicit none
      </direction-record>

      <modification-scope>
        Classify modification as repair, refine, or reimagine. Default vague requests such as “improve” to repair or restrained refinement, never reimagine.
      </modification-scope>
    </checkpoint-compose>

    <checkpoint-build>
      <build-contract>
        - Use project framework, components, dependencies, icon family, fonts, and conventions.
        - Implement responsive content priority and keyboard, focus, hover, active, disabled, and touch behavior.
        - Implement relevant loading, empty, error, success, and permission states.
        - Use domain-correct content and reduced-motion behavior.
        - Do not introduce a new UI library, icon family, font, or animation dependency when a viable one exists.
        - Typography, CTA, signup, and content changes must serve the confirmed product task, not visual novelty.
      </build-contract>

      <jump-points-build>
        - New material product gap: return to `checkpoint-resolve-context`.
        - Existing design-system file: update affected sections and iteration notes before starting another implementation iteration.
      </jump-points-build>
    </checkpoint-build>

    <checkpoint-render-critique-refine>
      1. Run the UI and inspect target breakpoints and interactive states.
      2. For image replication, compare at matching dimensions.
      3. For modification, compare before and after on the same route and viewport.

      <critique-order>
        1. task clarity and primary action
        2. hierarchy and composition
        3. responsive behavior and states
        4. typography and content rhythm
        5. CTA, signup, forms, trust, and completion friction
        6. color, surfaces, imagery, icons, and data presentation
        7. motion, accessibility, and technical integrity
      </critique-order>

      <refinement-contract>
        Fix visible weaknesses before decoration. Remove generic filler, repeated card treatments, meaningless effects, and arbitrary inconsistency.
      </refinement-contract>

      <jump-points-critique>
        - Critique changes direction rather than execution quality: return to `checkpoint-compose`, update the system record, then rebuild.
      </jump-points-critique>
    </checkpoint-render-critique-refine>

    <checkpoint-report>
      <evidence-gate>
        - Source claims require source or diff evidence.
        - Visual claims require rendered inspection at the reported viewport.
        - Interaction claims require runtime interaction or an appropriate passing test.
        - Accessibility claims require the relevant keyboard, semantic, contrast, screen-reader, or automated check.
        - Product-result claims describe delivered capability only. Never claim conversion, usability, or business improvement without measurement.
        - If a category was untouched, say “unchanged” or “not applicable” instead of inventing work.
      </evidence-gate>

      <final-report-contract>
        <outcome-summary>Explain what changed and what capability the implementation now provides. Do not present unmeasured impact as fact.</outcome-summary>
        <used-references>List every loaded path, including the catalog when opened. For each: role, selection evidence, owned surface, and exact influence. Separate routing catalog, primary archetype, secondary archetypes, style, domains, and DNA.</used-references>
        <direction-summary>Name primary archetype; each secondary and its bounded ownership; style; domains; DNA; signature move or none; and preserved invariants. For a local repair that skipped classification, explicitly state inherited direction or `not reclassified` instead of inventing a blend.</direction-summary>
        <implemented-changes>
          <typography-changes>Families, roles, scale, weights, line-height, rhythm, and why. Mark unchanged when applicable.</typography-changes>
          <cta-changes>Copy, hierarchy, placement, prominence, states, and conversion rationale. Mark unchanged when applicable.</cta-changes>
          <signup-changes>Entry point, fields, steps, validation, friction, trust cues, success and error states, and why. Mark not applicable when absent.</signup-changes>
          <domain-changes>Domain language, formatting, trust, safety, privacy, and regulatory decisions.</domain-changes>
          <dna-changes>Map each DNA capsule to the exact component or region where it appears.</dna-changes>
          <system-changes>Color, surfaces, spacing, density, grid, radius, borders, elevation, icons, imagery, motion, responsiveness, accessibility, and component states.</system-changes>
          <subtle-changes>For each subtle refinement, state before, after, and perceptual or usability reason.</subtle-changes>
        </implemented-changes>
        <preservation-summary>State what intentionally remained unchanged and why.</preservation-summary>
        <design-system-status>State found, implicit, created, updated, absent, or awaiting consent; include path and exact sections changed.</design-system-status>
        <verification-summary>State routes, viewports, interactions, accessibility paths, and technical checks actually inspected.</verification-summary>
      </final-report-contract>

      <jump-points-report>
        - No design-system file and none requested before this report: end with one direct question asking whether to create the Markdown file from the implemented direction.
        - User answers yes: create it, verify it reflects implementation, then report path and sections.
        - User answers no: leave it absent and do not ask again during this task.
      </jump-points-report>
    </checkpoint-report>
  </workflow>

  <reference-library>
    <direction-catalog>
      `references/catalog.md` — read after context resolution for every create or meaningful refinement task.
    </direction-catalog>

    <product-archetypes>
      - `landing-story`: `references/archetype-landing-story.md`
      - `publication`: `references/archetype-publication.md`
      - `dashboard`: `references/archetype-dashboard.md`
      - `workspace`: `references/archetype-workspace.md`
      - `catalog`: `references/archetype-catalog.md`
      - `search-discovery`: `references/archetype-search-discovery.md`
      - `conversation`: `references/archetype-conversation.md`
      - `guided-flow`: `references/archetype-guided-flow.md`
      - `live-tracking`: `references/archetype-live-tracking.md`
      - `media-experience`: `references/archetype-media-experience.md`
    </product-archetypes>

    <styles>
      - `restrained-premium`: `references/style-restrained-premium.md`
      - `editorial-humanist`: `references/style-editorial-humanist.md`
      - `friendly-soft`: `references/style-friendly-soft.md`
      - `technical-dense`: `references/style-technical-dense.md`
      - `immersive-cinematic`: `references/style-immersive-cinematic.md`
      - `expressive-raw`: `references/style-expressive-raw.md`
    </styles>

    <domains>
      - `finance`: `references/domain-finance.md`
      - `health-medication`: `references/domain-health-medication.md`
      - `travel-hospitality`: `references/domain-travel-hospitality.md`
      - `food-service`: `references/domain-food-service.md`
      - `pet-care`: `references/domain-pet-care.md`
      - `mobility-logistics`: `references/domain-mobility-logistics.md`
      - `media-entertainment`: `references/domain-media-entertainment.md`
    </domains>

    <dna-libraries>
      - `surfaces`: `references/dna-surfaces.md`
      - `composition`: `references/dna-composition.md`
      - `motion`: `references/dna-motion.md`
    </dna-libraries>

    <video-source-map>
      `references/video-source-map.md` — load only while maintaining this skill or re-deriving DNA from source media.
    </video-source-map>
  </reference-library>

  <red-flags>
    - Choosing references from sector words without reading product evidence.
    - Reporting references that were not opened or changes that were not verified.
    - Letting secondary archetypes compete with the primary shell.
    - Using domain as a visual preset rather than a semantic and trust overlay.
    - Replacing an existing design system, language, or brand during a vague “improve” request.
    - Updating design-system documentation with intended work that was not implemented.
    - Creating a generic design-system file without consent when none was requested.
    - Explaining aesthetics while omitting CTA, signup, states, responsiveness, accessibility, or runtime evidence.
  </red-flags>

  <completion-gate>
    - Material product gaps resolved before meaningful implementation.
    - Catalog, when opened, recorded as a routing reference. Only selected archetype, style, domain, and DNA files loaded and applied with bounded ownership.
    - Existing design system and product language preserved or explicitly changed by request.
    - Every implementation iteration reconciled and updated an existing design-system file with affected sections and actual iteration notes.
    - Rendered result inspected at relevant breakpoints and states.
    - Final report names references, archetypes, styles, domains, DNA, typography, CTA, signup, subtle changes, preservation, design-system status, and verification with evidence.
  </completion-gate>
</human-ui>
