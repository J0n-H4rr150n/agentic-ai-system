from __future__ import annotations

import asyncio
import html
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


app = FastAPI(title="Agentic AI System Lab Target", version="1.0")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "lab-target", "time": _now_iso()}


@app.get("/robots.txt")
def robots() -> PlainTextResponse:
    return PlainTextResponse("User-agent: *\nDisallow: /admin\n")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>Lab Target</title>
  </head>
  <body>
    <h1>Lab Target</h1>
    <p>This is a safe local test target for the Agentic AI System.</p>

    <ul>
      <li><a href=\"/api/health\">/api/health</a></li>
      <li><a href=\"/search?q=example\">/search?q=example</a></li>
      <li><a href=\"/status/404\">/status/404</a></li>
      <li><a href=\"/status/500\">/status/500</a></li>
      <li><a href=\"/headers\">/headers</a></li>
      <li><a href=\"/slow?s=1\">/slow?s=1</a></li>
    </ul>

    <form method=\"GET\" action=\"/search\">
      <label>Search: <input name=\"q\" value=\"example\" /></label>
      <button type=\"submit\">Go</button>
    </form>
  </body>
</html>
"""


@app.get("/headers")
def headers(request: Request) -> dict[str, Any]:
    # Return a small, stable subset to keep output readable.
    interesting = [
        "host",
        "user-agent",
        "accept",
        "accept-encoding",
        "accept-language",
        "content-type",
    ]
    normalized = {k: v for k, v in request.headers.items() if k.lower() in interesting}
    return {"headers": normalized}


@app.get("/search")
def search(q: str = Query(default="", max_length=200)) -> JSONResponse:
    # Echo is intentionally escaped so this is a safe target.
    safe = html.escape(q)
    return JSONResponse({"query": safe, "results": [{"title": "Example", "snippet": f"You searched for: {safe}"}]})


@app.get("/status/{code}")
def status(code: int) -> PlainTextResponse:
    if code < 100 or code > 599:
        raise HTTPException(status_code=400, detail="invalid status code")
    return PlainTextResponse(f"status={code}\n", status_code=code)


@app.get("/slow")
async def slow(s: float = Query(default=0.25, ge=0.0, le=5.0)) -> dict[str, Any]:
    await asyncio.sleep(float(s))
    return {"slept_seconds": float(s), "time": _now_iso()}
