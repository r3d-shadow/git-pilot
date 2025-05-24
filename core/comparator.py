def is_same(existing, new):
    if existing is None:
        return False
    return existing.strip() == new.strip()
