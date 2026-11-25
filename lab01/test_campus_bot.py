import io
import unittest
from unittest.mock import patch

from campus_bot import CampusBot, main


class CampusBotTests(unittest.TestCase):
    @patch("campus_bot.call_model")
    def test_facts_and_prior_turn_are_sent(self, complete):
        complete.side_effect = [{"reply": "Please email the office."}, {"reply": "Three days."}]
        bot = CampusBot("mock-model")
        bot.ask("Tell me about the confirmation letter.")
        bot.ask("How long does it take?")
        model, messages, temperature = complete.call_args.args
        self.assertEqual((model, temperature), ("mock-model", 0))
        self.assertIn("Room B204", messages[0]["content"])
        self.assertEqual(messages[1:], [
            {"role": "user", "content": "Tell me about the confirmation letter."},
            {"role": "assistant", "content": "Please email the office."},
            {"role": "user", "content": "How long does it take?"},
        ])

    @patch("campus_bot.call_model")
    def test_failed_or_blank_turn_leaves_history_usable(self, complete):
        complete.side_effect = [RuntimeError("mock error"), {"reply": " "}, {"reply": "OK"}]
        bot = CampusBot("mock-model")
        with self.assertRaises(RuntimeError):
            bot.ask("First")
        bot.ask("Second")
        bot.ask("Third")
        self.assertEqual([message["content"] for message in bot.history[1:]], ["Third", "OK"])

    @patch("campus_bot.configured_model", return_value="mock-model")
    @patch("campus_bot.call_model")
    @patch("builtins.input", side_effect=[" ", " QUIT "])
    def test_quit_and_blank_input_do_not_call_model(self, read_input, complete, model):
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            main()
        complete.assert_not_called()
        self.assertIn("Goodbye.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
