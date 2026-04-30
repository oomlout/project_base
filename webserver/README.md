# Webserver

Flask app for browsing generated parts from `parts/` and recording new manual entries into `working_manual.yaml`.

## Run

From the repo root:

```bash
python -m webserver.app
```

Then open `http://127.0.0.1:<port>/explore`.
The default port is `5000`, and it is configurable through `config_port.yaml`.

## Main Behaviors

- `/` redirects to `/explore`
- explore view loads from an in-memory cache built at startup
- explore results are shown as dense horizontal rows for faster scanning
- `Reload Fast` only refreshes new or changed part folders
- `Reload Fast` promotes itself to a full rebuild if `config_ui.yaml` changes
- `Reload All` rebuilds the cache from disk
- `Run Generation` launches `action_make_all.py` in a separate visible Windows `cmd` window
- `/add` records a new manual entry into `working_manual.yaml` at the repo root
- preview image selection is driven by `config_ui.yaml`
- startup port is driven by `config_port.yaml`

## Styling Structure

- Design tokens live in `static/style.css` under `:root`
- Shared layout and component classes are defined in `style.css`
- Shared page chrome and toolbar controls live in `templates/base.html`
- Page-specific behaviors are in `static/explore.js` and `static/add_item.js`

## UI Config

- `config_ui.yaml` currently exposes `preview_priority`
- The list is evaluated from top to bottom
- Exact filenames are matched before wildcard fallbacks
- `Reload All` always applies config changes
- `Reload Fast` also applies config changes and will rebuild the cache if the UI config changed

## Form Config

- `config_form_base.yaml` is the default add-form config
- `config_form.yaml` overrides it whenever that file exists
- The default generic family exposes `taxonomy_1` through `taxonomy_15`
- The webserver now records raw validated form values and does not perform taxonomy mapping
