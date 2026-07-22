"""
app.py

Flask application for the AI Assistant project.

Routes:
    /                    Main interface: pick a function, a prompt style,
                         enter input, get a response.
    /feedback            POST endpoint that records yes/no feedback for a
                         given response into feedback_log.json.
    /feedback-summary    Simple dashboard showing aggregate feedback stats,
                         broken down by function and by prompt variant.

Requirement mapping (see README.md for the full explanation):
    Functionality        -> prompts.FUNCTIONS (answer / summarize / creative / advice)
    Prompt Design        -> prompts.py (3 variants per function)
    User Interaction     -> index() route + templates/index.html
    Feedback Loop        -> submit_feedback() + feedback_summary() + feedback_log.json
"""

import json
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

from prompts import FUNCTIONS
from llm_client import generate_response, LLMConfigError, LLMRequestError

# Load variables from a local .env file (if present) into the environment.
# This lets you just paste your API key into .env instead of using export/set
# commands in the terminal every time.
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

FEEDBACK_LOG_PATH = os.path.join(os.path.dirname(__file__), "feedback_log.json")

# In-memory session history (kept simple: one shared list for the demo).
# A real multi-user app would key this by session ID; that's out of scope here.
SESSION_HISTORY = []


# ------------------------------------------------------------------
# Feedback log helpers
# ------------------------------------------------------------------

def _load_feedback_log():
    if not os.path.exists(FEEDBACK_LOG_PATH):
        return []
    try:
        with open(FEEDBACK_LOG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_feedback_log(entries):
    with open(FEEDBACK_LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def _append_feedback_entry(entry: dict):
    entries = _load_feedback_log()
    entries.append(entry)
    _save_feedback_log(entries)


# ------------------------------------------------------------------
# Main interface
# ------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    selected_function = request.form.get("function_key", "answer")
    selected_prompt_variant = request.form.get("prompt_variant")
    user_input = ""
    response_text = None
    error_message = None
    response_id = None

    if selected_function not in FUNCTIONS:
        selected_function = "answer"

    function_config = FUNCTIONS[selected_function]
    prompt_options = function_config["prompts"]

    if not selected_prompt_variant or selected_prompt_variant not in prompt_options:
        selected_prompt_variant = next(iter(prompt_options))

    if request.method == "POST":
        field_name = function_config["field_name"]
        user_input = request.form.get(field_name, "").strip()

        if not user_input:
            error_message = "Please enter some input before submitting."
        else:
            template = prompt_options[selected_prompt_variant]["template"]
            formatted_prompt = template.format(**{field_name: user_input})

            try:
                response_text = generate_response(formatted_prompt)
                response_id = str(uuid.uuid4())

                SESSION_HISTORY.append({
                    "id": response_id,
                    "function_key": selected_function,
                    "function_label": function_config["label"],
                    "prompt_variant": selected_prompt_variant,
                    "prompt_variant_label": prompt_options[selected_prompt_variant]["label"],
                    "user_input": user_input,
                    "response_text": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            except LLMConfigError as e:
                error_message = f"Configuration problem: {e}"
            except LLMRequestError as e:
                error_message = f"The assistant couldn't get a response right now: {e}"

    return render_template(
        "index.html",
        functions=FUNCTIONS,
        selected_function=selected_function,
        function_config=function_config,
        selected_prompt_variant=selected_prompt_variant,
        user_input=user_input,
        response_text=response_text,
        response_id=response_id,
        error_message=error_message,
        history=list(reversed(SESSION_HISTORY[-10:])),  # last 10, newest first
    )


# ------------------------------------------------------------------
# Feedback submission
# ------------------------------------------------------------------

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    response_id = request.form.get("response_id")
    was_helpful = request.form.get("was_helpful")  # "yes" or "no"

    match = next((h for h in SESSION_HISTORY if h["id"] == response_id), None)

    if match is not None and was_helpful in ("yes", "no"):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "function_key": match["function_key"],
            "function_label": match["function_label"],
            "prompt_variant": match["prompt_variant"],
            "prompt_variant_label": match["prompt_variant_label"],
            "user_input": match["user_input"],
            "response_text": match["response_text"],
            "was_helpful": was_helpful,
        }
        _append_feedback_entry(entry)
        flash("Thanks for your feedback!", "success")
    else:
        flash("Couldn't record feedback for that response.", "error")

    return redirect(url_for("index"))


# ------------------------------------------------------------------
# Feedback summary dashboard
# ------------------------------------------------------------------

@app.route("/feedback-summary")
def feedback_summary():
    entries = _load_feedback_log()

    total = len(entries)
    helpful_count = sum(1 for e in entries if e.get("was_helpful") == "yes")
    helpful_pct = round((helpful_count / total) * 100, 1) if total else 0

    by_function = {}
    by_prompt_variant = {}

    for e in entries:
        f_label = e.get("function_label", "Unknown")
        by_function.setdefault(f_label, {"total": 0, "helpful": 0})
        by_function[f_label]["total"] += 1
        if e.get("was_helpful") == "yes":
            by_function[f_label]["helpful"] += 1

        key = f"{e.get('function_label', 'Unknown')} — {e.get('prompt_variant_label', 'Unknown')}"
        by_prompt_variant.setdefault(key, {"total": 0, "helpful": 0})
        by_prompt_variant[key]["total"] += 1
        if e.get("was_helpful") == "yes":
            by_prompt_variant[key]["helpful"] += 1

    def _with_pct(d):
        out = {}
        for k, v in d.items():
            pct = round((v["helpful"] / v["total"]) * 100, 1) if v["total"] else 0
            out[k] = {**v, "pct": pct}
        return out

    return render_template(
        "feedback_summary.html",
        total=total,
        helpful_count=helpful_count,
        helpful_pct=helpful_pct,
        by_function=_with_pct(by_function),
        by_prompt_variant=_with_pct(by_prompt_variant),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
