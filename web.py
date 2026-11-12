"""Serve the F.R.I.D.A.Y. dashboard on loopback."""

import argparse
import json
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from friday import MODEL, chat

DASHBOARD = Path(__file__).with_name("index.html")
MAX_BODY = 320 * 1024


class Dashboard(BaseHTTPRequestHandler):
    def reply(self, status, content, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def json_reply(self, status, **data):
        self.reply(status, json.dumps(data).encode(), "application/json")

    def do_GET(self):
        if self.path == "/":
            self.reply(200, DASHBOARD.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/config":
            self.json_reply(200, model=self.server.model)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != host or self.headers.get("Origin") != f"http://{host}":
            self.json_reply(403, error="Open the dashboard using its printed local URL.")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                raise ValueError
            payload = json.loads(self.rfile.read(length))
            prompt = payload["prompt"]
            turns = payload["turns"]
            if not isinstance(prompt, str) or not (len(prompt) <= 4000 and prompt.strip()):
                raise ValueError
            if not isinstance(turns, list) or len(turns) > 6:
                raise ValueError
            history = deque(maxlen=12)
            for turn in turns:
                for role in ("user", "assistant"):
                    content = turn[role]
                    if not isinstance(content, str) or len(content) > 4000:
                        raise ValueError
                    history.append({"role": role, "content": content})
        except (ValueError, KeyError, TypeError):
            self.json_reply(400, error="Send a message between 1 and 4,000 characters.")
            return
        try:
            answer = chat(self.server.model, history, prompt.strip())
        except RuntimeError as error:
            self.json_reply(502, error=str(error))
            return
        self.json_reply(200, answer=answer)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Dashboard) as server:
        server.model = args.model
        print(f"Open http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
