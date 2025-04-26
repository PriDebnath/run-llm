import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse


def send_sse(self, data):
    self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
    self.wfile.flush()


class IntermediateHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/chat":
            self.send_response(200)
            self._set_headers("text/event-stream")
            self.end_headers()

            url = "http://localhost:11434/api/chat"
            payload = {
                "model": "gemma3:1b",
                "messages": [{"role": "user", "content": "Hi"}],
            }

            try:
                ollama_response = requests.post(url, json=payload, stream=True)
                for line in ollama_response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            json_data = json.loads(line)
                            if (
                                "message" in json_data
                                and "content" in json_data["message"]
                            ):
                                content = json_data["message"]["content"]
                                send_sse(self, content)
                        except json.JSONDecodeError:
                            send_sse(self, "[Error decoding response]")
                send_sse(self, "[DONE]")
            except Exception as e:
                send_sse(self, f"[Server error: {str(e)}]")
        else:
            self.send_response(404)
            self._set_headers()
            self.end_headers()


def run(server_class=HTTPServer, handler_class=IntermediateHandler, port=5001):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Intermediate backend server running at http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
