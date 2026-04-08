"""
Space & Physics Tutor — Flask Backend
Serves a chat UI and proxies messages to a locally fine-tuned
Llama 3.2 model via Apple's mlx-lm library.
"""

import os
import re
from flask import Flask, render_template, request, jsonify
from mlx_lm import load, generate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
ADAPTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adapters")
MAX_TOKENS = 1024

SYSTEM_PROMPT = (
    "You are an expert Space & Physics Tutor. "
    "Always provide complete, well-structured, and scientifically accurate answers. "
    "Format your responses using markdown: use **bold** for key terms, "
    "numbered lists for step-by-step reasoning, and bullet points for related concepts. "
    "Keep answers focused and self-contained — always finish your thoughts fully. "
    "Use real-world examples from space, astrophysics, and cosmology. "
    "Be encouraging and enthusiastic about physics."
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load model + adapter weights once at startup
# ---------------------------------------------------------------------------
print("\n🚀  Loading base model and adapter weights…")
print(f"    Base model : {BASE_MODEL}")
print(f"    Adapter    : {ADAPTER_PATH}")

model, tokenizer = load(BASE_MODEL, adapter_path=ADAPTER_PATH)

print("✅  Model loaded and ready!\n")


def trim_to_complete(text: str) -> str:
    """
    Trim generated text to the last complete sentence so responses
    never end mid-word or mid-sentence.
    """
    text = text.strip()
    if not text:
        return text

    # Already ends cleanly
    if text[-1] in '.!?"':
        return text

    # Find the last sentence-ending punctuation
    match = None
    for m in re.finditer(r'[.!?](?:\s|$)', text):
        match = m

    if match:
        return text[: match.end()].strip()

    # Fallback: trim at last newline to keep complete lines
    last_nl = text.rfind('\n')
    if last_nl > len(text) // 3:
        return text[:last_nl].strip()

    # Ultimate fallback: return as-is rather than empty
    return text

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Accept a user message, run it through the fine-tuned model,
    and return the generated response.
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Build the chat-template prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Generate
    response_text = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        verbose=False,
    )

    # Trim to the last complete sentence to avoid cut-off output
    clean_response = trim_to_complete(response_text)

    return jsonify({"response": clean_response})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
