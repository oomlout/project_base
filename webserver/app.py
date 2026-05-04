from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flask import Flask

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from webserver.config_app import APP_TITLE
from webserver.presentation import part_image_url
from webserver.routes import register_blueprints
from webserver.runtime import initialize_runtime


def create_app(config_overrides: dict[str, Any] | None = None) -> Flask:
    repo_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__)
    app.config.update(
        APP_TITLE=APP_TITLE,
        SECRET_KEY="parts-explorer-dev",
        REPO_ROOT=repo_root,
        PARTS_DIR=repo_root / "parts",
        PARTS_DIRS=[repo_root / "parts"],
        PARTS_SOURCE_DIR=repo_root / "parts_source",
        CONFIG_PART_SOURCE_PATH=repo_root / "webserver" / "config_part_source.yaml",
        CONFIG_UI_PATH=repo_root / "webserver" / "config_ui.yaml",
        CONFIG_FORM_BASE_PATH=repo_root / "webserver" / "config_form_base.yaml",
        CONFIG_FORM_PATH=repo_root / "webserver" / "config_form.yaml",
        CONFIG_PORT_PATH=repo_root / "webserver" / "config_port.yaml",
        MANUAL_QUEUE_PATH=repo_root / "working_manual.yaml",
    )
    if config_overrides:
        app.config.update(config_overrides)

    initialize_runtime(app, config_overrides)

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return {
            "app_title": app.config["APP_TITLE"],
            "ui_config": app.config["CONFIG_UI"],
            "part_image_url": part_image_url,
        }

    register_blueprints(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, host=app.config["HOST"], port=app.config["PORT"])
