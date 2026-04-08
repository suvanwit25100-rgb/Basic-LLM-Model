"""
Space & Physics Tutor — Flask Backend
Serves a chat UI and proxies messages to a locally fine-tuned
Llama 3.2 model via Apple's mlx-lm library.
"""

import os
from flask import Flask, render_template, request, jsonify
from mlx_lm import load, generate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
ADAPTER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adapters")
MAX_TOKENS = 512

SYSTEM_PROMPT = (
    "You are an expert Space & Physics Tutor. "
    "Provide clear, detailed, scientifically accurate explanations. "
    "Use step-by-step reasoning when solving physics problems. "
    "Be encouraging to students and use real-world examples "
    "involving space, astrophysics, and cosmology when relevant."
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

    return jsonify({"response": response_text.strip()})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
