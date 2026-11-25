"""A terminal Campus Info Bot grounded in the lab's fictional facts."""
from hello_llm import LAB, call_model, configured_model

TEMPERATURE = 0
INSTRUCTIONS = """You are the Campus Info Bot for a fictional university department.
Give the shortest useful answer supported by the department reference.
Use conversation history to resolve what the user means. The reference is the sole source of office facts.

For each procedure, match each instruction, form field, and timing claim to an explicit fact about
that same service. Keep separate services separate. For advising, the reference supplies an email
channel and two preferred time slots. Student ID and programme name belong to enrolment confirmation
letters. A way to submit a request establishes only how to submit it. The reference gives no advising
review, reply, or confirmation policy. Leave out any unstated step or requirement.

If the user asks you to perform an action, give one sentence saying you cannot perform it.
If the message also asks a distinct informational question, answer that part from the reference.
Example action request: "Call the office and tell me you called."
Example full reply: "I can’t call the office."
A request to confirm you did something is still an action request.

If the user asks about an unknown detail, say you do not have that information. For a mixed question,
give the supported information and identify the specific gap. Use the third person for the office.
Identify the facts as fictional if asked about real-world applicability.

Department reference:
"""
NO_REPLY = "The model returned no text. Please try again."


class CampusBot:
    def __init__(self, model):
        self.model = model
        facts = (LAB / "facts.md").read_text(encoding="utf-8")
        self.history = [{"role": "system", "content": INSTRUCTIONS + facts}]

    def ask(self, question):
        user = {"role": "user", "content": question}
        result = call_model(self.model, [*self.history, user], TEMPERATURE)
        reply = result["reply"]
        if reply and reply.strip():
            self.history.extend([user, {"role": "assistant", "content": reply}])
        return result


def main():
    bot = CampusBot(configured_model())
    print("Campus Info Bot | Fictional department | Type quit to exit.")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.casefold() == "quit":
            break
        if not question:
            continue
        try:
            reply = bot.ask(question)["reply"]
            print(f"Bot: {reply if reply and reply.strip() else NO_REPLY}")
        except Exception as error:
            print(f"Bot: Model call failed ({type(error).__name__}). Please try again.")
    print("Goodbye.")


if __name__ == "__main__":
    main()
