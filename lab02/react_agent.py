"""Lab 2: a ReAct agent from scratch (no framework).

Usage (run from the repository root):
    python lab02/react_agent.py              # run the 6 test questions, save evidence/trace_1..6.txt
    python lab02/react_agent.py "question"   # run one question (trace printed only)
    python lab02/react_agent.py --baseline   # Step 1: model alone, writes evidence/baseline.md
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv
from litellm import BadRequestError, RateLimitError, completion

from tools import TOOLS

litellm.suppress_debug_info = True   # hide the "Give Feedback / Get Help" banner on handled errors
load_dotenv()
MODEL = os.getenv("LLM_MODEL")
EVIDENCE = Path(__file__).parent / "evidence"

SYSTEM_PROMPT = """You are a helpful assistant for a trader at Makola Market in Accra.
You answer costing questions and quick factual questions.

You can use these tools:
- calculator: evaluates an arithmetic expression, e.g. 4*185 + 3*95. Use it for ALL arithmetic,
  including simple subtractions such as differences between years.
- wiki_lookup: returns the summary of a Wikipedia page. The input is the page title, e.g. Bono East Region.
  Use it for EVERY factual question (places, dates, people, organisations) before answering.
- finish: ends the task. The input is your final answer to the user.

You do NOT have function calling. Never call a tool directly; instead write the
action as plain text. Our code reads your text and runs the tool for you.

On every step reply in exactly this plain-text format and nothing else:
Thought: <your reasoning>
Action: calculator | wiki_lookup | finish
Action Input: <input for the tool, or the final answer if finish>

Rules:
- Use only one Action per reply, then stop. Never write an Observation yourself.
- Never do arithmetic in your head; always use the calculator.
- Never answer a factual question from memory; look it up with wiki_lookup first and
  base your answer on the Observation.
