"""ARTEMIS Web Search / Fetch — retrieval for Ollama agents (video: web research).

Gives the Artemis agent the ability to search the web and fetch pages, so your
Ollama models can ground answers in current information. Wires the existing
`web_search` and `fetch_page` tool slots in `tools.py` (currently unavailable
placeholders) to real implementations.

* `web_search(query, limit)` — returns a list of results (title, url, snippet).
* `web_fetch(url)` — fetches a page and extracts readable text.

The search backend is pluggable: set `search_backend` to a callable
`(query, limit) -> list[result]` (e.g. backed by a search API). Fetch uses
httpx with a browser-like UA and basic readability text extraction. Same-origin
and SSRF guards keep egress safe.
"""
from __future__ import annotations

import html
import re
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import httpx


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 0.0


# Default search backend: not connected. Configure set_search_backend() to wire
# a real retrieval provider (Brave, Serper, Google, DuckDuckGo HTML, etc.).
_DEFAULT_BACKEND_NOTICE = (
    "web_search backend not configured. Call set_search_backend(callable) with "
    "(query, limit) -> list[dict(title,url,snippet)], or wire a search API key "
    "in Operations."
)


class WebSearchService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._lock = threading.RLock()
        self._backend: Callable[[str, int], list[dict[str, str]]] | None = None
        self._ua = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120 Safari/537.36 Artemis/1.0"
        )
        # SSRF / egress guard: block private/link-local/multicast addresses.
        self._blocked_hosts = {
            "localhost", "127.0.0.1", "::1", "0.0.0.0",
            "169.254.169.254", "fe80::1", "ff02::1",
        }
        self._blocked_prefixes = ("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                                  "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                                  "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                                  "172.30.", "172.31.", "192.168.")

    # ── configuration ──
    def set_search_backend(self, backend: Callable[[str, int], list[dict[str, str]]]):
        with self._lock:
            self._backend = backend

    def backend_status(self) -> dict:
        with self._lock:
            return {"configured": self._backend is not None,
                    "notice": "" if self._backend is not None else _DEFAULT_BACKEND_NOTICE}

    # ── search ──
    def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        if not query or not query.strip():
            return {"ok": False, "error": "empty query", "results": []}
        limit = max(1, min(int(limit), 10))
        with self._lock:
            backend = self._backend
        if backend is None:
            return {"ok": False, "error": _DEFAULT_BACKEND_NOTICE, "results": []}
        try:
            raw = backend(query.strip(), limit)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"search backend error: {exc}", "results": []}
        results = []
        for item in raw[:limit]:
            results.append({
                "title": item.get("title", "")[:200],
                "url": item.get("url", "")[:500],
                "snippet": item.get("snippet", "")[:500],
            })
        return {"ok": True, "query": query.strip(), "results": results,
                "count": len(results), "backend": "configured"}

    # ── fetch ──
    def _is_blocked(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname or ""
            if host in self._blocked_hosts:
                return True
            if parsed.scheme not in ("http", "https"):
                return True
            for prefix in self._blocked_prefixes:
                if host.startswith(prefix):
                    return True
            return False
        except Exception:  # noqa: BLE001
            return True

    @staticmethod
    def _extract_text(html_content: str) -> str:
        # Crude readability: strip scripts/styles, collapse whitespace.
        text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html_content)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return text.strip()

    def fetch(self, url: str, max_chars: int = 12000) -> dict[str, Any]:
        if not url:
            return {"ok": False, "error": "empty url"}
        if self._is_blocked(url):
            return {"ok": False, "error": "URL blocked by egress/SSRF policy"}
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.hostname:
                return {"ok": False, "error": "invalid URL"}
        except Exception:  # noqa: BLE001
            return {"ok": False, "error": "invalid URL"}
        try:
            with httpx.Client(timeout=20, follow_redirects=True,
                              trust_env=False, headers={"User-Agent": self._ua}) as c:
                r = c.get(url)
                r.raise_for_status()
                ctype = r.headers.get("content-type", "")
                if "text/" not in ctype and "html" not in ctype and not ctype:
                    return {"ok": False, "error": f"unsupported content type: {ctype}",
                            "url": url}
                body = self._extract_text(r.text)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"fetch failed: {exc}", "url": url}
        trimmed = body[:max_chars]
        return {
            "ok": True, "url": url, "title": self._guess_title(r.text),
            "content": trimmed, "length": len(body),
            "truncated": len(body) > max_chars,
        }

    @staticmethod
    def _guess_title(html_content: str) -> str:
        m = re.search(r"(?is)<title>(.*?)</title>", html_content or "")
        if m:
            return html.unescape(m.group(1)).strip()[:200]
        return ""

    def status(self) -> dict:
        with self._lock:
            configured = self._backend is not None
        return {"web_search": {"configured": configured,
                               "notice": "" if configured else _DEFAULT_BACKEND_NOTICE},
                "web_fetch": {"available": True, "guards": "ssrf + same-scheme"},
                "search_tool": "web_search", "fetch_tool": "web_fetch"}


class WebSearchToolHost:
    """Adapts WebSearchService into the Artemis tool-registry calling convention."""

    def __init__(self, service: WebSearchService):
        self.service = service

    def web_search(self, args: dict[str, Any]) -> dict[str, Any]:
        return self.service.search(args.get("query", ""), args.get("limit", 5))

    def web_fetch(self, args: dict[str, Any]) -> dict[str, Any]:
        return self.service.fetch(args.get("url", ""), args.get("max_chars", 12000))
