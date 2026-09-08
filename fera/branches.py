"""Serial counterfactual execution with explicit task hooks and acceptance gate."""
from dataclasses import asdict
from pathlib import Path
import json
import traceback
from .datasets import stable_id, write_once
from .gates import require_gate
from .snapshot import restore

def collect(adapter, snapshot, candidates, suffix, metadata, extractor,
            gate_path, expected_fingerprint, output_dir):
    """Extractor(adapter, step_trace, block_steps) must return a validated Outcome.
    
    Use a successful reference candidate first. Resume only identical protocol IDs.
    Error records are excluded from scientific labels, and repeated errors abort.
    """
    evidence = require_gate(gate_path, expected_fingerprint)
    if evidence.get("collection_approved") is not True:
        raise RuntimeError("Contact-rich expert replay acceptance required before collection")
    results = []
    for candidate in candidates:
        identity = dict(metadata, candidate_id=candidate.candidate_id,
                        seed=candidate.seed, actions=candidate.actions.tolist(),
                        suffix=[list(map(float,a)) for a in suffix],
                        evidence_fingerprint=expected_fingerprint)
        sample_id = stable_id(identity)
        path = Path(output_dir)/f"{sample_id}.json"
        if path.exists():
            old=json.loads(path.read_text())
            if old["identity"] != identity or old["outcome"]["status"] != "ok":
                raise RuntimeError(f"Existing incomplete/error sample needs explicit review: {path}")
            results.append(old)
            continue
        trace = []
        try:
            restore(adapter,snapshot)
            for action in list(candidate.actions)+list(suffix):
                _,reward,done,_=adapter.step(action)
                trace.append(dict(state=adapter.state().tolist(),reward=float(reward),
                                  done=bool(done),success=adapter.success()))
                if done:
                    break
            outcome=extractor(adapter,trace,len(candidate.actions))
            record=dict(sample_id=sample_id,identity=identity,outcome=asdict(outcome),
                        trace=trace)
        except Exception:
            record=dict(sample_id=sample_id,identity=identity,
                        outcome={"status":"environment_error"},trace=trace,error=traceback.format_exc())
            write_once(path,record)
            raise
        write_once(path,record)
        results.append(record)
    return results
