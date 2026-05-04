# Plan 2: Modern Popup Image Display Plan

Date: 2026-05-01
Status: Implemented

## Progress

- [x] Review current image-serving and image-display behavior in the webserver
- [x] Research modern image display and modal/dialog practices
- [x] Draft a repo-specific UX and implementation plan
- [x] Confirm open product decisions with the user
- [x] Finalize the implementation-ready plan
- [x] Begin implementation
- [x] Add shared popup viewer
- [x] Wire explore page popup behavior
- [x] Wire detail page popup behavior
- [x] Finish tests and polish

## Goal

Replace the current image behavior that often opens a separate page with a modern popup-based experience, while also improving image performance and browsing ergonomics.

The plan should cover:

- popup image viewing instead of opening a raw image page
- modern image browsing patterns
- accessibility and keyboard support
- better image loading behavior
- fit with the existing explore/detail pages
- fit with the local derivative-cache plan from `plan_1.md`

## Current Behavior

Today the UI uses the original image route directly in several places:

- explore row preview images
- part detail primary preview
- file inventory hover previews
- the `Image` and `Open Preview` actions

Current limitations:

- clicking often navigates away or opens a raw image page
- there is no unified image viewer state
- there is no gallery flow for multiple images in one part
- image previews do not yet reflect modern loading and modal behavior
- hover preview works on desktop but is weaker on touch devices

## Research-Informed Design Principles

The following principles should shape the plan:

1. Use a semantic modal dialog instead of a hand-rolled popup container.
   Source basis: `dialog` guidance from web.dev and MDN emphasizes built-in modal semantics, focus handling, and Escape-to-close behavior.

2. Keep users in context when viewing images.
   For this app, that means opening images in-page instead of navigating to a raw asset view for normal preview interactions.

3. Use responsive image delivery instead of one-size-fits-all originals.
   Source basis: MDN and web.dev both recommend responsive images, width/height hints, and browser-guided source selection where possible.

4. Reserve layout space to avoid jank.
   Source basis: MDN and web.dev recommend width/height or aspect-ratio handling to reduce layout shift.

5. Lazy-load non-critical images, but not everything.
   Source basis: web.dev notes that overusing lazy loading can hurt performance; above-the-fold images should usually stay eager.

6. Prefer async decoding for non-critical images.
   Source basis: web.dev image-performance guidance recommends `decoding="async"` for many non-critical images.

7. Support keyboard and touch interactions as first-class behavior.
   Popup image UX should not be mouse-only.

## Recommended UX Direction

## 1. Introduce a Unified Image Viewer

Add one shared modal image viewer component that can be opened from:

- explore page thumbnail click
- explore page `Image` action
- part detail main preview click
- file inventory image click

The viewer should open in-place as a modal popup instead of navigating away.

Recommended implementation direction:

- use a shared `<dialog>` component rendered in the base layout or on relevant pages
- open it with JavaScript using `.showModal()`
- close with:
  - dedicated close button
  - `Esc`
  - backdrop click

## 2. Viewer Content Model

When the viewer opens, it should show:

- the selected image at the largest sensible display size
- part name
- file name or relative image path
- image position in the part gallery, such as `2 of 7`
- actions for:
  - next image
  - previous image
  - open original in a new tab
  - optionally download original

## 3. Gallery Behavior

For parts with multiple images, the popup should behave like a mini gallery.

Recommended behavior:

- clicking any image opens that image directly
- the popup steps through all previewable images in the current part
- left/right arrow keys move through images
- visible previous/next controls are present
- swipe support is intentionally deferred to a later phase

## 4. Mobile and Touch Behavior

Move away from hover-only affordances as the main discovery path.

Recommended behavior:

- on desktop, hover preview may remain as a lightweight secondary affordance
- on touch/mobile, tapping should open the modal viewer
- controls must be large enough for touch
- mobile phase 1 uses previous/next buttons only
- swipe gestures are deferred

## 5. Modern Display Practices To Incorporate

These should be explicitly included in the implementation plan:

### A. Responsive derivatives

Use the derivative-cache approach from `plan_1.md` to serve appropriately sized images for:

- explore thumbnails
- file inventory preview thumbnails
- modal display image

### B. Width/height or aspect-ratio reservation

Each UI slot should reserve display space before the image loads.

Targets:

- explore row preview slot
- detail preview frame
- modal image stage
- file inventory preview area

### C. Loading policy by context

Recommended defaults:

- explore images below the fold: `loading="lazy"`
- detail hero/primary preview: `loading="eager"`
- modal images: load on demand when opened
- preloading adjacent gallery images: optional phase-2 enhancement

### D. Decoding policy

Recommended defaults:

- use `decoding="async"` for explore thumbnails and non-critical previews
- modal hero image can remain browser-default or be tuned later

### E. Preserve access to originals

The popup replaces normal preview navigation, but the original file should still be available through an explicit action.

### F. Clear zoom/fit behavior

The popup should default to:

- fit-to-viewport
- preserve aspect ratio
- darkened backdrop
- no page navigation

Optional later enhancement:

- click-to-zoom or zoom toggle for close inspection

## Proposed UX for This Repo

## Explore Page

Current issue:

- clicking the preview takes the user to part detail, while the `Image` action opens the raw image

Proposed direction:

- click preview image: open popup viewer anchored to that part's image set
- `Image` action: also open the popup viewer, not a raw file
- `Open` action: keep going to part detail

