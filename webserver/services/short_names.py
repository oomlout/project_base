from __future__ import annotations

import re
from typing import Any

from webserver.services import parts_repository

MD5_KEYS = ("md5_6", "md5_6_alpha", "md5_6_upper", "md5_6_alpha_upper")
BIP39_2_KEYS = (
    "bip_39_2_word_space",
    "bip39_2_word",
    "bip39_2_words",
    "Bip39_2_word",
    "bip_39_2_word_underscore",
    "bip_39_2_word_no_space",
)
BIP39_3_KEYS = (
    "bip_39_3_word_space",
    "bip39_3_word",
    "bip39_3_words",
    "Bip39_3_word",
    "bip_39_3_word_underscore",
    "bip_39_3_word_no_space",
)


def _first_value(data: dict[str, Any], candidate_keys: tuple[str, ...]) -> str:
    by_lower_key = {str(key).lower(): value for key, value in data.items()}
    for key in candidate_keys:
        value = by_lower_key.get(key.lower())
        if value in (None, ""):
            continue
        if isinstance(value, list):
            return " ".join(str(item).strip() for item in value if item not in (None, ""))
        return str(value).strip()
    return ""


def normalize_code(value: str) -> str:
    return re.sub(r"[^0-9a-z]+", "", str(value or "").lower())


def normalize_words(value: str) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^0-9a-z]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_mode(query: str) -> str:
    return "bip39" if any(char.isspace() for char in str(query or "")) else "md5_6"


def build_short_name_entry(part: dict[str, Any]) -> dict[str, Any]:
    data = part.get("data", {})
    if not isinstance(data, dict):
        data = {}
    md5_6 = _first_value(data, MD5_KEYS)
    bip39_2_word = _first_value(data, BIP39_2_KEYS)
    bip39_3_word = _first_value(data, BIP39_3_KEYS)
    bip39_values = [
        str(data.get(key, "") or "").strip()
        for key in (
            "bip_39_2_word_space",
            "bip_39_2_word_underscore",
            "bip_39_2_word_no_space",
            "bip_39_3_word_space",
            "bip_39_3_word_underscore",
            "bip_39_3_word_no_space",
            "bip39_2_word",
            "bip39_3_word",
            "Bip39_2_word",
            "Bip39_3_word",
        )
        if str(data.get(key, "") or "").strip()
    ]
    bip39_search = normalize_words(f"{bip39_2_word} {bip39_3_word}")
    return {
        **part,
        "short_names": {
            "md5_6": md5_6,
            "bip39_2_word": bip39_2_word,
            "bip39_3_word": bip39_3_word,
            "md5_6_search": normalize_code(md5_6),
            "bip39_search": bip39_search,
            "bip39_exact_values": bip39_values,
        },
    }


def build_short_name_entries(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = [build_short_name_entry(part) for part in parts]
    return parts_repository.sort_parts(entries, "name")


def filter_short_name_entries(entries: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if query == "":
        return entries

    mode = search_mode(query)
    if mode == "bip39":
        tokens = [token for token in normalize_words(query).split(" ") if token]
        if not tokens:
            return entries
        return [
            entry
            for entry in entries
            if all(token in entry["short_names"]["bip39_search"] for token in tokens)
        ]

    needle = normalize_code(query)
    if not needle:
        return entries
    return [
        entry
        for entry in entries
        if needle in entry["short_names"]["md5_6_search"]
    ]


def exact_short_name_matches(parts: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    query_code = normalize_code(query)
    query_words = normalize_words(query)
    matches = []
    for entry in build_short_name_entries(parts):
        short_names = entry["short_names"]
        if query_code and short_names["md5_6_search"] == query_code:
            matches.append(entry)
            continue
        bip39_word_matches = query_words and any(
            normalize_words(value) == query_words
            for value in short_names["bip39_exact_values"]
        )
        bip39_code_matches = query_code and any(
            normalize_code(value) == query_code
            for value in short_names["bip39_exact_values"]
        )
        if bip39_word_matches or bip39_code_matches:
            matches.append(entry)
    return matches
