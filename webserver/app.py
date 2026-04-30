from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from webserver.cache import PartsCache
from webserver.config_app import APP_TITLE
from webserver.services import (
    config_form,
    config_part_source,
    config_port,
    config_ui,
    generation_runner,
    parts_repository,
    source_writer,
)


def _select_family(config: dict[str, Any], family_slug: str | None) -> tuple[str, dict[str, Any]]:
    families = config["families"]
    selected_slug = family_slug or config["default_family"]
    family_config = families.get(selected_slug)
    if family_config is None:
        selected_slug = config["default_family"]
        family_config = families[selected_slug]
    return selected_slug, family_config


def _build_form_values(family_config: dict[str, Any], submitted: dict[str, str] | None = None) -> dict[str, str]:
    values = dict(family_config.get("defaults", {}))
    for field in family_config.get("fields", []):
        values.setdefault(field["name"], field.get("default", ""))
    if submitted:
        values.update(submitted)
    return values


def _reload_ui_config(app: Flask) -> tuple[dict[str, Any], bool]:
    previous = app.config.get("CONFIG_UI", {})
    current = config_ui.load_ui_config(Path(app.config["CONFIG_UI_PATH"]))
    app.config["CONFIG_UI"] = current
    app.config["PARTS_CACHE"].set_preview_priority(current["preview_priority"])
    app.config["PARTS_CACHE"].set_search_field_names(
        [field["name"] for field in current["search_fields"]["available"]]
    )
    return current, current != previous


def _normalize_parts_dirs(
    parts_dirs: Path | str | list[Path | str] | tuple[Path | str, ...],
) -> list[Path]:
    if isinstance(parts_dirs, (Path, str)):
        candidates = [parts_dirs]
    else:
        candidates = list(parts_dirs or [])

    normalized: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        path = Path(candidate).resolve(strict=False)
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(path)
    return normalized


def _build_parts_source_config(parts_dirs: list[Path]) -> dict[str, Any]:
    return {
        "directories": [str(path) for path in parts_dirs],
        "resolved_directories": list(parts_dirs),
    }


def _reload_part_source_config(app: Flask) -> tuple[dict[str, Any], bool]:
    previous = app.config.get("CONFIG_PART_SOURCE", {})
    if app.config.get("PARTS_SOURCE_CONFIG_LOCKED"):
        current = _build_parts_source_config(_normalize_parts_dirs(app.config.get("PARTS_DIRS", [])))
        app.config["CONFIG_PART_SOURCE"] = current
        return current, False

    current = config_part_source.load_part_source_config(
        Path(app.config["CONFIG_PART_SOURCE_PATH"]),
        Path(app.config["REPO_ROOT"]),
    )
    previous_dirs = _normalize_parts_dirs(previous.get("resolved_directories", []))
    current_dirs = _normalize_parts_dirs(current["resolved_directories"])
    app.config["CONFIG_PART_SOURCE"] = current
    app.config["PARTS_DIRS"] = current_dirs
    if current_dirs:
        app.config["PARTS_DIR"] = current_dirs[0]
    app.config["PARTS_CACHE"].set_parts_dirs(current_dirs)
    return current, current_dirs != previous_dirs


def _build_manual_form_values(
    working_manual: dict[str, Any],
    manual_fields: list[dict[str, str]],
) -> dict[str, str]:
    return source_writer.build_multiline_field_values(
        working_manual,
        [field["name"] for field in manual_fields],
    )


