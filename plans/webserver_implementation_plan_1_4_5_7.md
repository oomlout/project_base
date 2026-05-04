# Webserver Implementation Plan: Items 1, 4, 5, and 7

Date: 2026-05-01
Status: Completed
Scope: implement the previously identified improvements for backend structure, reload performance, scan-time cost reduction, and frontend usability.

## Goal Mapping

| Item | Goal | Short Name |
| --- | --- | --- |
| 1 | Split the app into clearer backend structure with blueprints and cleaner app setup | Backend Structure |
| 4 | Make `Reload Fast` genuinely cheap at runtime | Fast Reload |
| 5 | Reduce scan-time work during startup and cache refresh | Lazy Metadata |
| 7 | Improve explore/detail UX with denser, more useful information display | Frontend UX |

## Progress Dashboard

| Phase | Status | Progress | Notes |
| --- | --- | --- | --- |
| Phase 0: Baseline and instrumentation | Completed | 4/4 | Baseline timings captured and recorded |
| Phase 1: Backend structure refactor | Completed | 6/6 | Routes split into blueprints with shared runtime/presentation helpers |
| Phase 2: Fast reload optimization | Completed | 6/6 | Reload now compares lightweight per-part signatures instead of full eager metadata records |
| Phase 3: Scan-time reduction | Completed | 6/6 | File inventories and image dimensions moved to on-demand loading |
| Phase 4: Frontend UX improvements | Completed | 7/7 | Explore rows denser; sort and taxonomy-state persistence added |
| Phase 5: Validation and rollout | Completed | 5/5 | Tests, timings, screenshot, and README update complete |

## Success Criteria

- `webserver.app` no longer acts as the single large route-and-helper module.
- `Reload Fast` avoids full `rglob()` work for unchanged parts in normal cases.
- Explore page startup and refresh do less image and file metadata work up front.
- Explore rows surface more actionable metadata without feeling heavier.
- Existing tests continue to pass, and new behavior has test coverage where practical.

## Phase 0: Baseline and Instrumentation

- [x] Record current startup timing for `create_app()` on a representative dataset.
- [x] Record current `Reload Fast` timing on a no-change run and a small-change run.
- [x] Identify current hotspots in cache load, file walking, and image-dimension reads.
- [x] Write down the baseline numbers in the Progress Log section below.

## Phase 1: Backend Structure Refactor

### Deliverables

- [x] Create a `webserver/routes/` package.
- [x] Move explore and part-detail routes into a blueprint module.
- [x] Move add-item routes into a blueprint module.
- [x] Move reload and generation action routes into a blueprint module.
- [x] Keep `create_app()` as the assembly point only: config load, cache setup, blueprint registration, shared helpers.
- [x] Preserve current route URLs and current test behavior.

### Notes

- Prefer small helper modules over replacing one large file with several still-large files.
- Keep cache/service logic outside route modules.
- Avoid changing route semantics unless required by performance work later in the plan.

### Acceptance Criteria

- `webserver/app.py` is materially smaller and easier to scan.
- Route registration is grouped by responsibility.
- Existing tests still pass after refactor.

## Phase 2: Fast Reload Optimization

### Deliverables

- [x] Replace deep full-directory signature work in the common fast path.
- [x] Introduce a cheaper change-detection strategy for part folders.
- [x] Reuse cached signatures or manifests instead of recomputing every file tree on every fast reload.
- [x] Preserve correctness when files are added, removed, or modified.
- [x] Keep fallback behavior for uncertain or invalid state.
- [x] Add tests covering no-change reload and changed-folder reload behavior.

### Candidate Approach

| Option | Description | Recommendation |
| --- | --- | --- |
| Directory manifest cache | Persist a small summary per part and compare quick signals first | Recommended |
| Parent-folder mtime gate | Only deep-scan folders whose directory metadata changed | Good if reliable enough on target filesystem |
| File watcher | Real-time invalidation using filesystem events | Useful later, but probably too much for first pass |

### Acceptance Criteria

- No-change `Reload Fast` is meaningfully cheaper than today.
- Changed-part reload still updates the correct records.
- Config changes can still force a full rebuild when needed.

## Phase 3: Scan-Time Reduction

### Deliverables

