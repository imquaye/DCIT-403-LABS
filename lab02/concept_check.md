# Lab 2: Architectures: A ReAct Agent From Scratch: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Classify a thermostat, a chess engine and a ReAct agent as reactive, deliberative or hybrid, with one reason each.

Thermostat — Reactive: It responds directly to temperature changes using predefined rules, without planning future actions.

Chess engine — Deliberative: It evaluates possible moves and their consequences before deciding which move to make.

ReAct agent — Hybrid: It combines reasoning to decide which action to take with reacting to observations returned by tools.


## Q2. In the trace above, which lines are percepts, and which are actions?

The percepts are the user's original question and the observations returned by the calculator, such as Observation: 1025 and Observation: 175.

The actions are the tool calls, including Action: calculator, and the final Action: finish.

The Thought lines represent the agent's reasoning, while Action Input specifies what is passed to the selected tool or returned as the final answer.


## Q3. Why do we pass `stop=["Observation:"]` when calling the model?

We use stop=["Observation:"] to prevent the model from generating its own observations. The model should only decide which action to take, while our Python code executes the tool and provides the actual result.

This makes the agent more reliable because it uses real tool outputs instead of invented results.


## Q4. Map the trace above to the BDI terms belief, desire and intention.

Belief: The agent knows that the trader has GHS 1,200, rice costs GHS 185 per bag, and oil costs GHS 95 per gallon. It later learns that the total expenses are GHS 1,025.

Desire: The agent wants to determine how much money the trader will have left after buying the items.

Intention: The agent decides to use the calculator to find the total expenses, subtract them from GHS 1,200, and provide the remaining balance of GHS 175.

