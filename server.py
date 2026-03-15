"""HTTP server wrapper around chat-client-toy's OllamaClient.

Exposes an OpenAI-compatible /v1/chat/completions endpoint so other
services (like restaurant-chat) can use this as their LLM gateway.

Usage:
    uv run python server.py [--port 8100] [--model llama3.1:8b]
"""

import argparse
import asyncio
import json
import uuid
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from providers.OllamaClient import AsyncOllamaClient


def load_restaurant(slug: str) -> dict:
    """Load restaurant config and menu from restaurants/<slug>/"""
    restaurant_dir = Path(__file__).parent / "restaurants" / slug
    if not restaurant_dir.exists():
        return {}
    config = json.loads((restaurant_dir / "config.json").read_text())
    config["menu"] = (restaurant_dir / "menu.md").read_text()
    return config


def create_handler(model: str, restaurant: dict | None = None):
    class ChatHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/v1/chat/completions":
                self.send_error(404)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))

            messages = body.get("messages", [])
            req_model = body.get("model", model)

            # Extract system prompt
            system = ""
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    chat_messages.append(msg)

            # Inject restaurant context if available
            if restaurant:
                system += f"\n\nRestaurant: {restaurant['name']}\nCuisine: {restaurant.get('cuisine', '')}\n\n{restaurant['menu']}"

            # Create a fresh client per request
            # Disable tools in restaurant mode — menu is in the system prompt
            from tools.tools import ToolRegistry
            tool_reg = ToolRegistry() if restaurant else None
            kwargs = {"model": req_model, "instructions": system}
            if tool_reg is not None:
                kwargs["tool_registry"] = tool_reg
            client = AsyncOllamaClient(**kwargs)

            # Build conversation history from prior messages
            from providers.models import Conversation
            for msg in chat_messages[:-1]:
                if msg["role"] in ("user", "assistant"):
                    client.conversation_history.append(Conversation(role=msg["role"], content=msg["content"]))

            # Generate response for the last user message
            last_msg = chat_messages[-1]["content"] if chat_messages else ""
            loop = asyncio.new_event_loop()
            try:
                reply = loop.run_until_complete(client.generate_response(last_msg))
            finally:
                loop.close()

            # Return OpenAI-compatible response
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "model": req_model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": reply},
                        "finish_reason": "stop",
                    }
                ],
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        def log_message(self, format, *args):
            print(f"[chat-client-toy] {args[0]}")

    return ChatHandler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8100)
    parser.add_argument("--model", default="llama3.1:8b")
    parser.add_argument("--restaurant", default=None, help="Restaurant slug (folder name in restaurants/)")
    args = parser.parse_args()

    restaurant = load_restaurant(args.restaurant) if args.restaurant else None
    server = HTTPServer(("0.0.0.0", args.port), create_handler(args.model, restaurant))
    import sys
    print(f"🧠 chat-client-toy gateway on http://localhost:{args.port}/v1/chat/completions", flush=True)
    print(f"   Model: {args.model}", flush=True)
    if restaurant:
        print(f"   Restaurant: {restaurant['name']}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
