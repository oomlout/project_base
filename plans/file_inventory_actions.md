# File Inventory Actions Plan

## Goal

Add a modular file-action system to the part detail file inventory so applicable files can launch external conversions from the UI.

Initial actions:

- `.scad` -> `Generate STL` using `openscad`
- `.svg` -> `Convert to PDF` using `inkscape`

Supporting changes:

- Detached popup cmd launch behavior with no completion tracking
- Compact file size labels like `980`, `1.2k`, and `2.4M`
- Generic row-action rendering so future actions are registry additions

## Decisions

- Launch actions in detached popup cmd windows
- Do not add completion tracking or error monitoring
- Resolve `openscad` and `inkscape` from `PATH`
- Keep the implementation modular around a reusable action registry and launcher

## Progress

1. Discovery - complete
2. Design - complete
3. Backend action service - complete
4. Inventory integration - complete
5. Route and UI wiring - complete
6. Tests and validation - complete

## Implementation Steps

1. Add `webserver/services/file_actions.py` with action definitions, applicability checks, output path builders, and command builders.
2. Generalize `webserver/services/generation_runner.py` so it can launch arbitrary detached commands in a popup cmd window.
3. Extend `webserver/services/parts_repository.py` to add compact `size_label` values and attach `actions` to each file row.
4. Add a POST route for part file actions in `webserver/routes/parts.py`.
5. Update `webserver/templates/part_detail.html` to show generic inline action buttons per file.
6. Tighten `webserver/static/style.css` so the file inventory stays dense with action buttons.
7. Add focused tests in `webserver/tests/test_app.py` and service tests as needed.

## Verification

1. Confirm compact size labels render without the word `bytes`.
2. Confirm `.scad` rows expose `Generate STL`.
3. Confirm `.svg` rows expose `Convert to PDF`.
4. Confirm invalid actions and invalid paths are rejected safely.
5. Confirm the launcher is called with the expected OpenSCAD and Inkscape commands.
6. Confirm the part detail page renders the new actions and compact sizes.