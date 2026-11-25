"""Run the Wednesday diagnostic with the Lab 1 model configuration."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

DIAGNOSTIC = Path(__file__).resolve().parent
REPOSITORY = DIAGNOSTIC.parents[1]


def read_questions(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    questions = [line for line in map(str.strip, lines) if line and not line.startswith("#")]
    if len(questions) != 3:
        raise ValueError(f"Expected exactly three questions in {path.name}; found {len(questions)}.")
    return questions


def ask(model, question):
    response = completion(
        model=model,
        messages=[{"role": "user", "content": question}],
        temperature=0,
        timeout=30,
        num_retries=0,
    )
    reply = response.choices[0].message.content if response.choices else None
    tokens = getattr(getattr(response, "usage", None), "total_tokens", None)
    if not reply or not reply.strip():
        raise ValueError("The model returned an empty reply.")
    if type(tokens) is not int or tokens < 0:
        raise ValueError("The provider did not report valid total token usage.")
    return reply, tokens


def main(directory=DIAGNOSTIC):
    load_dotenv(REPOSITORY / ".env")
    model = os.getenv("LLM_MODEL", "").strip()
    if not model:
        print("Set LLM_MODEL in your environment or the repository .env, then run the diagnostic again.", file=sys.stderr)
        return 1

    try:
        questions = read_questions(directory / "questions.txt")
    except (OSError, ValueError) as error:
        print(f"Cannot load diagnostic questions. {error}", file=sys.stderr)
        return 1

    rows = ["# Wednesday diagnostic", "", f"Model: `{model}`", ""]
    total = 0
    failed = False
    for index, question in enumerate(questions, 1):
        rows.extend([f"## Question {index}", "", question, ""])
        try:
            reply, tokens = ask(model, question)
        except Exception as error:
            # Provider exception text can include request configuration.
            print(f"Question {index} failed ({type(error).__name__}).", file=sys.stderr)
            rows.extend([f"**Unavailable ({type(error).__name__}).**", ""])
            failed = True
            continue
        total += tokens
        rows.extend([reply, "", f"Total tokens for this question: **{tokens}**", ""])

    if failed:
        rows.extend(["**Incomplete run.**", "", f"Tokens reported for successful calls: **{total}**", ""])
    else:
        rows.extend([f"Combined total tokens: **{total}**", ""])

    output = directory / ("answers-incomplete.md" if failed else "answers.md")
    try:
        output.write_text("\n".join(rows), encoding="utf-8")
    except OSError as error:
        print(f"Cannot write diagnostic output. {error}", file=sys.stderr)
        return 1
    print(f"Saved {output}", flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
