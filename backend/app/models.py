from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Finding(BaseModel):
    endpoint: str
    method: str
    test_name: str
    severity: str
    evidence_request: str
    evidence_response: str
    remediation: str

class ScanReport(BaseModel):
    scan_id: str
    target_url: str
    status: str
    progress: int
    findings: List[Finding] = []

class Endpoint(BaseModel):
    method: str
    url: str
    path_params: List[str] = []
    query_params: List[str] = []
    headers: Dict[str, str] = {}
    body: Optional[Any] = None
    auth_required: bool = False
