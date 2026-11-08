"""Provider-specific error classification, kept outside the interaction core."""
from infra.llm_errors import LLMTruncated

TRUNCATED_RESPONSE_ERRORS = (LLMTruncated,)
