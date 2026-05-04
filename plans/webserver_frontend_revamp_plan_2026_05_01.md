# Webserver Frontend Revamp Plan

Date: 2026-05-01
Status: Proposed
Recommendation: Proceed with a visual refresh, not a structural rewrite
Primary surface: `webserver/templates/explore.html`

## Objective

Make the app feel more fun, fresher, and more intentional while keeping its strongest trait: fast scanning of lots of parts.

This plan assumes we keep the current Flask + server-rendered architecture, preserve taxonomy-first browsing, and improve the product through a focused UI system refresh rather than a framework migration.

## Current State Snapshot

Based on the current templates, stylesheet, and saved explore screenshots:

- The app already has a solid information architecture and useful density.
- The current visual tone is competent but restrained: dark utility sidebar, pale glass panels, muted earthy accents.
- The explore page is functional, but the emotional tone still leans "internal tool" more than "maker studio" or "fun catalog browser".
- The app uses large hero space for a fairly small amount of useful content.
- The row layout works well, but the actions, chips, and counts still feel generic rather than distinctive.
- The taxonomy area is useful, though visually separate from the rest of the browse flow.
- The add-item and detail pages are consistent, but they do not yet feel like part of a memorable visual system.

## Recommended Direction

### Direction Name

Maker Console

### Direction Summary

Keep the app desktop-efficient and browse-first, but shift the visual language toward a brighter workshop/catalog experience:

- warmer and more energetic color
- stronger typography hierarchy
- more personality in chips, counts, and empty states
- tighter action surfaces
- subtle motion and depth used with restraint

This should feel closer to a joyful inventory tool than a soft enterprise dashboard.

## Research Synthesis

Research was reviewed on 2026-05-01 with an emphasis on current 2025-2026 product UI signals and practical app-home patterns.

| Source | Signal | Implication for this app |
| --- | --- | --- |
| Shopify App Home guidance | Home pages should provide daily value, status updates, immediate actions, and clear CTAs | Make the top of explore more actionable and less decorative |
| Figma Config 2025 | Dense surfaces can still feel expressive when color and type are intentional | Use stronger display typography and a clearer tokenized color system |
| Apple Liquid Glass rollout, June 9 2025 | Expressive translucency is back, but content should stay central | Keep layered surfaces only where they improve focus, not everywhere |
| Atlassian lozenge guidance | Status indicators should support quick recognition | Upgrade metadata pills and taxonomy chips into a more purposeful status language |
| Atlassian empty-state guidance | Empty states can add energy, but copy must stay short and scannable | Make no-results and sparse states feel supportive rather than flat |
| Webflow 2025 trend roundup | Glows, depth, microinteractions, and futuristic accents are current, but should guide attention | Add selective hover glow, stronger focus states, and a few controlled motion cues |

## Design Principles

1. Keep scanning speed sacred.
2. Spend the visual budget on meaning, not decoration.
3. Make taxonomy feel like a first-class navigation system.
4. Let color encode structure, not just style.
5. Use "fun" as energy and friendliness, not clutter.
6. Make the app feel crafted on desktop first, then collapse gracefully for mobile.

## What To Keep

- Server-rendered templates
- Dense result rows instead of card grids
- Sticky left navigation
- Live client-side search filtering
- Taxonomy-first navigation model
- Image-first identification for parts where thumbnails are meaningful

## What To Change

### 1. Visual Identity

- Replace the current muted moss/brass palette with a brighter workshop palette.
- Introduce clearer accent roles:
  - primary action
  - taxonomy depth
  - success/info/warning
  - preview/image surfaces
- Swap the current "soft frosted everywhere" feel for a mixed system:
  - crisp solid surfaces for utility zones
  - translucent layers only in hero/tool areas
- Give the product a more ownable typographic voice.

### 2. Explore Header

- Reduce vertical hero height.
- Turn the header into a high-value command zone.
- Surface:
  - page purpose
  - current taxonomy path
  - visible and cached counts
  - search and sort
  - one clearly dominant primary action
- Consider a compact "Today in cache" or "Active source" summary if useful.

