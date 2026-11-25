# Lab 1 evidence

## Earlier temperature trials

Six independent calls used the same prompt and requested model `groq/openai/gpt-oss-20b`. Groq reported `openai/gpt-oss-20b` in each response. [Verbatim replies and token usage](hello-i7_o79e9.jsonl)

| Temperature | Trial | Prompt tokens | Completion tokens | Total tokens |
|---|---|---|---|---|
| 0 | 1 | 83 | 283 | 366 |
| 0 | 2 | 83 | 283 | 366 |
| 0 | 3 | 83 | 283 | 366 |
| 1 | 1 | 83 | 129 | 212 |
| 1 | 2 | 83 | 68 | 151 |
| 1 | 3 | 83 | 250 | 333 |

At requested temperature 0, all replies were “Welcome to the Department of Computer Science!” At temperature 1, all three sentences differed, including the department name and whether the greeting included a tagline. The higher-temperature sample also had a wider range of completion token counts. Groq counted reasoning tokens in completion usage, so these counts exceed the visible reply lengths. Three trials per setting show what happened in this run and cannot establish universal determinism or a general cost difference.

## Conversation

The [readable five-turn transcript](conversation-transcript.txt) reproduces the user messages and replies from a [live conversation run](conversation-x6yqqa9t.jsonl). That run used the earlier prompt that tells the bot to give a brief refusal and stop for action-only requests. The same prompt was used in the [complete six-case retry that scored 4/6](tests-final-retry-0yxbx8cd.jsonl). The later service-specific prompt used for the 6/6 evaluation is preserved in [the final evaluation JSONL](tests-pjecfymn.jsonl).

The [terminal screenshot](campus_bot_screenshot.png) captures a separate live five-turn session with the same questions and different replies. Both sessions show the bot resolving the fifth turn's reference to the enrolment confirmation letter and giving the required student ID and programme name and a three-working-day turnaround. The fictional facts describe that turnaround as typical.

The [terminal smoke test](terminal-demo.txt) captured a live first reply, rate-limit messages and the goodbye on quit. See [tests.md](../tests.md) for the live test criteria, prompt iterations and individual results.

## Earlier temperature trials with the manual question only

The manual question supplied for this exercise was “In one sentence, what is an intelligent agent?” The six independent Groq calls below used that exact prompt. [Verbatim answers and provider usage](hello-a3shjfp_.jsonl)

| Temperature | Trial | Prompt tokens | Completion tokens | Total tokens |
|---|---|---|---|---|
| 0 | 1 | 81 | 90 | 171 |
| 0 | 2 | 81 | 90 | 171 |
| 0 | 3 | 81 | 90 | 171 |
| 1 | 1 | 81 | 85 | 166 |
| 1 | 2 | 81 | 159 | 240 |
| 1 | 3 | 81 | 106 | 187 |

At requested temperature 0, all three responses used the same one-sentence definition. At temperature 1, all three still described perceiving an environment and acting toward goals, but the wording varied. One closely resembled the temperature-0 definition, one used “computational system” and “specified objectives,” and one added knowledge, reasoning and learning. Prompt usage stayed at 81 tokens. The provider included reasoning tokens in completion usage, so the totals reflect more than the visible sentence. These six calls show the variation observed for this prompt and model.

The prompt follow-up passed all six chatbot cases. [New raw case evidence](tests-pjecfymn.jsonl) · [Scoring and reasons](../tests.md#manual-alignment-follow-up)

## Final temperature trials with both message roles

Each Groq call used the system message “You are a helpful assistant.” followed by the user message “In one sentence, what is an intelligent agent?” All six calls succeeded on the first attempt. [Exact message payloads, verbatim replies, and token usage](hello-6jirp9r9.jsonl)

| Requested temperature | Trial | Prompt tokens | Completion tokens | Total tokens |
|---|---|---|---|---|
| 0 | 1 | 90 | 95 | 185 |
| 0 | 2 | 90 | 95 | 185 |
| 0 | 3 | 90 | 95 | 185 |
| 1 | 1 | 90 | 126 | 216 |
| 1 | 2 | 90 | 108 | 198 |
| 1 | 3 | 90 | 129 | 219 |

The three temperature-0 replies were identical. At temperature 1, all three definitions differed. They added details about beliefs and intentions, internal models and rewards, or sensors and actuators. All six kept the core idea of perceiving an environment and acting to achieve goals. The counts describe this run, and completion usage includes provider-reported reasoning tokens.
