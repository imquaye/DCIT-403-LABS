"""Make six live LiteLLM calls and retain the response and usage for each."""
import json
import os
from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from litellm import RateLimitError, completion

LAB = Path(__file__).resolve().parent
EVIDENCE = LAB / "evidence"
PROMPT = "In one sentence, what is an intelligent agent?"
MAX_RATE_LIMIT_WAIT = 60


def configured_model():
    load_dotenv(LAB.parent / ".env")
    model = os.getenv("LLM_MODEL", "").strip()
    if not model:
        raise SystemExit("Set LLM_MODEL in the environment or repository .env.")
    return model


def call_model(model, messages, temperature):
    options = dict(model=model, messages=messages, temperature=temperature, timeout=30, num_retries=0)
    attempts = 1
    try:
        response = completion(**options)
    except RateLimitError as error:
        headers = getattr(error.response, "headers", {})
        retry_after = headers.get("retry-after")
        if retry_after is None:
            wait = MAX_RATE_LIMIT_WAIT
        else:
            try:
                wait = float(retry_after)
            except ValueError:
                raise error from None
        if not 0 <= wait <= MAX_RATE_LIMIT_WAIT:
            raise
        print(f"Provider rate limit. Retrying once in {wait:g} seconds.", flush=True)
        sleep(wait)
        attempts += 1
        response = completion(**options)
    reply = response.choices[0].message.content
    usage = getattr(response, "usage", None)
    return {
        "reply": reply,
        "attempts": attempts,
        "response_model": response.model,
        "usage": usage.model_dump(exclude_none=True) if usage is not None else None,
    }


class Evidence:
    """Append to a fresh JSONL file so interrupted runs retain completed calls."""

    def __init__(self, stem):
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(
            dir=EVIDENCE, prefix=f"{stem}-", suffix=".jsonl", delete=False
        ) as file:
            self.path = Path(file.name)
        print(f"Evidence file: {self.path}", flush=True)

    def record(self, row):
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    model = configured_model()
    evidence = Evidence("hello")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": PROMPT},
    ]
    incomplete = 0
    for temperature in (0, 1):
        for trial in range(1, 4):
            row = {"model": model, "temperature": temperature, "trial": trial, "messages": messages}
            try:
                row.update(call_model(model, messages, temperature))
            except Exception as error:
                row["error_type"] = type(error).__name__
            if not (row.get("reply") or "").strip() or row.get("usage") is None:
                incomplete += 1
            evidence.record(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    if incomplete:
        raise SystemExit(f"Incomplete temperature experiment: {incomplete} of 6 trials lack a reply or usage.")


if __name__ == "__main__":
    main()