### 3. Taxonomy Navigation

- Integrate selected taxonomy chips more tightly with search.
- Make branch options look like an interactive filter rail, not a separate block.
- Use depth-aware color or border treatment consistently.
- Keep counts prominent.
- Preserve collapse state, but make the open/closed affordance cleaner and more modern.

### 4. Results Rows

- Keep long horizontal rows.
- Increase contrast between preview, identity, metadata, and actions.
- Make titles feel more editorial and less default UI.
- Promote the most useful metadata and demote the rest.
- Add stronger hover/keyboard-focus treatment.
- Consider optional row variants:
  - featured row for exact search hits
  - standard row for normal browse mode

### 5. Detail Page

- Reuse the new color and spacing system from explore.
- Strengthen the preview area so it feels more like a "workbench" than a plain panel.
- Make the file inventory easier to skim with better grouping, icons, or status pills.
- Give manual attributes and YAML sections clearer hierarchy.

### 6. Add Item Page

- Make form selection and data entry feel simpler and more guided.
- Improve spacing rhythm and section framing.
- Add stronger field grouping and focus states.
- Keep the workflow quick rather than ornamental.

## Suggested Visual System

### Palette Direction

Recommended mood:

- warm off-white or light sand base
- deep ink/navy for structure
- bright citrus or flame accent for primary actions
- teal or cobalt accent for browse/search states
- taxonomy hues that step by depth without turning rainbow-chaotic

### Typography Direction

- Keep a practical body font.
- Use a more expressive condensed or industrial-feeling display face for headings.
- Let headings do more of the personality work so the rest of the UI can stay disciplined.

### Motion Direction

- Add short hover lift on rows and buttons
- Add subtle reveal/fade on page load for top-level sections
- Add stronger focus/selection transitions on chips and taxonomy options
- Avoid constant animation, parallax, or anything that slows scanning

### Surface Direction

- Solid side navigation
- Crisp bordered rows
- Tinted chips and badges
- One or two translucent/highlighted surfaces near the top
- More texture and depth in the background, less blur-heavy everywhere

## Implementation Plan

## Phase 0: Baseline And Moodboards

Status: Not started

- [ ] Capture fresh screenshots of `explore`, `part_detail`, and `add_item`
- [ ] Collect 2-3 reference directions for typography, color, and motion
- [ ] Pick one final visual route before coding
- [ ] Write down token goals before editing CSS

Acceptance criteria:

- We have a single chosen design direction
- The revamp is aligned before implementation starts

## Phase 1: Token Refresh

Status: Not started

- [ ] Redesign `:root` tokens in `webserver/static/style.css`
- [ ] Add semantic tokens for primary action, taxonomy depth, status, and focus
- [ ] Define a tighter spacing scale for dense screens
- [ ] Define typography roles for display, section, body, meta, and code

Acceptance criteria:

- Color and spacing decisions are centralized
- Explore, detail, and add-item can share the same visual language

## Phase 2: Shared Chrome Refresh

Status: Not started

- [ ] Refresh `webserver/templates/base.html`
- [ ] Update sidebar hierarchy and nav/button styling
- [ ] Rework sticky top bar for clearer page context
- [ ] Improve flashed-message styling and placement

Acceptance criteria:

- Global chrome already feels refreshed before page-specific work starts

## Phase 3: Explore Page Revamp

Status: Not started

- [ ] Reduce hero height and turn it into a compact control deck
- [ ] Redesign search, sort, and count modules
- [ ] Rework taxonomy into a denser filter/navigation band
- [ ] Restyle results rows with stronger structure and better emphasis
- [ ] Improve no-results messaging and empty-state tone

Acceptance criteria:

- Explore feels notably fresher without losing density
- More useful information appears above the fold

## Phase 4: Detail Page Revamp

Status: Not started

- [ ] Refresh `webserver/templates/part_detail.html`
- [ ] Strengthen preview framing and metadata hierarchy
- [ ] Improve file inventory readability
- [ ] Bring manual attribute editing into the new system
- [ ] Refresh YAML/code block presentation

