import re
from collections import Counter
from typing import Dict, List


class PatternExtractor:
    """Lightweight text analyzer for detecting simple token frequency patterns."""

    def extract_patterns(self, text: str) -> Dict[str, int]:
        """Return a frequency map of normalized tokens found in the provided text."""
        tokens = re.findall(r"\b\w+\b", text.lower())
        return dict(Counter(tokens))

    def top_patterns(self, text: str, *, limit: int = 5) -> List[str]:
        """Return the most frequent tokens up to the provided limit."""
        frequencies = self.extract_patterns(text)
        sorted_tokens = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
        return [token for token, _ in sorted_tokens[:limit]]
