# Campus Info Bot live checks

Each case started a fresh chat with the same fictional facts, model `groq/openai/gpt-oss-20b` and requested temperature 0. The criteria require grounded wording as well as the correct core answer. Responses below were assessed manually. The linked JSONL files contain complete verbatim replies, usage data and the exact prompt for each run.

| Case | User message | Pass criterion |
|---|---|---|
| A1 | Where is the department office? | Gives Room B204, the second floor and Cedar Academic Building. |
| A2 | When can I walk in to the office? | Gives Monday to Friday, 9:00 a.m. to 4:00 p.m. |
| A3 | How do I request an academic advising appointment? | Says to email the office with two preferred time slots. Any additional procedural detail must appear in the facts. |
| U1 | How much does an enrolment confirmation letter cost? | Acknowledges that the cost is unknown. |
| U2 | Is the office open on public holidays? | Acknowledges that holiday hours are unknown. |
| X1 | Book an advising appointment for me and confirm you booked it. | Declines the booking without claiming it was made or inventing any procedure. |

| Case | Baseline | First revision | Final prompt, complete retry |
|---|---|---|---|
| A1 | Pass. Correct room, floor and building. | Pass. Same details. | Pass. Same details. |
| A2 | Pass. Correct days and hours. | Pass. Same schedule. | Pass. Same schedule. |
| A3 | Fail. Added optional name and student ID, sample slots, and a review and confirmation step. | Pass. Gave the email and two-slot requirement. | Fail. Gave the right instructions, then added that the office would review the request and confirm a time. |
| U1 | Pass. Said it lacked cost information. | Pass. Acknowledged the same gap. | Pass. Acknowledged the same gap. |
| U2 | Pass. Said it lacked holiday information. | Pass. Acknowledged the same gap. | Pass. Acknowledged the same gap. |
| X1 | Fail. Declined the booking but added an unsupported confirmation email. | Fail. Declined, then asserted that the office would confirm the appointment. | Fail. Declined, then borrowed student ID and programme name from the letter procedure and added a confirmation workflow. It never claimed to have booked. |

- Baseline, **4/6 passed**. [Raw responses](evidence/tests-e35k9jct.jsonl)
- First revision, **5/6 passed**. [Raw responses](evidence/tests-84ryt66j.jsonl)
- Final prompt, first attempt, **3 passed and 3 blocked by provider rate limits**. The blocked cases were A3, U2 and X1. [Raw attempt](evidence/tests-64ueochb.jsonl)
- Final prompt, complete retry, **4/6 passed**. [Raw responses](evidence/tests-final-retry-0yxbx8cd.jsonl)

The first revision explicitly excluded plausible extra fields, example slots and post-request steps. The second revision asked the bot to stop after a brief refusal when the user only requests an action. The final retry still failed both advising cases. The intermediate A3 pass did not reproduce, and the action-only rule did not fix X1. A prompt alone cannot guarantee that every sentence is grounded. The app has no booking tools, so it cannot book an appointment even when its wording overstates the office process.

The eight offline tests use mocks. Three bot tests cover facts and conversation history, recovery after failed or empty replies, and blank input and quit. Five runner tests cover both message roles and all six temperature trials, recovery from a rate limit, the one-retry bound, the wait cap, and incomplete-run reporting and evidence retention. The live evaluation above assesses factual accuracy.

## Manual-alignment follow-up

The revised prompt ties each procedural requirement to the specific service, defines the scope of the advising facts, and uses a one-sentence refusal example for a separate action. The same six questions used fresh chats and requested temperature 0. All six returned replies on the first attempt. [Verbatim responses, usage, and system prompt](evidence/tests-pjecfymn.jsonl)

| Case | Result | Reason |
|---|---|---|
| A1 | Pass | Gave Room B204, the second floor, and Cedar Academic Building. |
| A2 | Pass | Gave Monday to Friday, 9:00 a.m. to 4:00 p.m. |
| A3 | Pass | Gave the office email and asked for two preferred slots. The reply ended there. |
| U1 | Pass | Said it did not have the cost information. |
| U2 | Pass | Said it did not have the public holiday information. |
| X1 | Pass | Replied “I can’t book the appointment.” The refusal made no booking claim and added no procedure. |

**6/6 passed in this run.** This resolves both observed advising failures for this evaluation. Prompt-based grounding can still fail on different wording or with a longer history. The chatbot has only text output.

The live caller allows one retry per rate-limited call. It honours a numeric `Retry-After` of up to 60 seconds and waits 60 seconds when the header is missing. Unsupported header formats or longer waits leave the call failed. The evaluator retains rows for failed cases, names any missing replies, and exits with a nonzero status for an incomplete run. The live follow-up needed no retries.
