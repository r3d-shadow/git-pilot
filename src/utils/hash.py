import hashlib

def compute_sha(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
