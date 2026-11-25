"""Offline checks for provider errors and incomplete evidence."""
import io
import unittest
from unittest.mock import Mock, patch

import httpx
from litellm import RateLimitError

from hello_llm import call_model, main
from run_evaluation import run


def rate_limit(retry_after):
    request = httpx.Request("POST", "https://example.org")
    response = httpx.Response(429, request=request, headers={"Retry-After": retry_after})
    return RateLimitError("Mock rate limit", llm_provider="groq", model="mock-model", response=response)


class LiveRunnerTests(unittest.TestCase):
    @patch("hello_llm.Evidence")
    @patch("hello_llm.configured_model", return_value="mock-model")
    @patch("hello_llm.completion")
    def test_temperature_trials_send_both_manual_roles(self, complete, configured_model, evidence):
        response = Mock(model="mock-model")
        response.choices = [Mock()]
        response.choices[0].message.content = "Mock reply"
        response.usage.model_dump.return_value = {"total_tokens": 10}
        complete.return_value = response

        with patch("sys.stdout", new_callable=io.StringIO):
            main()

        self.assertEqual(
            [call.kwargs["temperature"] for call in complete.call_args_list],
            [0, 0, 0, 1, 1, 1],
        )
        expected = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "In one sentence, what is an intelligent agent?"},
        ]
        for call in complete.call_args_list:
            self.assertEqual(call.kwargs["messages"], expected)

    @patch("hello_llm.sleep")
    @patch("hello_llm.completion")
    def test_rate_limit_can_recover_after_one_wait(self, complete, sleep):
        response = Mock(model="mock-model", usage=None)
        response.choices = [Mock()]
        response.choices[0].message.content = "Recovered"
        complete.side_effect = [rate_limit("2"), response]

        result = call_model("mock-model", [], 0)

        self.assertEqual((result["reply"], result["attempts"]), ("Recovered", 2))
        self.assertEqual(complete.call_count, 2)
        sleep.assert_called_once_with(2)

    @patch("hello_llm.sleep")
    @patch("hello_llm.completion")
    def test_repeated_rate_limit_stops_after_one_retry(self, complete, sleep):
        complete.side_effect = [rate_limit("2"), rate_limit("2")]
        with self.assertRaises(RateLimitError):
            call_model("mock-model", [], 0)

        self.assertEqual(complete.call_count, 2)
        sleep.assert_called_once_with(2)

    @patch("hello_llm.sleep")
    @patch("hello_llm.completion")
    def test_wait_beyond_cap_is_not_retried(self, complete, sleep):
        complete.side_effect = rate_limit("61")
        with self.assertRaises(RateLimitError):
            call_model("mock-model", [], 0)

        complete.assert_called_once()
        sleep.assert_not_called()

    @patch("run_evaluation.CampusBot")
    @patch("run_evaluation.Evidence")
    def test_provider_error_keeps_case_record_and_marks_run_incomplete(self, evidence, bot):
        bot.return_value.ask.side_effect = [rate_limit("61"), {"reply": "A later reply"}]
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            complete = run("mock-model", "tests", (("A1", "First"), ("A2", "Second")), fresh_chat=True)

        self.assertFalse(complete)
        rows = [call.args[0] for call in evidence.return_value.record.call_args_list]
        self.assertEqual(rows[1]["error_type"], "RateLimitError")
        self.assertEqual(rows[2]["reply"], "A later reply")
        self.assertIn("Incomplete tests: no model reply for A1.", output.getvalue())
