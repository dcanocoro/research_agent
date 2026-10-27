"""Local UTF-8 size budget, independent of provider tokenizer mappings."""
from typing import Any

from .recording import encoded


class ContextConfigurationError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ByteCounter:
    # Heuristic reserve, not a bound on provider output or a bytes/token conversion.
    output_bytes_per_token = 8

    def __init__(self) -> None:
        self.metadata = {"method": "typed-json-utf8-bytes-v1", "unit": "bytes",
                         "safety_margin": 0.10, "output_bytes_per_token": self.output_bytes_per_token,
                         "provider_exact": False}

    def count(self, value: Any) -> int:
        return len(encoded(value))

    def measure(self, system: str, history: list[Any], tools: list[Any], output_tokens: int) -> dict[str, int]:
        if not isinstance(output_tokens, int) or isinstance(output_tokens, bool) or output_tokens <= 0:
            raise ContextConfigurationError("invalid_output_token_reserve")
        size = self.count({"system": system, "input": history, "tools": tools})
        reserve = output_tokens * self.output_bytes_per_token
        return {"input_bytes": size, "reserved_output_bytes": reserve,
                "budgeted_bytes": (size * 11 + 9) // 10 + reserve}
