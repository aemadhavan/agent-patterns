import os
import threading
from anthropic import Anthropic
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import BaseCallbackHandler

load_dotenv(override=True)  # .env wins over stray shell/IDE-injected keys

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
_client: Anthropic | None = None
_call_lock = threading.Lock()
_llm_call_count = 0


def reset_call_count() -> None:
    """Reset the global LLM call counter before benchmarking a pattern."""
    global _llm_call_count
    with _call_lock:
        _llm_call_count = 0


def get_call_count() -> int:
    """Return the number of LLM calls recorded since the last reset."""
    with _call_lock:
        return _llm_call_count


def _increment_call_count() -> None:
    global _llm_call_count
    with _call_lock:
        _llm_call_count += 1


class _CallCountCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs) -> None:
        _increment_call_count()

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        _increment_call_count()


def get_llm(temperature: float = 0.0) -> ChatAnthropic:
    """Return a configured ChatAnthropic instance for LangGraph nodes and agents."""
    return ChatAnthropic(
        model=ANTHROPIC_MODEL,
        api_key=os.environ["ANTHROPIC_API_KEY"],
        temperature=temperature,
        max_tokens=1024,
        callbacks=[_CallCountCallback()],
    )


def generate_text(prompt: str, system: str | None = None, max_tokens: int = 1024, track: bool = True) -> str:
    """Direct Anthropic Messages API helper for lightweight single-step calls."""
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if track:
        _increment_call_count()

    kwargs = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    msg = _client.messages.create(**kwargs)
    return msg.content[0].text
