"""Local, explicitly estimated token accounting; never a provider-exact count."""
from importlib.metadata import version
from math import ceil
from typing import Any

from .recording import encoded


class ContextConfigurationError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class TokenCounter:
    def __init__(self, provider: str, model: str) -> None:
        import tiktoken
        if provider != "openai":
            raise ContextConfigurationError("unsupported_tokenizer_provider")
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError as exc:
            raise ContextConfigurationError("unsupported_tokenizer_model") from exc
        self.metadata = {"method": "typed-json-tiktoken-estimate-v1", "package": "tiktoken",
                         "version": version("tiktoken"), "encoding": self.encoding.name,
                         "provider": provider, "model": model, "safety_margin": 0.10,
                         "provider_exact": False}

    def count(self, value: Any) -> int:
        return len(self.encoding.encode(encoded(value).decode("utf-8"), disallowed_special=()))

    def measure(self, system: str, history: list[Any], tools: list[Any], output_tokens: int) -> dict[str, int]:
        tokens = self.count({"system": system, "input": history, "tools": tools})
        return {"estimated_input_tokens": tokens, "reserved_output_tokens": output_tokens,
                "budgeted_tokens": ceil(tokens * 1.10) + output_tokens}
