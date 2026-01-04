import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient

from backend.main import create_app


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = b"<!doctype html><html><head><!--secret--></head><body><h1>Hello</h1></body></html>"
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A002
        # Silence server logging in tests.
        return


def _start_server() -> tuple[HTTPServer, threading.Thread, str]:
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    host, port = server.server_address
    url = f"http://{host}:{port}/"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, url


def _graph(url: str) -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "a",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "a:out:1", "kind": "output"}],
                "config": {"initial_state": {"target_url": url}},
            },
            {
                "id": "b",
                "type": "browser",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "b:in:1", "kind": "input"},
                    {"id": "b:out:1", "kind": "output"},
                ],
                "config": {
                    "action": "navigate",
                    "url_key": "target_url",
                    "observation_mode": "source_inspector",
                    "output_key": "browser_output",
                },
            },
            {
                "id": "c",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "c:in:1", "kind": "input"}],
                "config": {"result_key": "result"},
            },
        ],
        "edges": [
            {"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}},
            {"id": "e2", "from": {"nodeId": "b", "portId": "b:out:1"}, "to": {"nodeId": "c", "portId": "c:in:1"}},
        ],
    }


def test_e2e_run_fetches_html_and_records_trace() -> None:
    server, thread, url = _start_server()

    try:
        client = TestClient(create_app())
        created = client.post("/api/run", json={"graph": _graph(url), "mode": "run"})
        assert created.status_code == 200
        run_id = created.json()["run_id"]

        final = None
        for _ in range(100):
            got = client.get(f"/api/run/{run_id}")
            assert got.status_code == 200
            data = got.json()
            if data["status"] != "running":
                final = data
                break
            time.sleep(0.01)

        assert final is not None
        assert final["status"] == "completed"

        # Ensure we saw the browser step and that it captured HTML.
        browser_step = next(s for s in final["trace"] if s["node_id"] == "b")
        out = browser_step["output"]["browser_output"]

        assert "html_source" in out
        assert "Hello" in out["html_source"]
        assert "html_cleaned" in out
        # build_html_cleaned extracts comments into a header.
        assert "EXTRACTED_COMMENTS" in out["html_cleaned"]

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)
