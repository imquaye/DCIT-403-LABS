# Campus Info Bot PEAS

| Component | Description |
|---|---|
| Performance measure | Give accurate and relevant answers supported by the supplied facts, use earlier messages when needed, state uncertainty about missing information, and describe actions honestly. |
| Environment | A terminal conversation with one user about a fictional department office, using a fixed local facts file for the session. |
| Actuators | Print text replies, status messages and a farewell in the terminal. |
| Sensors | Receive terminal input and read the local facts file. The model receives the facts and retained chat history with each request. |

## Environment properties

| Property | Classification | Justification |
|---|---|---|
| Observability | Partially observable | The bot sees what the user types and the supplied reference. Actual office conditions, unstated intentions and missing policies are outside its observations. |
| Number of agents | Single-agent | The bot is the only agent being designed and evaluated. In this task model the user supplies requests and context, with no other autonomous decision-maker in the service workflow. |
| Outcome predictability | Stochastic | Model replies can vary, and a text reply does not determine how the user will respond. Low temperature reduces sampling variation. |
| Dependence between decisions | Sequential | Earlier turns establish entities and preferences. A later request such as “How do I get one?” may depend on the service selected earlier. |
| Change during deliberation | Static | The reference is fixed during a session and the terminal collects the next user message after the bot answers. The underlying real-world office is outside this simulated environment. |
| State and action representation | Discrete | Inputs and outputs are represented by discrete text tokens and decisions occur at turn boundaries, even though the range of possible messages is large. |
