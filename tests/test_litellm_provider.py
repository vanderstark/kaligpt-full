"""Tests for the LiteLLM provider in KaliGPT."""

from unittest import mock
from types import SimpleNamespace


def _make_response(content="Hello", tool_calls=None):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def _setup_provider():
    """Import provider and set required globals."""
    import agents.litellm_provider as provider
    provider.LITELLM_MODEL = "anthropic/claude-sonnet-4-6"
    provider.TOOLS_INFO = None
    provider.TOOL_FUNCTION_MAP = {}
    return provider


class TestAsk:
    """Verify ask() calls litellm.completion with correct params."""

    def test_basic_completion(self):
        fake_resp = _make_response("test output")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)
            provider = _setup_provider()

            result, history = provider.ask(
                "hello",
                [{"role": "system", "content": "You are helpful."}],
                tools=None,
            )

        assert result == "test output"
        assert history[-1]["content"] == "test output"
        assert history[-1]["role"] == "assistant"
        assert litellm.completion.call_args[1]["drop_params"] is True

    def test_model_forwarded(self):
        fake_resp = _make_response("ok")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)
            provider = _setup_provider()
            provider.LITELLM_MODEL = "bedrock/anthropic.claude-v2"

            provider.ask("test", [{"role": "system", "content": "sys"}], tools=None)

        assert litellm.completion.call_args[1]["model"] == "bedrock/anthropic.claude-v2"

    def test_tools_forwarded(self):
        fake_resp = _make_response("done")
        fake_tools = [{"type": "function", "function": {"name": "test_tool"}}]

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)
            provider = _setup_provider()

            provider.ask("run tool", [{"role": "system", "content": "sys"}], tools=fake_tools)

        call_kwargs = litellm.completion.call_args[1]
        assert call_kwargs["tools"] == fake_tools
        assert call_kwargs["tool_choice"] == "auto"

    def test_no_tools_sends_none(self):
        fake_resp = _make_response("done")

        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(return_value=fake_resp)
            provider = _setup_provider()

            provider.ask("test", [{"role": "system", "content": "sys"}])

        assert litellm.completion.call_args[1]["tool_choice"] == "none"

    def test_error_returns_error_message(self):
        with mock.patch.dict("sys.modules", {"litellm": mock.MagicMock()}):
            import litellm
            litellm.completion = mock.MagicMock(side_effect=Exception("auth failed"))
            provider = _setup_provider()

            result, _ = provider.ask("hello", [{"role": "system", "content": "sys"}], tools=None)

        assert "auth failed" in result


class TestAgentManagement:
    """Verify litellm is registered as a provider."""

    def test_litellm_in_providers_list(self):
        from agents.utils.agent_management import ALL_AI_PROVIDERS
        assert "litellm" in ALL_AI_PROVIDERS
