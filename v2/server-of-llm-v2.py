import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# ✅ Store chat history per session
session_memory = {}


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
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        url = "http://localhost:11434/api/chat"
        prompt = data.get("prompt", "Hi")
        session_id = data.get("user_id", "1")

        #
        if self.path == "/clear-session":
            if session_id and session_id in session_memory:
                del session_memory[session_id]
                self.send_response(200)
                self._set_headers()
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "Session cleared"}).encode("utf-8")
                )
            else:
                self.send_response(404)
                self._set_headers()
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Session not found"}).encode("utf-8")
                )
            return

        # ✅ Initialize or update session message list
        if session_id not in session_memory:
            session_memory[session_id] = []
        session_memory[session_id].append({"role": "user", "content": prompt})

        print("\033[34m" + f"Text=>{session_memory}" + "\033[0m", session_memory)
        payload = {
            # "model": "gemma3:1b",  # Replace with your model
            "model": "deepseek-r1:1.5b",  # Replace with your model
            "messages": session_memory[session_id],
        }

        try:
            self.send_response(200)
            self._set_headers()
            self.end_headers()

            ollama_response = requests.post(
                url,
                json=payload,
                stream=True,
            )

            full_response = ""
            print(ollama_response)

            for line in ollama_response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        json_data = json.loads(line)
                        if "message" in json_data and "content" in json_data["message"]:
                            content = json_data["message"]["content"]
                            full_response += (
                                content  # ✅ Collect entire assistant response
                            )
                            self.wfile.write(content.encode("utf-8"))
                            self.wfile.flush()
                    except json.JSONDecodeError:
                        pass

            # ✅ Append assistant response to memory
            session_memory[session_id].append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            self.send_response(500)
            self._set_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


def run(server_class=HTTPServer, handler_class=IntermediateHandler, port=5001):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Intermediate backend server running at http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
