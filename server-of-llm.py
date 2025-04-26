import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer


class IntermediateHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_POST(self):

        if self.path == "/chat":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            url = "http://localhost:11434/api/chat"

            payload = {
                "model": "gemma3:1b",  # Replace with the model name you're using
                "messages": [{"role": "user", "content": "What is Python?"}],
            }
            print(payload)
            try:
                # Forward the request to Ollama
                print("tryinggggg")

                ollama_response = requests.post(
                    url,
                    # headers={"Content-Type": "application/json"},
                    json=payload,
                    stream=True,
                )
                # just printing the response for now . make send to frontend and display it one by one

                for line in ollama_response.iter_lines(decode_unicode=True):
                    if line:  # Ignore empty lines
                        try:
                            # Parse each line as a JSON object
                            json_data = json.loads(line)
                            # Extract and print the assistant's message content
                            if (
                                "message" in json_data
                                and "content" in json_data["message"]
                            ):
                                print(json_data["message"]["content"], end="")
                        except json.JSONDecodeError:
                            print(f"\nFailed to parse line: {line}")

            except Exception as e:
                self.send_response(500)
                self._set_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
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
