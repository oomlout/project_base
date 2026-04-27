# Webserver

Flask app for browsing generated parts from `parts/` and creating new source entries in `parts_source/`.

## Run

From the repo root:

```bash
python -m webserver.app
```

Then open `http://127.0.0.1:5000/explore`.

## Main Behaviors

- `/` redirects to `/explore`
- explore view loads from an in-memory cache built at startup
- explore results are shown as dense horizontal rows for faster scanning
- `Reload Fast` only refreshes new or changed part folders
- `Reload Fast` promotes itself to a full rebuild if `ui_config.yaml` changes
- `Reload All` rebuilds the cache from disk
- `Run Generation` launches `action_make_all.py` in a separate visible Windows `cmd` window
- `/add` writes a new `parts_source/<part_id>/working.yaml` based on the selected form config
- preview image selection is driven by `ui_config.yaml`

## Styling Structure

- Design tokens live in `static/style.css` under `:root`
- Shared layout and component classes are defined in `style.css`
- Shared page chrome and toolbar controls live in `templates/base.html`
- Page-specific behaviors are in `static/explore.js` and `static/add_item.js`

## UI Config

- `ui_config.yaml` currently exposes `preview_priority`
- The list is evaluated from top to bottom
- Exact filenames are matched before wildcard fallbacks
- `Reload All` always applies config changes
- `Reload Fast` also applies config changes and will rebuild the cache if the UI config changed