Acceptance criteria:

- Detail page clearly belongs to the same product as explore

## Phase 5: Add Item Flow Revamp

Status: Not started

- [ ] Refresh `webserver/templates/add_item.html`
- [ ] Improve form hierarchy and field spacing
- [ ] Add more deliberate call-to-action treatment
- [ ] Improve form affordances and helper text styling

Acceptance criteria:

- Data entry feels calmer and quicker
- The form no longer looks like a secondary page

## Phase 6: Motion And Polish

Status: Not started

- [ ] Add restrained motion to rows, chips, panels, and header elements
- [ ] Refine hover, active, and focus states
- [ ] Tune image-preview interactions so they feel more intentional
- [ ] Remove any decorative treatment that hurts clarity

Acceptance criteria:

- The UI feels alive, but never busy

## Phase 7: Responsive Pass And Verification

Status: Not started

- [ ] Review at desktop width
- [ ] Review at tablet width
- [ ] Review at mobile width
- [ ] Run the existing test suite
- [ ] Capture after screenshots
- [ ] Update `webserver/README.md` if behavior or UI conventions changed materially

Acceptance criteria:

- The refresh works across supported sizes
- No existing flows regress

## Priority Order

1. Token refresh
2. Shared chrome
3. Explore page
4. Detail page
5. Add item page
6. Motion and polish
7. Responsive verification

## Risks And Guardrails

| Risk | Why it matters | Guardrail |
| --- | --- | --- |
| Too much "fun" hurts usability | This app is still a productivity tool | Keep rows dense and action-first |
| Too much translucency reduces readability | The current app already uses several layered surfaces | Limit glass effects to top-level surfaces |
| Color overuse weakens taxonomy meaning | Everything cannot be accent-colored | Reserve strong hues for status, actions, and taxonomy cues |
| Typography becomes quirky instead of useful | Explore is text-heavy | Use expressive display type only for headings and hero labels |
| Mobile layout regresses | Dense desktop layouts collapse badly if not reviewed | Treat responsive cleanup as a required phase, not a nice-to-have |

## Success Criteria

- The app feels noticeably more modern on first load
- Explore feels faster to read, not slower
- The UI has more personality without becoming noisy
- Actions are clearer and more inviting
- Taxonomy navigation feels integrated instead of bolted on
- Detail and add-item pages match the same visual system

## Status Tracker

| Workstream | Status | Owner | Notes |
| --- | --- | --- | --- |
| Baseline and references | Not started | Unassigned | Fresh screenshots and reference set still needed |
| Design tokens | Not started | Unassigned | CSS token pass will set the direction |
| Shared chrome | Not started | Unassigned | Sidebar and top bar |
| Explore refresh | Not started | Unassigned | Highest-value phase |
| Detail refresh | Not started | Unassigned | Should follow explore patterns |
| Add-item refresh | Not started | Unassigned | Form polish and hierarchy |
| Motion and polish | Not started | Unassigned | Only after layout is stable |
| Verification | Not started | Unassigned | Screenshots, tests, responsive pass |

## Progress Log

| Date | Area | Update | Result |
| --- | --- | --- | --- |
| 2026-05-01 | Audit | Reviewed current templates, CSS, JS, and saved screenshots | Baseline captured |
| 2026-05-01 | Research | Reviewed current design-system and trend references | Direction selected: Maker Console |
| 2026-05-01 | Planning | Created frontend revamp plan with phased tracking | Ready for implementation |

## References

- Shopify App Home page guidance: https://shopify.dev/docs/apps/design/user-experience/app-home-page
- Figma Config 2025 visual identity notes: https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/
- Apple tvOS 26 redesign notes, published June 9, 2025: https://www.apple.com/newsroom/2025/06/apple-tv-brings-a-beautiful-redesign-and-enhanced-home-entertainment-experience/
- Atlassian lozenge component: https://atlassian.design/components/lozenge
- Atlassian empty-state guidance: https://atlassian.design/foundations/content/designing-messages/empty-state
- Webflow 2025 design trends roundup: https://webflow.com/blog/web-design-trends-2025