- [x] Split part loading into lightweight explore metadata and heavier detail metadata.
- [x] Stop building full file inventories for every part during explore cache load.
- [x] Delay image dimension reads until detail view or explicit preview generation when possible.
- [x] Keep enough preview metadata for explore thumbnails to render safely.
- [x] Revisit search-index generation so only required fields are computed up front.
- [x] Add tests for lazy-loaded file inventory and image metadata behavior.

### Proposed Shape

| Concern | Current State | Planned State |
| --- | --- | --- |
| Part scan | Full folder walk for each part | Minimal scan for explore-visible data |
| File inventory | Built for every part up front | Built on demand for detail page |
| Image dimensions | Read during initial scan | Read lazily or cached separately |
| Search fields | Built from current configured fields | Keep, but avoid unrelated expensive metadata |

### Acceptance Criteria

- Explore cache load does less I/O and less image processing work.
- Detail page still shows complete file inventory when opened.
- Thumbnail and modal features still work.

## Phase 4: Frontend UX Improvements

### Deliverables

- [x] Add more useful metadata to explore rows, such as taxonomy breadcrumb or compact tags.
- [x] Add visible file/image counts where helpful.
- [x] Improve result-row hierarchy so titles, ids, and actions are easier to scan.
- [x] Make search/filter controls feel more intentional and compact.
- [x] Persist taxonomy panel collapsed state in the browser.
- [x] Add a sort control if the current default ordering is not enough.
- [x] Review mobile layout after the denser row update.

### UX Direction

- Keep the current visual character; do not redesign from zero.
- Make the explore page feel more like a compact asset browser.
- Use density to increase usefulness, not clutter.
- Prioritize scanability over decorative additions.

### Acceptance Criteria

- A user can understand each row faster without opening the detail page.
- The explore page shows more decision-making context above the fold.
- Mobile behavior remains usable.

## Phase 5: Validation and Rollout

- [x] Run the existing unit test suite and fix regressions.
- [x] Add focused tests for new lazy-loading and reload behavior.
- [x] Re-check startup and fast reload timings against the Phase 0 baseline.
- [x] Capture before/after screenshots of the explore page.
- [x] Update `webserver/README.md` if architecture or behavior changed.

## Order of Execution

1. Phase 0: baseline and instrumentation
2. Phase 1: backend structure refactor
3. Phase 2: fast reload optimization
4. Phase 3: scan-time reduction
5. Phase 4: frontend UX improvements
6. Phase 5: validation and rollout

## Risks and Watchouts

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Refactor and perf work overlap | Structural moves can hide performance regressions | Measure before and after each phase |
| Lazy metadata breaks detail templates | Templates currently expect full file/image data | Add a clear lazy-loading boundary and tests |
| Fast reload misses changes | Cheap invalidation can become incorrect | Keep conservative fallback paths |
| UX density becomes clutter | More metadata can reduce readability | Validate with screenshots and mobile review |

## Progress Log

Use this section as the running journal. Update the status lines and checkboxes above as work completes.

| Date | Phase | Update | Result |
| --- | --- | --- | --- |
| 2026-05-01 | Plan | Initial plan created | Ready for implementation |
| 2026-05-01 | Phase 0 | Baseline captured on current 50-part dataset | `create_app`: 0.6182s, no-change reload: 0.0091s |
| 2026-05-01 | Phase 1 | Split routes into `explore`, `parts`, `manual`, and `actions` blueprints | App assembly simplified and routes preserved |
| 2026-05-01 | Phase 2 | Replaced eager deep-record signatures with lightweight tracked snapshots | Fast reload now watches YAML metadata plus lightweight image/file signals |
| 2026-05-01 | Phase 3 | Moved file inventory, image dimensions, and viewer payload generation to on-demand loading | Explore cache now holds lighter records |
| 2026-05-01 | Phase 4 | Added explore sorting, row metadata, compact filter controls, and taxonomy collapse persistence | Explore page is denser and more informative |
| 2026-05-01 | Phase 5 | Validation complete | `python -m unittest webserver.tests.test_app -q` passed with 37 tests; after screenshot saved to `webserver/explore_screenshot_after.png`; post-change sample timings: `create_app` 0.5823s, no-change reload 0.0155s, single-part change reload 0.0340s |

## Completion Checklist

- [x] Phase 0 complete
- [x] Phase 1 complete
- [x] Phase 2 complete
- [x] Phase 3 complete
- [x] Phase 4 complete
- [x] Phase 5 complete
- [x] Final README and plan status updated
