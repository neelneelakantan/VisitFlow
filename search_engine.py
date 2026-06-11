# search_engine.py
import re

def tokenize_query(q: str) -> list[str]:
    """
    Split query into tokens.
    Supports:
      - pipeline: |
      - include: token or +token
      - exclude: -token
      - regex: /pattern/
      - tags: #tag
    """
    if not q:
        return []

    # Split on | first
    segments = [seg.strip() for seg in q.split("|") if seg.strip()]

    tokens = []
    for seg in segments:
        for tok in seg.split():
            if tok.strip():
                tokens.append(tok.strip())

    return tokens


def match_token(token: str, text: str, tags: list[str]) -> bool:
    """
    Returns True if the token matches the entry.
    """
    t = token.lower()
    text_lower = text.lower()

    # Exclude: -token
    if t.startswith("-") and len(t) > 1:
        sub = t[1:]
        return sub not in text_lower

    # Regex: /pattern/
    if t.startswith("/") and t.endswith("/") and len(t) > 2:
        pattern = t[1:-1]
        try:
            return re.search(pattern, text, re.IGNORECASE) is not None
        except re.error:
            return t[1:-1] in text_lower

    # Tag: #tag
    if t.startswith("#") and len(t) > 1:
        tag = t[1:]
        return tag in tags

    # Explicit include: +token
    if t.startswith("+") and len(t) > 1:
        sub = t[1:]
        return sub in text_lower

    # Simple include
    return t in text_lower


def refine_search(query: str, entries: list, get_text, get_tags):
    """
    Multi-stage refinement:
      entries: list of objects (Daily3, Visit, Harvester, etc.)
      get_text: function(entry) -> str
      get_tags: function(entry) -> list[str]
    """
    tokens = tokenize_query(query)
    if not tokens:
        return entries

    results = entries

    for token in tokens:
        filtered = []
        for e in results:
            text = get_text(e)
            tags = get_tags(e)
            if match_token(token, text, tags):
                filtered.append(e)
        results = filtered

    return results
