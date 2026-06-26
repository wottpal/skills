#!/usr/bin/env python3
"""Extract readable text from `himalaya message read --json` output."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from typing import Any, Iterable


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        if value:
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for key in ("Text", "Html", "text", "html"):
            if key in value:
                yield from iter_strings(value[key])


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<(script|style).*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s*\n+", "\n\n", value)
    return value.strip()


def body_candidates(message: dict[str, Any]) -> list[str]:
    candidates: list[str] = []

    for key in ("text_body", "html_body"):
        candidates.extend(iter_strings(message.get(key)))

    parts = message.get("parts")
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict):
                candidates.extend(iter_strings(part.get("body")))

    seen: set[str] = set()
    normalized: list[str] = []

    for candidate in candidates:
        text = strip_html(candidate)
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)

    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chars", type=int, default=3000)
    parser.add_argument("--urls", action="store_true")
    args = parser.parse_args()

    message = json.load(sys.stdin)
    text = "\n\n".join(body_candidates(message))
    if args.chars > 0:
        text = text[: args.chars]

    print(text)

    if args.urls:
        raw = json.dumps(message)
        urls = sorted(set(re.findall(r"https?://[^\"'\\s<>]+", raw)))
        if urls:
            print("\nURLS:")
            print("\n".join(urls))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