def _selected_search_fields(config: dict[str, Any], submitted: list[str] | None = None) -> list[str]:
    available_names = [field["name"] for field in config["search_fields"]["available"]]
    requested = submitted if submitted is not None else config["search_fields"]["default_selected"]
    normalized: list[str] = []
    for field_name in requested:
        name = str(field_name).strip()
        if name and name in available_names and name not in normalized:
            normalized.append(name)
    if normalized:
        return normalized
    return list(config["search_fields"]["default_selected"])


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

    part_source_override_provided = bool(
        config_overrides and ("PARTS_DIRS" in config_overrides or "PARTS_DIR" in config_overrides)
    )
    app.config["PARTS_SOURCE_CONFIG_LOCKED"] = part_source_override_provided

    if part_source_override_provided:
        override_value = (
            app.config["PARTS_DIRS"]
            if config_overrides and "PARTS_DIRS" in config_overrides
            else app.config["PARTS_DIR"]
        )
        resolved_parts_dirs = _normalize_parts_dirs(override_value)
        loaded_part_source_config = _build_parts_source_config(resolved_parts_dirs)
    else:
        loaded_part_source_config = config_part_source.load_part_source_config(
            Path(app.config["CONFIG_PART_SOURCE_PATH"]),
            Path(app.config["REPO_ROOT"]),
        )
        resolved_parts_dirs = _normalize_parts_dirs(loaded_part_source_config["resolved_directories"])

    app.config["CONFIG_PART_SOURCE"] = loaded_part_source_config
    app.config["PARTS_DIRS"] = resolved_parts_dirs
    if resolved_parts_dirs:
        app.config["PARTS_DIR"] = resolved_parts_dirs[0]

    loaded_ui_config = config_ui.load_ui_config(Path(app.config["CONFIG_UI_PATH"]))
    loaded_form_config = config_form.load_form_config(
        Path(app.config["CONFIG_FORM_BASE_PATH"]),
        Path(app.config["CONFIG_FORM_PATH"]),
    )
    loaded_port_config = config_port.load_port_config(Path(app.config["CONFIG_PORT_PATH"]))
    app.config["CONFIG_UI"] = loaded_ui_config
    app.config["CONFIG_FORM"] = loaded_form_config
    app.config["CONFIG_PORT"] = loaded_port_config
    app.config["PORT"] = loaded_port_config["port"]
    cache = PartsCache(
        app.config["PARTS_DIRS"],
        loaded_ui_config["preview_priority"],
        [field["name"] for field in loaded_ui_config["search_fields"]["available"]],
    )
    cache.load_all()
    app.config["PARTS_CACHE"] = cache

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return {
            "app_title": app.config["APP_TITLE"],
            "ui_config": app.config["CONFIG_UI"],
        }

    @app.get("/")
    def index():
        return redirect(url_for("explore"))

    @app.get("/explore")
    def explore():
        cache = app.config["PARTS_CACHE"]
        current_ui_config = app.config["CONFIG_UI"]
        all_parts = cache.get_parts()
        taxonomy_filters = {
            key: request.args.get(key, "").strip()
            for key in [field for field in request.args.keys() if field.startswith("taxonomy_")]
        }
        query = request.args.get("q", "").strip()
        selected_search_fields = _selected_search_fields(
            current_ui_config,
            request.args.getlist("search_fields"),
        )
        filtered_parts = parts_repository.filter_parts(
            all_parts,
            taxonomy_filters,
            query,
            selected_search_fields,
        )
        navigation = parts_repository.build_taxonomy_navigation(all_parts, taxonomy_filters)
        breadcrumb_params: dict[str, str] = {}
        for pair in navigation["selected"]:
            breadcrumb_params[pair["key"]] = pair["value"]
            pair["params"] = dict(breadcrumb_params)
            if query:
                pair["params"]["q"] = query
            for field_name in selected_search_fields:
                pair["params"].setdefault("search_fields", [])
                pair["params"]["search_fields"].append(field_name)
            pair["url"] = url_for("explore", **pair["params"])
        for option in navigation["options"]:
            params = {key: value for key, value in taxonomy_filters.items() if value}
            params[option["key"]] = option["value"]
            if query:
                params["q"] = query
            if selected_search_fields:
                params["search_fields"] = list(selected_search_fields)
            option["params"] = params
            option["url"] = url_for("explore", **params)
        return render_template(
            "explore.html",
            all_parts=all_parts,
            parts=filtered_parts,
            taxonomy_filters=taxonomy_filters,
            query=query,
            search_field_options=current_ui_config["search_fields"]["available"],
            selected_search_fields=selected_search_fields,
            navigation=navigation,
            cache_errors=cache.get_errors(),
        )

    @app.get("/parts/<part_id>")
    def part_detail(part_id: str):
        cache = app.config["PARTS_CACHE"]
        part = cache.get_part(part_id)
        if part is None:
            abort(404)
        manual_fields = app.config["CONFIG_UI"]["manual_fields"]
        previewable = part.get("preview_file")
        working_yaml_text = yaml.safe_dump(
            part["working_yaml"],
            allow_unicode=False,
            sort_keys=False,
        )
        working_manual_text = ""
        if part["working_manual"]:
            working_manual_text = yaml.safe_dump(
                part["working_manual"],
                allow_unicode=False,
                sort_keys=False,
            )
        return render_template(
            "part_detail.html",
            part=part,
            manual_fields=manual_fields,
            manual_form_values=_build_manual_form_values(part["working_manual"], manual_fields),
            previewable=previewable,
            working_manual_text=working_manual_text,
            working_yaml_text=working_yaml_text,
        )

    @app.post("/parts/<part_id>/manual")
    def update_part_manual(part_id: str):
        cache = app.config["PARTS_CACHE"]
        part = cache.get_part(part_id)
        if part is None:
            abort(404)

        manual_fields = app.config["CONFIG_UI"]["manual_fields"]
        manual_path = Path(part["part_dir"]) / "working_manual.yaml"
        try:
            result = source_writer.write_part_manual_fields(
                manual_path,
                request.form.to_dict(),
                [field["name"] for field in manual_fields],
            )
        except source_writer.ValidationError as exc:
            flash(str(exc), "error")
            return redirect(url_for("part_detail", part_id=part_id))

        summary = cache.reload_changed()
        for error in summary.errors:
            flash(error, "error")

        if result["file_exists"]:
            flash(f"Saved working_manual.yaml for {part['name']}.", "success")
        else:
            flash(f"Cleared working_manual.yaml for {part['name']}.", "success")
        return redirect(url_for("part_detail", part_id=part_id))

    @app.post("/parts/<part_id>/reload")
    def reload_part_detail(part_id: str):
        cache = app.config["PARTS_CACHE"]
        part = cache.get_part(part_id)
        if part is None:
            abort(404)

        _, ui_changed = _reload_ui_config(app)
        _, part_source_changed = _reload_part_source_config(app)
        if ui_changed or part_source_changed:
            summary = cache.load_all()
            flash("Reloaded part details after applying config changes.", "success")
        else:
            summary = cache.reload_changed()
            flash(f"Reloaded part details for {part['name']} from disk.", "success")

        for error in summary.errors:
            flash(error, "error")
        if cache.get_part(part_id) is None:
            flash("That part is no longer available in the configured sources.", "error")
            return redirect(url_for("explore"))
        return redirect(url_for("part_detail", part_id=part_id))

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
        loaded_form_config = config_form.load_form_config(
            Path(app.config["CONFIG_FORM_BASE_PATH"]),
            Path(app.config["CONFIG_FORM_PATH"]),
        )
        app.config["CONFIG_FORM"] = loaded_form_config
        families = loaded_form_config["families"]
        selected_slug, family_config = _select_family(
            loaded_form_config,
            request.values.get("family") if request.method == "POST" else request.args.get("family")
        )
        if request.method == "POST":
            submitted = request.form.to_dict()
            try:
                result = source_writer.write_manual_entry(
                    Path(app.config["MANUAL_QUEUE_PATH"]),
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
                    families=families,
                    form_values=form_values,
                )

            flash(
                f"Recorded manual entry #{result['entry_count']} in {result['target_file']}.",
                "success",
            )
            return redirect(url_for("add_item", family=selected_slug))

        form_values = _build_form_values(family_config)
        return render_template(
            "add_item.html",
            family_slug=selected_slug,
            family_config=family_config,
            families=families,
            form_values=form_values,
        )

    @app.post("/reload/fast")
    def reload_fast():
        _, ui_changed = _reload_ui_config(app)
        _, part_source_changed = _reload_part_source_config(app)
        if ui_changed or part_source_changed:
            summary = app.config["PARTS_CACHE"].load_all()
            flash("Config changed, so fast reload promoted itself to a full cache rebuild.", "success")
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
        _reload_part_source_config(app)
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
    app.run(debug=False, port=app.config["PORT"])