- If a tool gives an error or no result, say so honestly instead of guessing.
- Never repeat an action with the same input; the result will not change.
- If no tool is needed, use finish straight away."""

ACTION_RE = re.compile(
    r"Thought:[ \t]*(?P<thought>.+?)[ \t]*\n"
    r"[ \t]*Action:[ \t]*(?P<action>\w+)[ \t]*\n"
    r"[ \t]*Action Input:[ \t]*(?P<input>.*)",
    re.DOTALL,
)
REPLY_FIELD_RE = re.compile(r"^[ \t]*(?:Thought|Action|Action Input|Observation):",
                            re.MULTILINE)

FORMAT_HELP = ("Your reply could not be parsed. Reply in exactly this format:\n"
               "Thought: <your reasoning>\nAction: calculator | wiki_lookup | finish\n"
               "Action Input: <input>")


def parse(text):
    text = text.replace("\r\n", "\n").strip()
    match = ACTION_RE.fullmatch(text)
    if not match or len(REPLY_FIELD_RE.findall(text)) != 3:
        return None, None
    action_input = match["input"].strip()
    if not match["thought"].strip() or not action_input:
        return None, None
    return match["action"], action_input


NO_FUNCTIONS = {"role": "user", "content": (
    "Do not call functions. Write your next step as plain text in the format "
    "Thought:, Action:, Action Input:.")}


def _ask(messages, retries=5):
    # The Groq free tier has a tokens-per-minute limit. On HTTP 429 we wait for
    # the time Groq suggests (plus a margin) and try again instead of crashing.
    for attempt in range(retries + 1):
        try:
            resp = completion(model=MODEL, messages=messages,
                              temperature=0, stop=["Observation:"])
            return (resp.choices[0].message.content or "").strip()
        except RateLimitError as e:
            if attempt == retries:
                raise
            m = re.search(r"try again in ([\d.]+)s", str(e))
            wait = (float(m.group(1)) if m else 10) + 2
            print(f"[rate limited; waiting {wait:.0f}s before retrying]")
            time.sleep(wait)


def _failed_call(e):
    """If Groq rejected a native function call, return the call the model tried."""
    m = re.search(r'\{"error".*\}', str(e))
    if not m or "tool_use_failed" not in m.group(0):
        return None
    try:
        call = json.loads(json.loads(m.group(0))["error"]["failed_generation"])
    except (ValueError, KeyError, TypeError):
        call = None
    # The attempted call is sometimes not valid JSON; mark it as unreadable.
    return call if isinstance(call, dict) and call.get("name") else {"name": None}


def _call_to_text(call):
    """Rewrite a rejected native function call in our Thought/Action text format."""
    if not call["name"]:
        # Unreadable call: return an empty reply so the loop sends FORMAT_HELP.
        return ""
    args = call.get("arguments") or {}
    if isinstance(args, dict) and "Action" in args:
        # The model "called" a made-up tool (e.g. "assistant") whose arguments
        # are our own fields: {"Thought": ..., "Action": ..., "Action Input": ...}
        return (f"Thought: {args.get('Thought') or '[converted native function call]'}\n"
                f"Action: {args['Action']}\nAction Input: {args.get('Action Input', '')}")
    # The model called one of our tools directly, e.g. calculator(expression=...)
    value = next(iter(args.values()), "") if isinstance(args, dict) else args
    name = call.get("name")
    return (f"Thought: [no written reasoning: the model made a native function call, "
            f"converted to text] Use the {name} tool with input: {value}\n"
            f"Action: {name}\nAction Input: {value}")


def call_model(messages):
    # gpt-oss sometimes tries a native function call instead of writing text,
    # which Groq rejects (tool_use_failed), and sometimes returns an empty reply.
    # In both cases we retry once with a reminder to write plain text; if it
    # still calls a function, Groq returns the attempted call in the error and
    # we rewrite it in our text format.
    try:
        reply = _ask(messages)
        if reply:
            return reply
    except BadRequestError as e:
        if not _failed_call(e):
            raise
    try:
        return _ask(messages + [NO_FUNCTIONS])
    except BadRequestError as e:
        call = _failed_call(e)
        if not call:
            raise
        return _call_to_text(call)


def run_agent(question, max_steps=6):
    """Run the Thought -> Action -> Observation loop. Returns (answer, trace text)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    trace = []

    def log(line):
        print(line)
        trace.append(line)

    log(f"Question: {question}")
    log(f"Model: {MODEL}")
    log("")
    done = set()                                    # (action, input) pairs already run
    for step in range(1, max_steps + 1):
        log(f"--- Step {step} ---")
        reply = call_model(messages)                # think (deliberative)
        log(reply or "(empty reply from the model)")
        if reply:                                   # an empty turn confuses the model
            messages.append({"role": "assistant", "content": reply})

        action, action_input = parse(reply)
        if action is None:                          # unparseable or empty reply
            observation = f"{FORMAT_HELP}\nThe user's question is still: {question}"
        elif action == "finish":                    # termination
            log(f"\nFinal answer: {action_input}")
            return action_input, "\n".join(trace)
        elif action not in TOOLS:                   # unknown tool name
            observation = (f"Unknown action '{action}'. "
                           "Use one of: calculator, wiki_lookup, finish.")
        elif (action, action_input) in done:        # reactive rule: repeated action
            observation = ("You already ran this exact action and its result will not "
                           "change. Use the information you have, try a different input, "
                           "or finish and say honestly what you could not find.")
        else:                                       # act, then sense the result
            observation = TOOLS[action](action_input)
            done.add((action, action_input))

        log(f"Observation: {observation}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    answer = f"Stopped: reached max_steps ({max_steps}) without a final answer."
    log(f"\n{answer}")
    return answer, "\n".join(trace)


# Step 4 (budget) and Step 5 (five more questions)
QUESTIONS = [
    # 1. Budget question from Part A
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil "
    "at GHS 95 each. How much will I have left?",
    # 2. Needs both tools
    "What is the capital of the Bono East Region? If I travel there 3 times a month "
    "and each trip costs GHS 120, how much do I spend on the trips in a year?",
    # 3. Needs both tools
    "In what year was the University of Ghana founded, and how many years ago was "
    "that from 2026?",
    # 4. Wikipedia page that does not exist
    "Tell me about the Makola Flying Yam Festival of 1823.",
    # 5. Needs no tool
    "Hello! Can you help me today?",
    # 6. Deliberately badly worded
    "rice 185 4bag + oil 95 x3 ... 1200 cedis have, left how much??",
]


def _require_new_evidence(paths):
    existing = [str(path) for path in paths if path.exists() or path.is_symlink()]
    if existing:
        raise FileExistsError("refusing to overwrite " + ", ".join(existing))


def _write_evidence(path, content):
    with path.open("x", encoding="utf-8") as output:
        output.write(content)


def baseline():
    """Step 1: ask the model alone (no tools) and record the answers."""
    path = EVIDENCE / "baseline.md"
    _require_new_evidence([path])
    budget, facts = QUESTIONS[0], [
        ("What is the capital of the Bono East Region?", "Techiman"),
        ("In what year was the University of Ghana founded?", "1948"),
    ]
    rows = []
    for i in range(3):
        ans = call_model([{"role": "user", "content": budget}])
        rows.append((f"Budget run {i + 1}", ans, "175" in ans))
    for q, expected in facts:
        ans = call_model([{"role": "user", "content": q}])
        rows.append((q, ans, expected in ans))

    lines = ["# Lab 2 Baseline: the model on its own (no tools)", "",
             f"Model: `{MODEL}`", "",
             f"Budget question: {budget}", "",
             "Correct budget answer: GHS 175 (4x185 + 3x95 = 1025; 1200 - 1025 = 175).",
             "Correct facts: Techiman; 1948.", "",
             "| Question | Model answer | Correct? |", "|---|---|---|"]
    for q, ans, ok in rows:
        lines.append(f"| {q} | {ans.replace(chr(10), ' ').replace('|', '/')} | "
                     f"{'Correct' if ok else 'Incorrect'} |")
    lines += ["", "## Notes", "",
              "- How confident did the factual answers sound? (fill in)", ""]
    _write_evidence(path, "\n".join(lines))
    print("\n".join(lines))


def _batch():
    paths = [EVIDENCE / f"trace_{n}.txt" for n in range(1, len(QUESTIONS) + 1)]
    _require_new_evidence(paths)
    for n, (question, path) in enumerate(zip(QUESTIONS, paths), start=1):
        print(f"\n=========== Trace {n} ===========")
        try:
            _, trace = run_agent(question)
        except Exception as e:
            sys.exit(f"Lab 2 batch failed on trace {n} ({question}): {e}")
        _write_evidence(path, trace)
        time.sleep(20)                              # let the per-minute token budget refill


if __name__ == "__main__":
    if not MODEL:
        sys.exit("LLM_MODEL is not set. Copy .env.example to .env first.")
    # The model sometimes writes characters (e.g. U+202F) the Windows console can't show.
    sys.stdout.reconfigure(errors="replace")

    if len(sys.argv) > 1 and sys.argv[1] != "--baseline":
        run_agent(" ".join(sys.argv[1:]))
    else:
        try:
            EVIDENCE.mkdir(exist_ok=True)
            if len(sys.argv) > 1:
                baseline()
            else:
                _batch()
        except OSError as e:
            sys.exit(f"Could not save Lab 2 evidence: {e}")
