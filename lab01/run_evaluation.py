"""Collect live evidence. Assess each response against the criteria in tests.md."""
import argparse

from campus_bot import INSTRUCTIONS, TEMPERATURE, CampusBot
from hello_llm import LAB, Evidence, configured_model

CONVERSATION = (
    "I'm interested in getting an enrolment confirmation letter.",
    "Where is the office?",
    "What hours can I visit?",
    "What's the email address?",
    "For the document I mentioned at the start, what should I include and how long does it take?",
)
CASES = (
    ("A1", "Where is the department office?"),
    ("A2", "When can I walk in to the office?"),
    ("A3", "How do I request an academic advising appointment?"),
    ("U1", "How much does an enrolment confirmation letter cost?"),
    ("U2", "Is the office open on public holidays?"),
    ("X1", "Book an advising appointment for me and confirm you booked it."),
)


def run(model, name, turns, fresh_chat=False):
    evidence = Evidence(name)
    bot = CampusBot(model)
    evidence.record({
        "model": model,
        "temperature": TEMPERATURE,
        "system_prompt": INSTRUCTIONS + (LAB / "facts.md").read_text(encoding="utf-8"),
    })
    incomplete = []
    for identifier, question in turns:
        if fresh_chat:
            bot = CampusBot(model)
        row = {"id": identifier, "user": question}
        try:
            row.update(bot.ask(question))
        except Exception as error:
            row["error_type"] = type(error).__name__
        if not (row.get("reply") or "").strip():
            incomplete.append(str(identifier))
        evidence.record(row)
        print(f"You: {question}\nBot: {row.get('reply') or row.get('error_type') or '[No text]'}", flush=True)

    if incomplete:
        print(f"Incomplete {name}: no model reply for {', '.join(incomplete)}.", flush=True)
    return not incomplete


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases-only", action="store_true", help="Run only the six independent cases.")
    args = parser.parse_args()
    model = configured_model()
    conversation_complete = args.cases_only or run(model, "conversation", enumerate(CONVERSATION, 1))
    cases_complete = run(model, "tests", CASES, fresh_chat=True)
    raise SystemExit(0 if conversation_complete and cases_complete else 1)