Optional enhancement:

- add a subtle "expand" affordance on hover/focus to signal popup behavior

## Part Detail Page

Current issue:

- the main preview is static and `Open Preview` leaves the context

Proposed direction:

- clicking the main preview opens the popup viewer
- `Open Preview` becomes `View Image`
- file inventory image links also open the popup viewer
- raw/original access moves into a secondary action inside the popup and optionally remains in the file list

## File Inventory

Current issue:

- image hover previews are desktop-centric and image links open a new tab

Proposed direction:

- clicking an image row opens the popup viewer
- hover preview can remain on desktop, but it should no longer be the only rich preview path
- include visible image markers or badges to signal which files are popup-previewable

## Proposed UI Component Set

### Shared modal viewer

One reusable viewer component with:

- image stage
- caption/meta row
- close button
- previous/next buttons
- open-original button

### Optional thumbnail strip

For parts with several images, consider a lightweight thumbnail strip below the main image in the popup.

Recommendation:

- not required for phase 1
- useful for parts with many related images

### Empty/failure states

If a derivative fails:

- show a clean fallback state
- keep the original-image action available

## Implementation Phases

## Phase 1: Decide Interaction Contract

- define exactly which clicks open the popup
- define whether popup is modal or modeless
- define whether next/previous spans only previewable images in a part
- define whether backdrop click closes the viewer

Acceptance:

- interaction rules are explicit and stable

Locked decisions:

- popup is modal
- next/previous steps through all previewable images in the current part
- mobile phase 1 uses buttons only
- clicking the dark backdrop closes the popup

## Phase 2: Define Shared Viewer Data Model

- create a normalized image-entry shape for previewable files
- include:
  - part id
  - part name
  - relative path
  - original URL
  - derivative URL(s)
  - index within image list
  - total count

Acceptance:

- both explore and detail pages can open the same viewer with the same data shape

## Phase 3: Add Modal Viewer Component

- implement viewer markup
- add accessible labels
- wire focus management
- support Esc close
- support previous/next keyboard navigation

Acceptance:

- popup works with keyboard only
- popup does not require opening a raw image page

## Phase 4: Wire Explore Page

- preview click opens popup
- `Image` button opens popup
- leave `Open` button as the route to part detail

Acceptance:

- explore image viewing no longer requires navigation away

## Phase 5: Wire Detail Page

- primary preview opens popup
- file inventory image rows open popup
- `Open Preview` is replaced or relabeled to match popup behavior

Acceptance:

- detail-page image viewing stays in context

## Phase 6: Add Modern Loading Behavior

- integrate derivative image URLs from `plan_1.md`
- add `loading` strategy by context
- add `decoding` strategy by context
- reserve image space with width/height or aspect-ratio

Acceptance:

- image rendering is smoother and less wasteful

## Phase 7: Polish

- transition and backdrop styling
- touch-friendly controls
- consistent button naming
- optional adjacent-image prefetch for smoother gallery stepping

Acceptance:

- viewer feels intentional, modern, and fast

## Technical Design Notes

### Popup Technology Choice

Recommendation:

- prefer native `<dialog>` over a custom div-based modal

Why:

- better semantics
- built-in close affordances
- easier focus handling
- aligns with modern browser support and guidance

### Viewer State Strategy

Recommendation:

- keep a small client-side viewer controller in JavaScript
- let templates emit data attributes or a JSON blob per page

This avoids a separate fetch layer for phase 1.

### Image Sizing Tiers

Suggested initial derivative tiers:

- explore thumbnail
- file-list hover/thumb preview
- modal display image

The popup should use a higher-quality/larger derivative than list contexts, but not default to the original unless explicitly requested.

### Original File Access

Keep a clearly named action inside the popup:

- `Open Original`

This preserves power-user workflows without making the raw file the default behavior.

## Risks and Tradeoffs

- a full gallery viewer adds JS complexity
- hover preview and popup preview may overlap unless interaction rules are clear
- very large image sets may need lightweight preloading, not eager loading
- SVG files may need special-case handling if modal zooming becomes important later

## Recommended First Scope

Implement first:

1. shared modal popup using `<dialog>`
2. explore preview click opens popup
3. detail preview click opens popup
4. file inventory image click opens popup
5. previous/next image navigation within a part
6. explicit `Open Original` action
7. derivative-backed modal/list images once `plan_1.md` begins implementation

Defer until later:

1. pinch zoom
2. swipe gestures
3. thumbnail strip
4. animated zoom transitions
5. cross-part gallery navigation

## Confirmed Product Decisions

These decisions are now fixed for the first implementation pass:

1. The popup gallery steps through all previewable images in the current part.
2. Mobile phase 1 uses buttons only.
3. Clicking the dark backdrop closes the popup.

## Research Notes

The plan above was informed by these references:

- web.dev on the HTML `dialog` element: https://web.dev/learn/html/dialog
- MDN on the `<dialog>` element: https://developer.mozilla.org/docs/Web/HTML/Reference/Elements/dialog
- web.dev on responsive images: https://web.dev/learn/design/responsive-images/
- MDN on responsive images: https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
- MDN on lazy loading: https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Lazy_loading
- web.dev on image performance and decoding/loading behavior: https://web.dev/learn/performance/image-performance?hl=en
- MDN on aspect ratio and preventing layout jank: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_sizing/Aspect_ratios
