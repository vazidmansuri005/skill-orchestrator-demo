"""Token counting helpers.

Uses tiktoken's cl100k_base encoding when available (a good public proxy for
how LLMs tokenize). Falls back to a ~4-chars-per-token estimate so the demo
runs with zero dependencies installed.
"""

from functools import lru_cache


@lru_cache(maxsize=1)
def _encoder():
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def tokenizer_name() -> str:
    return "tiktoken/cl100k_base" if _encoder() else "estimate(~4 chars/token)"


def count_tokens(text: str) -> int:
    enc = _encoder()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // 4)
