import hashlib
import json
from pathlib import Path

def require_gate(path, expected_fingerprint):
    evidence = json.loads(Path(path).read_text())
    if evidence.get("passed") is not True or evidence.get("fingerprint") != expected_fingerprint:
        raise RuntimeError("Missing, failed, or stale determinism evidence: collection prohibited")
    return evidence

def fingerprint(config, source_revision):
    value = json.dumps({"config": config, "source_revision": source_revision}, sort_keys=True)
    return hashlib.sha256(value.encode()).hexdigest()
