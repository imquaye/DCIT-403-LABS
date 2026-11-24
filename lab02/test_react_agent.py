"""Offline regression checks for the Lab 2 agent and tools."""

import contextlib
import importlib.util
import io
import json
import re
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import tools


AGENT_PATH = Path(__file__).with_name("react_agent.py")
LITELLM = types.ModuleType("litellm")
LITELLM.BadRequestError = type("BadRequestError", (Exception,), {})
LITELLM.RateLimitError = type("RateLimitError", (Exception,), {})
LITELLM.completion = Mock(side_effect=AssertionError("Unexpected model call"))
DOTENV = types.ModuleType("dotenv")
DOTENV.load_dotenv = lambda: None

with patch.dict(sys.modules, litellm=LITELLM, dotenv=DOTENV):
    spec = importlib.util.spec_from_file_location("lab02_agent_for_tests", AGENT_PATH)
    agent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent)


def reply(action, value):
    return f"Thought: Reasoning\nAction: {action}\nAction Input: {value}"


def model_response(content):
    return types.SimpleNamespace(choices=[types.SimpleNamespace(
        message=types.SimpleNamespace(content=content))])


class AgentTests(unittest.TestCase):
    def test_completion_stop_sequence_and_rate_limit_retry(self):
        messages = [{"role": "user", "content": "Question"}]
        result = reply("finish", "Answer")
        with patch.object(agent, "completion", side_effect=[
            LITELLM.RateLimitError("try again in 1.5s"), model_response(result),
        ]) as completion, patch.object(agent.time, "sleep") as sleep:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(agent._ask(messages), result)
        self.assertEqual(completion.call_count, 2)
        for call in completion.call_args_list:
            self.assertEqual(call.kwargs["stop"], ["Observation:"])
            self.assertEqual(call.kwargs["messages"], messages)
        sleep.assert_called_once_with(3.5)

    def test_parser_and_recovery(self):
        action = reply("calculator", "1200-1025")
        self.assertEqual(agent.parse(action.replace("\n", "  \r\n")),
                         ("calculator", "1200-1025"))
        for invalid in ("", "Action: finish\nAction Input: yes",
                        "Preamble\n" + action, action + "\nObservation: 175",
                        action + "\n" + action, reply("finish", "")):
            with self.subTest(invalid=invalid):
                self.assertEqual(agent.parse(invalid), (None, None))
        replies = ["", reply("unknown", "x"), action, action, reply("finish", "GHS 175\nRemaining.")]
        with patch.object(agent, "call_model", side_effect=replies), contextlib.redirect_stdout(io.StringIO()):
            answer, trace = agent.run_agent("Budget?")
        self.assertEqual(answer, "GHS 175\nRemaining.")
        for entry in (agent.FORMAT_HELP, "Unknown action", "Observation: 175", "already ran"):
            self.assertIn(entry, trace)
        self.assertEqual(trace.count("Observation: 175"), 1)

    def test_trace_1_calculator_syntax_error_recovery(self):
        question = (
            "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons "
            "of oil at GHS 95 each. How much will I have left?"
        )
        malformed = "4*185 + 3*95 1200 - (4*185 + 3*95)"
        corrected = "1200 - (4*185 + 3*95)"
        expected_answer = "You will have GHS 175 left."
        replies = [
            reply("calculator", malformed),
            reply("calculator", corrected),
            reply("finish", expected_answer),
        ]

        with patch.object(agent, "call_model", side_effect=replies), contextlib.redirect_stdout(io.StringIO()):
            answer, trace = agent.run_agent(question)

        self.assertEqual(answer, expected_answer)
        self.assertRegex(
            trace,
            rf"Action: calculator\nAction Input: {re.escape(malformed)}\n"
            r"Observation: Error: invalid syntax[^\n]*\n--- Step 2 ---\n",
        )
        self.assertIn(
            f"Action: calculator\nAction Input: {corrected}\n"
            "Observation: 175\n--- Step 3 ---\n",
            trace,
        )
        self.assertTrue(trace.endswith(f"\nFinal answer: {expected_answer}"))

    def test_native_call_recovery(self):
        error = LITELLM.BadRequestError(json.dumps({"error": {
            "code": "tool_use_failed",
            "failed_generation": json.dumps({"name": "assistant", "arguments": {
                "Action": "calculator", "Action Input": "2+2"}}),
        }}))
        with patch.object(agent, "_ask", side_effect=["", error]) as ask:
            self.assertEqual(agent.parse(agent.call_model([])), ("calculator", "2+2"))
        self.assertEqual(ask.call_args.args[0], [agent.NO_FUNCTIONS])

    def test_saved_trace_format(self):
        counts = []
        for path in sorted(agent.EVIDENCE.glob("trace_[1-6].txt")):
            accepted = empty = 0
            steps = re.split(r"^--- Step \d+ ---\n", path.read_text(encoding="utf-8"), flags=re.M)
            for step in steps[1:]:
                content = re.split(r"^Observation:|^Final answer:", step, maxsplit=1, flags=re.M)[0]
                if content.strip() == "(empty reply from the model)":
                    self.assertEqual(agent.parse(""), (None, None))
                    empty += 1
                else:
                    action, value = agent.parse(content)
                    self.assertIn(action, (*agent.TOOLS, "finish"))
                    self.assertTrue(value)
                    accepted += 1
            counts.append((accepted, empty))
        self.assertEqual(counts, [(3, 0), (3, 0), (3, 0), (2, 0), (1, 0), (2, 1)])

    def test_cli_batch_failure_and_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / AGENT_PATH.name
            script.write_bytes(AGENT_PATH.read_bytes())
            evidence = script.parent / "evidence"
            evidence.mkdir()
            baseline = evidence / "baseline.md"
            baseline.write_bytes(b"existing baseline")
            trace = evidence / "trace_1.txt"
            stdout = io.StringIO()
            stdout.reconfigure = Mock()
            with patch.dict(sys.modules, litellm=LITELLM, dotenv=DOTENV), patch.dict(
                "os.environ", {"LLM_MODEL": "mock"},
            ), patch.object(LITELLM, "completion", side_effect=[
                model_response(reply("finish", "Answer")), RuntimeError("mock model failure"),
            ]) as completion, patch.object(agent.time, "sleep"), contextlib.redirect_stdout(stdout), patch.object(
                sys, "argv", [str(script)],
            ):
                with self.assertRaisesRegex(SystemExit, "batch failed on trace 2 .*mock model failure") as failure:
                    runpy.run_path(str(script), run_name="__main__")
                self.assertIsInstance(failure.exception.code, str)  # SystemExit string means status 1.
                self.assertFalse((evidence / "trace_2.txt").exists())
                saved_trace = trace.read_bytes()
                with self.assertRaisesRegex(SystemExit, "refusing to overwrite .*trace_1.txt"):
                    runpy.run_path(str(script), run_name="__main__")
                with patch.object(sys, "argv", [str(script), "--baseline"]):
                    with self.assertRaisesRegex(SystemExit, "refusing to overwrite .*baseline.md"):
                        runpy.run_path(str(script), run_name="__main__")
                self.assertEqual(completion.call_count, 2)
            with self.assertRaises(FileExistsError):
                agent._write_evidence(trace, "replacement")
            self.assertEqual(trace.read_bytes(), saved_trace)
            self.assertEqual(baseline.read_bytes(), b"existing baseline")


