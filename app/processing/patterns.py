from collections import Counter
from typing import List, Tuple


def frequent_ngrams(event_types: List[str], n: int = 5, min_count: int = 3) -> List[Tuple[List[str], int]]:
    grams = Counter(tuple(event_types[i : i + n]) for i in range(len(event_types) - n + 1))
    return [(list(g), c) for g, c in grams.items() if c >= min_count]
