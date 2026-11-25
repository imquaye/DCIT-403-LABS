# Lab 1: Agents Then and Now: PEAS and Your First LLM Call

**Topic:** Agent definitions, PEAS, environment types, the LLM as reasoning engine

**Style:** Standalone, code

Instructions are in the DCIT 403 Laboratory Manual (version 2), Lab 1.

## Deliverables

- `hello_llm.py`, `peas.md`, `facts.md`, `campus_bot.py`, `tests.md`
- `concept_check.md`
- `evidence/` with at least one screenshot of a conversation
- `diagnostic/` (Wednesday)

Put outputs, traces, logs and screenshots in `evidence/`. Answer `concept_check.md` before the Wednesday session. Steps marked Independent in the manual are done on your own between the Thursday and Wednesday labs.

## Run and review

From the repository root, with Python 3.11+, LiteLLM, `LLM_MODEL` and the configured provider's key available:

```sh
python lab01/hello_llm.py
python lab01/campus_bot.py
python lab01/run_evaluation.py
python -m unittest discover -s lab01 -v
```

The experiment commands create fresh evidence files. See [the evidence index](evidence/README.md) and [the scored live evaluation](tests.md).

The README lists an individual Wednesday diagnostic with a `diagnostic/` deliverable. Consult the manual or the instructor for the specific prompt, format and submission instructions. The repository also asks you to answer the concept check in your own words before Wednesday. Review the assisted study draft in [concept_check.md](concept_check.md) and restate the explanations yourself for that independent requirement.