class WikipediaTests(unittest.TestCase):
    def test_http_and_json_errors(self):
        for status, payload, expected in [
            (404, None, "No Wikipedia page"),
            (429, None, "rate limited"),
            (503, None, "HTTP 503"),
            (200, ValueError(), "invalid JSON"),
            (200, [], "unexpected response"),
            (200, {"extract": 42}, "unexpected summary"),
        ]:
            response = Mock(status_code=status)
            if isinstance(payload, Exception):
                response.json.side_effect = payload
            else:
                response.json.return_value = payload
            with self.subTest(expected=expected), patch.object(tools.requests, "get", return_value=response):
                self.assertIn(expected, tools.wiki_lookup("Page"))
        with patch.object(tools.requests, "get", side_effect=tools.requests.Timeout):
            self.assertIn("could not reach", tools.wiki_lookup("Page"))

    def test_summary_and_intro_fallback(self):
        summary = Mock(status_code=200, **{"json.return_value": {"extract": "Short"}})
        intro = Mock(status_code=200, **{"json.return_value": {
            "query": {"pages": {"1": {"extract": "Founded   in 1948."}}}}})
        with patch.object(tools.requests, "get", side_effect=[summary, intro]) as get:
            self.assertEqual(tools.wiki_lookup("A/B? C"), "Founded in 1948.")
            self.assertTrue(get.call_args_list[0].args[0].endswith("/A%2FB%3F_C"))
        with patch.object(tools.requests, "get", side_effect=[summary, Mock(status_code=429)]):
            self.assertEqual(tools.wiki_lookup("Page"), "Short")
