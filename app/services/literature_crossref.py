import time
from typing import Any, Dict, List, Optional
import requests


class LiteratureCrossRef:
    def __init__(self, api_timeout_seconds: int = 10) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Legal-Analysis-System/1.0 (academic; contact: admin@example.com)"
        })
        self.api_timeout_seconds = api_timeout_seconds

    def search_semantic_scholar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,authors,year,venue,url,abstract,citationCount"
            }
            resp = self.session.get(url, params=params, timeout=self.api_timeout_seconds)
            resp.raise_for_status()
            data = resp.json() or {}
            results = data.get("data", [])
            return [
                {
                    "title": r.get("title"),
                    "authors": ", ".join(a.get("name") for a in r.get("authors", [])),
                    "year": r.get("year"),
                    "venue": r.get("venue"),
                    "url": r.get("url"),
                    "abstract": r.get("abstract"),
                    "citations": r.get("citationCount"),
                }
                for r in results
            ]
        except Exception:
            return []

    def search_crossref(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            url = "https://api.crossref.org/works"
            params = {"query": query, "rows": limit}
            resp = self.session.get(url, params=params, timeout=self.api_timeout_seconds)
            resp.raise_for_status()
            items = resp.json().get("message", {}).get("items", [])
            results: List[Dict[str, Any]] = []
            for it in items:
                results.append({
                    "title": (it.get("title") or [""])[0],
                    "authors": ", ".join(
                        f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get("author", [])
                    ),
                    "year": (it.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0],
                    "venue": it.get("container-title", [""])[0],
                    "url": it.get("URL"),
                    "abstract": it.get("abstract"),
                    "citations": it.get("is-referenced-by-count"),
                })
            return results
        except Exception:
            return []

    def aggregate_results(self, query: str, limit: int = 10) -> Dict[str, Any]:
        ss = self.search_semantic_scholar(query, limit=min(5, limit))
        cr = self.search_crossref(query, limit=min(5, limit))
        combined = ss + cr
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for r in combined:
            key = (r.get("title") or "").strip().lower()
            if key in seen or not key:
                continue
            seen.add(key)
            deduped.append(r)
        deduped.sort(key=lambda x: (x.get("citations") or 0), reverse=True)
        return {"query": query, "results": deduped[:limit]}

