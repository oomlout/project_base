from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from webserver.cache import PartsCache
from webserver.config import APP_TITLE, DEFAULT_FAMILY, PART_FAMILY_CONFIGS
from webserver.services import generation_runner, parts_repository, source_writer, ui_config


def _select_family(family_slug: str | None) -> tuple[str, dict[str, Any]]:
    selected_slug = family_slug or DEFAULT_FAMILY
    family_config = PART_FAMILY_CONFIGS.get(selected_slug)
    if family_config is None:
        selected_slug = DEFAULT_FAMILY
        family_config = PART_FAMILY_CONFIGS[selected_slug]
    return selected_slug, family_config


def _build_form_values(family_config: dict[str, Any], submitted: dict[str, str] | None = None) -> dict[str, str]:
    values = dict(family_config.get("defaults", {}))
    for field in family_config.get("fields", []):
        values.setdefault(field["name"], "")
    if submitted:
        values.update(submitted)
    return values


def _reload_ui_config(app: Flask) -> tuple[dict[str, Any], bool]:
    previous = app.config.get("UI_CONFIG", {})
    current = ui_config.load_ui_config(Path(app.config["UI_CONFIG_PATH"]))
    app.config["UI_CONFIG"] = current
    app.config["PARTS_CACHE"].set_preview_priority(current["preview_priority"])
    return current, current != previous


def create_app(config_overrides: dict[str, Any] | None = None) -> Flask:
    repo_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__)
    app.config.update(
        APP_TITLE=APP_TITLE,
        SECRET_KEY="parts-explorer-dev",
        REPO_ROOT=repo_root,
        PARTS_DIR=repo_root / "parts",
        PARTS_SOURCE_DIR=repo_root / "parts_source",
        UI_CONFIG_PATH=repo_root / "webserver" / "ui_config.yaml",
    )
    if config_overrides:
        app.config.update(config_overrides)

    loaded_ui_config = ui_config.load_ui_config(Path(app.config["UI_CONFIG_PATH"]))
    app.config["UI_CONFIG"] = loaded_ui_config
    cache = PartsCache(Path(app.config["PARTS_DIR"]), loaded_ui_config["preview_priority"])
    cache.load_all()
    app.config["PARTS_CACHE"] = cache
    app.config["PART_FAMILY_CONFIGS"] = PART_FAMILY_CONFIGS

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return {
            "app_title": app.config["APP_TITLE"],
            "ui_config": app.config["UI_CONFIG"],
        }

    @app.get("/")
    def index():
        return redirect(url_for("explore"))

    @app.get("/explore")
    def explore():
        cache = app.config["PARTS_CACHE"]
        all_parts = cache.get_parts()
        taxonomy_filters = {
            key: request.args.get(key, "").strip()
            for key in [field for field in request.args.keys() if field.startswith("taxonomy_")]
        }
        query = request.args.get("q", "").strip()
        filtered_parts = parts_repository.filter_parts(all_parts, taxonomy_filters, query)
        navigation = parts_repository.build_taxonomy_navigation(all_parts, taxonomy_filters)
        breadcrumb_params: dict[str, str] = {}
        for pair in navigation["selected"]:
            breadcrumb_params[pair["key"]] = pair["value"]
            pair["params"] = dict(breadcrumb_params)
            if query:
                pair["params"]["q"] = query
            pair["url"] = url_for("explore", **pair["params"])
        for option in navigation["options"]:
            params = {key: value for key, value in taxonomy_filters.items() if value}
            params[option["key"]] = option["value"]
            if query:
                params["q"] = query
            option["params"] = params
            option["url"] = url_for("explore", **params)
        return render_template(
            "explore.html",
            all_parts=all_parts,
            parts=filtered_parts,
            taxonomy_filters=taxonomy_filters,
            query=query,
            navigation=navigation,
            cache_errors=cache.get_errors(),
        )

    @app.get("/parts/<part_id>")
    def part_detail(part_id: str):
        cache = app.config["PARTS_CACHE"]
        part = cache.get_part(part_id)
        if part is None:
            abort(404)
        previewable = part.get("preview_file")
        working_yaml_text = yaml.safe_dump(
            part["working_yaml"],
            allow_unicode=False,
            sort_keys=False,
        )
        return render_template(
            "part_detail.html",
            part=part,
            previewable=previewable,
            working_yaml_text=working_yaml_text,
        )

    @app.get("/parts/<part_id>/files/<path:relative_path>")
    def part_file(part_id: str, relative_path: str):
        cache = app.config["PARTS_CACHE"]
        part = cache.get_part(part_id)
        if part is None:
            abort(404)
        part_dir = Path(part["part_dir"]).resolve()
        requested = (part_dir / relative_path).resolve()
        if part_dir not in requested.parents and requested != part_dir:
            abort(404)
        if not requested.exists() or not requested.is_file():
            abort(404)
        return send_file(requested)

    @app.route("/add", methods=["GET", "POST"])
    def add_item():
        selected_slug, family_config = _select_family(
            request.values.get("family") if request.method == "POST" else request.args.get("family")
        )
        if request.method == "POST":
            submitted = request.form.to_dict()
            try:
                result = source_writer.write_source_entry(
                    Path(app.config["PARTS_SOURCE_DIR"]),
                    submitted,
                    family_config,
                )
            except source_writer.ValidationError as exc:
                flash(str(exc), "error")
                form_values = _build_form_values(family_config, submitted)
                return render_template(
                    "add_item.html",
                    family_slug=selected_slug,
                    family_config=family_config,
                    families=PART_FAMILY_CONFIGS,
                    form_values=form_values,
                )

            flash(
                f"Created parts_source entry '{result['part_id']}' at {result['target_file']}.",
                "success",
            )
            return redirect(url_for("add_item", family=selected_slug))

        form_values = _build_form_values(family_config)
        return render_template(
            "add_item.html",
            family_slug=selected_slug,
            family_config=family_config,
            families=PART_FAMILY_CONFIGS,
            form_values=form_values,
        )

    @app.post("/reload/fast")
    def reload_fast():
        _, ui_changed = _reload_ui_config(app)
        if ui_changed:
            summary = app.config["PARTS_CACHE"].load_all()
            flash("UI config changed, so fast reload promoted itself to a full cache rebuild.", "success")
        else:
            summary = app.config["PARTS_CACHE"].reload_changed()
        flash(
            f"Fast reload scanned {summary.scanned} parts and refreshed {summary.changed} changed entries.",
            "success",
        )
        if summary.removed:
            flash(f"Removed {summary.removed} missing entries from cache.", "success")
        for error in summary.errors:
            flash(error, "error")
        return redirect(request.referrer or url_for("explore"))

    @app.post("/reload/all")
    def reload_all():
        _reload_ui_config(app)
        summary = app.config["PARTS_CACHE"].load_all()
        flash(
            f"Full reload loaded {summary.loaded} parts from disk.",
            "success",
        )
        for error in summary.errors:
            flash(error, "error")
        return redirect(request.referrer or url_for("explore"))

    @app.post("/generation/run")
    def run_generation():
        generation_runner.launch_generation(Path(app.config["REPO_ROOT"]))
        flash("Launched action_make_all.py in a separate cmd window.", "success")
        return redirect(request.referrer or url_for("explore"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
