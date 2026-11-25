# Lab 1: Agents Then and Now: PEAS and Your First LLM Call: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Give the PEAS description of a self-checkout machine at a supermarket.

**Performance** includes correct prices and totals, completed payments, short queues and correct handling of restricted items. **Environment** includes the shopper, products, checkout station, store systems and attendants. **Actuators** include the display, speaker, receipt printer and messages to the payment system or attendant. **Sensors** include the barcode scanner, bagging scale, touchscreen and card reader.


## Q2. Is the Campus Info Bot's environment episodic or sequential? Justify your answer using what the bot needs to remember.

The environment is sequential. If a user asks about an enrolment confirmation letter and later asks “How long does it take?”, the bot needs the earlier turn to identify what “it” means. Previous replies can also establish context for later choices.


## Q3. Which part of an LLM agent plays the role of the percept sequence?

The percept sequence is the history of observations available to the agent. In the chat implementation, the sequence of user messages forms its conversational observations, and the loaded facts provide an additional observation of the reference. The full message list also contains instructions and earlier agent actions, which are preserved as context.


## Q4. An agent gives a wrong office location because its facts block was out of date. Was it irrational? Explain.

The incorrect answer alone does not establish irrationality. Rationality depends on what the agent could reasonably infer from its observations, its knowledge and its objective when it acted. If the facts were its only authorised source and it had no indication they were stale, relying on them could be rational. If it could see a freshness warning or contradictory evidence, appropriate behaviour would include qualifying the answer or acknowledging uncertainty.
