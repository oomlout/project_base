from __future__ import annotations

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from webserver.services import short_names as short_name_service

short_names_blueprint = Blueprint("short_names", __name__)


def _render_short_names(query: str):
    cache = current_app.config["PARTS_CACHE"]
    entries = short_name_service.build_short_name_entries(cache.get_parts())
    filtered_entries = short_name_service.filter_short_name_entries(entries, query)
    return render_template(
        "short_names.html",
        all_parts=entries,
        parts=filtered_entries,
        query=query,
        search_mode=short_name_service.search_mode(query),
        cache_errors=cache.get_errors(),
        image_viewer_enabled=True,
    )


@short_names_blueprint.get("/short_names")
def short_names():
    return _render_short_names(request.args.get("q", ""))


def _part_id_query(extra: str) -> str:
    return "_".join(part for part in str(extra or "").replace("\\", "/").split("/") if part).strip("_")


def _part_id_matches(parts: list[dict], query: str) -> list[dict]:
    normalized_query = _part_id_query(query).lower()
    if not normalized_query:
        return []
    return [
        part
        for part in parts
        if normalized_query in str(part.get("id", "")).lower()
    ]


def _short_name_query(extra: str) -> str:
    return str(extra or "").replace("\\", " ").replace("/", " ").strip()


@short_names_blueprint.get("/id/<path:extra>")
def resolve_shortlink(extra: str):
    cache = current_app.config["PARTS_CACHE"]
    part_id_query = _part_id_query(extra)
    part = cache.get_part(part_id_query)
    if part is not None:
        return redirect(url_for("parts.part_detail", part_id=part["id"]))

    all_parts = cache.get_parts()
    short_name_matches = short_name_service.exact_short_name_matches(all_parts, extra)
    if len(short_name_matches) == 1:
        return redirect(url_for("parts.part_detail", part_id=short_name_matches[0]["id"]))

    short_name_search_query = _short_name_query(extra)
    short_name_search_matches = short_name_service.filter_short_name_entries(
        short_name_service.build_short_name_entries(all_parts),
        short_name_search_query,
    )
    if len(short_name_search_matches) == 1:
        return redirect(url_for("parts.part_detail", part_id=short_name_search_matches[0]["id"]))

    id_matches = _part_id_matches(all_parts, extra)
    if len(id_matches) == 1:
        return redirect(url_for("parts.part_detail", part_id=id_matches[0]["id"]))
    if "_" in extra or "\\" in extra or len(id_matches) > 1:
        return redirect(url_for("explore.explore", q=part_id_query, search_fields="id"))

    return _render_short_names(short_name_search_query)
