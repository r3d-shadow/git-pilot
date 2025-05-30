def is_same(existing: str, new: str) -> bool:
    """
    Compare two pieces of text, ignoring leading/trailing whitespace.
    Returns True if they are identical (after stripping), False otherwise.
    """
    if existing is None:
        return False
    return existing.strip() == new.strip()
