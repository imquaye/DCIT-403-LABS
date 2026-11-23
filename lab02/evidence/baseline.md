# Lab 2 Baseline: the model on its own (no tools)

Model: `groq/openai/gpt-oss-20b`

Budget question: I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?

Correct budget answer: GHS 175 (4x185 + 3x95 = 1025; 1200 - 1025 = 175).
Correct facts: Techiman; 1948.

| Question | Model answer | Correct? |
|---|---|---|
| Budget run 1 | First, calculate the total cost of what you’re buying:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add those together:  \[ GHS\,740 + GHS\,285 = GHS\,1\,025 \]  You started with GHS 1,200. Subtract the total cost:  \[ GHS\,1\,200 - GHS\,1\,025 = GHS\,175 \]  **You will have GHS 175 left.** | Correct |
| Budget run 2 | First, calculate the total cost of what you’re buying:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add those together:  \[ GHS\,740 + GHS\,285 = GHS\,1\,025 \]  You started with GHS 1,200. Subtract the total cost:  \[ GHS\,1\,200 - GHS\,1\,025 = GHS\,175 \]  **You will have GHS 175 left.** | Correct |
| Budget run 3 | First, calculate the total cost of what you’re buying:  - **Rice:** 4 bags × GHS 185 = **GHS 740**   - **Oil:** 3 gallons × GHS 95 = **GHS 285**  Add those together:  \[ GHS\,740 + GHS\,285 = GHS\,1\,025 \]  You started with GHS 1,200. Subtract the total cost:  \[ GHS\,1\,200 - GHS\,1\,025 = GHS\,175 \]  **You will have GHS 175 left.** | Correct |
| What is the capital of the Bono East Region? | The capital of the Bono East Region is **Techiman**. | Correct |
| In what year was the University of Ghana founded? | The University of Ghana was founded in **1948** (originally as the University College of Gold Coast). | Correct |

## Notes

- The model answered both factual questions confidently without expressing uncertainty. Both answers were correct. The baseline achieved 5/5 correct answers, including all three budget calculations. However, the baseline model did not retrieve external evidence to verify its factual answers. The ReAct agent also completed all six test scenarios, demonstrating tool usage and error recovery rather than an accuracy improvement on the budget question.