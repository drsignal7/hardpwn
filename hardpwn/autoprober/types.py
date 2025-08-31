from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class Finding:
    kind: str
    pins: Dict[str, Any]
    confidence: float
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProbeReport:
    target_id: str
    findings: List[Finding] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def add_finding(self, f: Finding):
        self.findings.append(f)

    def log(self, msg: str):
        self.logs.append(msg)
