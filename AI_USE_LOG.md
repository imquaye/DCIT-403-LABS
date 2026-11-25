# AI-Use Log

## Lab 2 – Architectures: A ReAct Agent From Scratch

| Date | Lab | Tool | What I asked | What I used | What I changed or checked |
|---|---|---|---|---|---|
| 23 Nov 2026 | Lab 2 | ChatGPT | Asked for an explanation of the ReAct architecture, lab requirements and GitHub Codespaces setup. | Used the explanations to understand the agent's components, experiments and setup procedure. | Verified the Python environment, installed libraries and Groq API connection. |
| 23 Nov 2026 | Lab 2 | Groq (gpt-oss-20b) | Executed five baseline questions and six ReAct test scenarios. | Collected model responses and agent traces as experimental evidence. | Verified the five baseline answers, reviewed all six traces and identified recovery from invalid calculator input and an empty model response. |
| 23 Nov 2026 | Lab 2 | OpenAI Codex | Asked Codex to inspect the repository, check Lab 2 deliverables, identify errors and run non-destructive checks. | Used the audit results to identify weaknesses in Wikipedia error handling, ReAct action parsing and evidence protection. | Reviewed the findings against the laboratory manual and confirmed that the required implementation files and experimental evidence were present. |
| 23 Nov 2026 | Lab 2 | OpenAI Codex and ChatGPT | Requested improvements to Wikipedia error handling, action parsing and protection against accidental overwriting of experimental evidence. | Used AI-assisted code corrections and mocked tests to strengthen the ReAct agent. | Reviewed the changes, restored the required LiteLLM `stop=["Observation:"]` parameter, verified the corrections and confirmed that the original baseline and six traces remained unchanged. |
| 24 Nov 2026 | Lab 2 | OpenAI Codex and ChatGPT | Requested an additional regression test reproducing the malformed calculator expression and recovery recorded in Trace 1. | Used Codex to add a targeted offline test and ChatGPT to review the testing approach. | Ran the complete test suite in GitHub Codespaces. All eight automated tests passed. Confirmed that the original evidence was unchanged and pushed the updated test to GitHub. |

### Collaboration Note

The initial Python implementation was developed collaboratively using one teammate's repository. We worked from that shared implementation before transferring the code into our individual repositories.

I transferred the shared implementation into my repository, configured my own model access, executed the baseline and ReAct experiments, reviewed the experimental evidence and verified the improvements made during debugging and testing.

I also ran the automated test suite, confirmed that all eight tests passed, and committed and pushed my completed Lab 2 work to my individual GitHub repository.

### Individual Repository

https://github.com/imquaye/DCIT-403-LABS

### AI-Use Declaration

AI tools were used to support understanding, debugging, code review and testing. The experimental results reported for Lab 2 came from the actual baseline and ReAct runs, while the subsequent regression tests used mocked model responses.

The original experimental evidence was preserved. AI assistance and the collaborative nature of the initial implementation have been disclosed in this log.


## Lab 1 – AI-Use Log

| Date | Lab | Tool | What I asked | What I used | What I changed or checked |
|---|---|---|---|---|---|
| 24–25 Nov 2026 | Lab 1 | OpenAI Codex | Code assistance, debugging and testing. | Python implementation and diagnostic support. | Functional and offline tests. |
| 24–25 Nov 2026 | Lab 1 | Groq | LLM inference and temperature experiments. | Model responses and token usage. | Experimental outputs and results. |
| 24–25 Nov 2026 | Lab 1 | ChatGPT | Technical review and verification. | Code review feedback. | Evidence and test results. |