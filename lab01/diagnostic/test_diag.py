import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import diag


@patch("diag.load_dotenv")
@patch("diag.completion")
class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)

    def test_missing_model_reports_configuration_help(self, complete, load_dotenv):
        with patch.dict(os.environ, {"LLM_MODEL": " "}), patch("sys.stderr", new_callable=io.StringIO) as output:
            self.assertEqual(diag.main(self.folder), 1)
        self.assertIn("Set LLM_MODEL", output.getvalue())
        complete.assert_not_called()

    def test_invalid_questions_stop_before_model_calls(self, complete, load_dotenv):
        with patch.dict(os.environ, {"LLM_MODEL": "mock-model"}), patch("sys.stderr", new_callable=io.StringIO) as output:
            self.assertEqual(diag.main(self.folder), 1)
            self.assertIn("questions.txt", output.getvalue())
            (self.folder / "questions.txt").write_text("# Samples\nOne?\n\nTwo?\n", encoding="utf-8")
            self.assertEqual(diag.main(self.folder), 1)
        self.assertIn("found 2", output.getvalue())
        complete.assert_not_called()

    def test_three_calls_save_replies_and_sum_usage(self, complete, load_dotenv):
        self.write_questions()
        complete.side_effect = [self.response(reply, tokens) for reply, tokens in (
            ("First reply", 10), ("Second reply", 20), ("Third reply", 30),
        )]
        with patch.dict(os.environ, {"LLM_MODEL": "mock-model"}), patch("sys.stdout"):
            self.assertEqual(diag.main(self.folder), 0)
        report = (self.folder / "answers.md").read_text(encoding="utf-8")
        self.assertIn("Combined total tokens: **60**", report)
        for reply in ("First reply", "Second reply", "Third reply"):
            self.assertIn(reply, report)
        self.assertEqual(
            [call.kwargs["messages"] for call in complete.call_args_list],
            [[{"role": "user", "content": question}] for question in ("One?", "Two?", "Three?")],
        )

    def test_incomplete_run_preserves_previous_complete_report(self, complete, load_dotenv):
        self.write_questions()
        report = self.folder / "answers.md"
        report.write_text("Previous report", encoding="utf-8")
        complete.side_effect = [self.response("First reply", 10), RuntimeError(), self.response("Third reply", 30)]
        with patch.dict(os.environ, {"LLM_MODEL": "mock-model"}), patch("sys.stdout"), patch("sys.stderr"):
            self.assertEqual(diag.main(self.folder), 1)
        self.assertEqual(report.read_text(encoding="utf-8"), "Previous report")
        incomplete = (self.folder / "answers-incomplete.md").read_text(encoding="utf-8")
        self.assertIn("Unavailable (RuntimeError)", incomplete)
        self.assertIn("Tokens reported for successful calls: **40**", incomplete)

    def write_questions(self):
        (self.folder / "questions.txt").write_text("# Samples\nOne?\n\nTwo?\nThree?\n", encoding="utf-8")

    @staticmethod
    def response(reply, tokens):
        return Mock(choices=[Mock(message=Mock(content=reply))], usage=Mock(total_tokens=tokens))
