# G.H.O.S.T. - GhostLLM Unit Tests
# Tests ask() and clean_reply() using pytest.
# Gemini is replaced with a fake client so tests run offline and cost nothing.

import pytest
from backend.llm import GhostLLM, FALLBACK_REPLY


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self, reply_text):
        self.reply_text = reply_text
        self.calls = []

    def generate_content(self, model, contents, config):
        self.calls.append(contents)
        return FakeResponse(self.reply_text)


class FakeClient:
    def __init__(self, reply_text="Hello, Guardian."):
        self.models = FakeModels(reply_text)


def make_llm(reply_text="Hello, Guardian."):
    return GhostLLM(client=FakeClient(reply_text), model="test-model")


class TestAsk:

    # TC1: input is not a string
    @pytest.mark.parametrize("bad_input", [None, 123, 4.5, ["hi"], {"msg": "hi"}])
    def test_ask_non_string_raises(self, bad_input):
        llm = make_llm()
        with pytest.raises(TypeError, match="Message must be a string"):
            llm.ask(bad_input)

    # TC2: empty or whitespace-only string
    @pytest.mark.parametrize("bad_input", ["", "   ", "\n\t"])
    def test_ask_empty_raises(self, bad_input):
        llm = make_llm()
        with pytest.raises(ValueError, match="Message cannot be empty"):
            llm.ask(bad_input)

    # TC3: message longer than the limit (input overflow)
    @pytest.mark.parametrize("length", [2001, 10000])
    def test_ask_too_long_raises(self, length):
        llm = make_llm()
        with pytest.raises(ValueError, match=r"Message is too long \(max 2000 characters\)"):
            llm.ask("a" * length)

    # TC4: valid messages, including boundary lengths 1 and 2000
    @pytest.mark.parametrize("message", ["Hi", "What time is it?", "a", "a" * 2000],
                             ids=["short", "question", "1 char", "2000 chars"])
    def test_ask_valid_returns_reply(self, message):
        llm = make_llm("Hello, Guardian.")
        assert llm.ask(message) == "Hello, Guardian."

    # TC5: same message repeated many times
    def test_ask_repeated_input(self):
        llm = make_llm("Hello, Guardian.")
        for _ in range(100):
            assert llm.ask("Hello") == "Hello, Guardian."
        assert len(llm.client.models.calls) == 100

    # TC6: Gemini returns nothing -> fallback reply
    def test_ask_empty_model_reply_uses_fallback(self):
        llm = make_llm(None)
        assert llm.ask("Hello") == FALLBACK_REPLY


class TestCleanReply:

    # TC7: markdown symbols removed
    @pytest.mark.parametrize("raw, expected", [
        ("**Hello** there", "Hello there"),
        ("# Weather", "Weather"),
        ("Run `pip install`", "Run pip install"),
        ("_Sure_ thing", "Sure thing"),
    ])
    def test_clean_removes_markdown(self, raw, expected):
        assert make_llm().clean_reply(raw) == expected

    # TC8: extra spaces and newlines collapsed
    @pytest.mark.parametrize("raw, expected", [
        ("Hello\nworld", "Hello world"),
        ("  lots   of   space  ", "lots of space"),
        ("Line one\n\n\nLine two", "Line one Line two"),
    ])
    def test_clean_collapses_whitespace(self, raw, expected):
        assert make_llm().clean_reply(raw) == expected

    # TC9: None, empty, or only markdown -> fallback
    @pytest.mark.parametrize("raw", [None, "", "   ", "***", "# ##"])
    def test_clean_empty_returns_fallback(self, raw):
        assert make_llm().clean_reply(raw) == FALLBACK_REPLY

    # TC10: non-string reply
    @pytest.mark.parametrize("raw", [123, ["hi"], {"text": "hi"}])
    def test_clean_non_string_raises(self, raw):
        with pytest.raises(TypeError, match="Reply must be a string"):
            make_llm().clean_reply(raw)

    # TC11: already clean text unchanged
    def test_clean_plain_text_unchanged(self):
        assert make_llm().clean_reply("It is 72 degrees today.") == "It is 72 degrees today."
