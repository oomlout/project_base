# Plan 1: Cached Image Downsampling For Webserver

Date: 2026-05-01

## Progress

- [x] Write implementation plan
- [x] Add image derivative service
- [x] Add machine-local derivative cache
- [x] Add derived image route
- [x] Wire templates to derived images
- [x] Add tests and documentation

## Goal

Improve image serving so the webserver does not always send the original full-size image.

We want:

- downsampled images for common UI uses
- cached resized outputs that can be reused on the machine serving the app
- no cached derivatives stored in git
- no cached derivatives stored in folders likely to be cloud-synced with the repo
- a design that still allows access to the original full-size file when needed

## Current State

Today the app serves images directly from the part folder through `part_file` in `webserver/app.py`.

That means:

- explore thumbnails use the original source image
- detail previews use the original source image
- file-list hover previews use the original source image
- repeated requests can cost unnecessary disk I/O, decode time, and bandwidth

## Recommended Cache Strategy

Use a machine-local cache outside the repo, preferably under Windows local app data.

Primary cache location:

- `%LOCALAPPDATA%\\project_base\\webserver_image_cache`

Why:

- not tracked by git
- not inside the project tree
- less likely to be synced by OneDrive or similar tools
- reusable across app restarts

Fallbacks if needed:

1. an explicit config override path
2. a temp/local cache path under the user profile
3. only as a last resort, a repo-local ignored cache directory

## High-Level Design

### 1. Split image serving into original vs derived use-cases

Keep the current original-file route for downloads and full-resolution viewing.

Add a separate derived-image route for resized assets, for example:

- `/parts/<part_id>/image/<path:relative_path>`

Expected query args:

- `w`: target width
- `h`: optional target height
- `fit`: optional mode such as `contain` or `cover`
- `q`: optional quality preset for JPEG/WebP

This keeps original-file behavior simple and makes the resized path explicit.

### 2. Add a dedicated image derivative service

Create a new service module, likely:

- `webserver/services/image_derivatives.py`

Responsibilities:

- validate requested sizes
- detect image-capable source files
- compute cache keys
- create output directories
- generate resized images
- return cached files when valid
- invalidate stale derivatives when the source image changes

### 3. Cache key design

Each derivative should be keyed by:

- absolute source file path
- source file modified time and size
- requested width
- requested height
- fit mode
- output format
- quality settings
- implementation version string

This allows safe reuse and easy invalidation when source files or resize rules change.

### 4. Output format rules

Initial proposal:

- preserve PNG for alpha images when transparency matters
- use JPEG or WebP for non-alpha thumbnails if available
- keep SVG files unchanged for now unless rasterization is explicitly added later

For phase 1, we should avoid complex SVG rasterization unless the current image mix requires it.

### 5. UI integration targets

First wave of consumers:

1. explore page row thumbnails
2. part detail main preview
3. file inventory hover preview images

Each should request a size appropriate to its layout instead of the original file.

## Proposed Configuration Additions

We can either extend `config_ui.yaml` or add a dedicated image config file.

Recommendation for now: extend `config_ui.yaml`.

Suggested keys:

```yaml
image_serving:
  enabled: true
  cache_dir: auto
  thumbnail_width_explore: 320
  preview_width_detail: 1400
  preview_width_popover: 480
  quality_jpeg: 82
  quality_webp: 80
  max_source_pixels: 40000000
```

Meaning of `cache_dir`:

- `auto` means resolve to `%LOCALAPPDATA%\\project_base\\webserver_image_cache`
- later we can allow an explicit absolute path

## Implementation Phases

## Phase 1: Plan The Contract

- define the derived-image route shape
- define cache-key rules
- choose supported source formats for v1
- decide on quality and size defaults

Acceptance:

- config and route contract are written down and stable enough to implement

## Phase 2: Add Derivative Service

- create `image_derivatives.py`
- resolve machine-local cache root
- build deterministic derivative file paths
- generate missing derivatives
- reuse valid existing derivatives
- invalidate by source stat plus version signature

Acceptance:

- requesting the same image/size twice reuses the cached derivative
- changing the source image causes a fresh derivative to be generated

## Phase 3: Add Flask Route

- add a new route for resized images
- validate query parameters
- return `404` for unsupported source paths
- return derived file via `send_file`
- set useful cache headers where safe

Acceptance:

- browser requests to the derived route return the resized asset
- invalid parameters fail safely

## Phase 4: Wire Templates To Resized Assets

- update `explore.html`
- update `part_detail.html`
- use smaller sizes for thumbnails and hover previews
- decide whether detail preview should link through to the original file

Acceptance:

- explore and detail pages stop pulling large originals for normal preview rendering
- original full-size image is still available through the existing file route

## Phase 5: Add Observability And Guardrails

- log cache hits vs generated derivatives
- log generation failures clearly
- add safe limits for requested width and height
- avoid generating derivatives for tiny originals that do not benefit

Acceptance:

- failures are diagnosable
- malicious or accidental oversized requests are bounded

## Phase 6: Cleanup And Policy

- document cache location and cleanup expectations
- optionally add a manual cache-clear helper later
- make sure no derivative path is ever written into part folders

Acceptance:

- cache behavior is documented
- derivative files are confirmed to stay outside git-tracked content

## Technical Notes

### Cache Directory Resolution

Preferred resolution order:

1. explicit configured absolute cache path
2. `%LOCALAPPDATA%\\project_base\\webserver_image_cache`
3. temp/user-local machine cache path

Avoid by default:

- repo root
- `parts/`
- OneDrive-backed project folders

### Library Choice

Preferred choice:

- Pillow

Reason:

- straightforward resize support
- common and stable
- enough for raster image downsampling

If Pillow is not already installed in the runtime, we should confirm whether to add it as a dependency or use an external tool already present on the machine.

### Derivative Naming

Example pattern:

`<cache_root>/<hashed source id>/<mtime-size-version>/<width>x<height>-<fit>.<ext>`

This keeps cache cleanup and invalidation simple.

## Risks

- very large source files may still be expensive on first decode
- SVG handling may need a separate strategy
- Windows path normalization needs to be consistent for cache keys
- if templates request too many distinct sizes, cache fragmentation will grow

## Recommended First Implementation Scope

Keep the first build small:

1. raster images only: `.png`, `.jpg`, `.jpeg`, `.webp`
2. width-driven resizing first
3. one derived route
4. three template integration points
5. machine-local cache under `%LOCALAPPDATA%`

Do not include in the first pass:

1. SVG rasterization
2. background pre-generation of all thumbnails
3. multi-node/shared cache support
4. image editing or metadata extraction

## Acceptance Criteria For The Whole Feature

- normal browsing no longer serves giant originals for thumbnails
- repeat requests are faster because derivatives are reused
- cached derivatives survive app restarts on the same machine
- cached derivatives are not committed to git
- cached derivatives are not stored in part folders
- original files remain accessible when the user explicitly opens them

## Likely Files To Touch

- `webserver/app.py`
- `webserver/config_ui.yaml`
- `webserver/templates/explore.html`
- `webserver/templates/part_detail.html`
- `webserver/tests/test_app.py`
- new: `webserver/services/image_derivatives.py`

## Nice Follow-Ups After Plan 1

- add a tiny admin/status view showing cache size and hit rate
- add a cache clear button
- prewarm explore thumbnails during full reload if startup cost is acceptable
- add per-template image presets so sizes are not hardcoded in templates
