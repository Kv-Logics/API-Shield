import httpx
import re
from ..models import Finding, Endpoint

async def run_sensitive_data_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Finding | None:
    """
    Test 4: Sensitive Data Exposure
    Scans responses for known secret patterns.
    """
    url = endpoint.url
    method = endpoint.method
    headers = dict(endpoint.headers)
    
    try:
        if method == "GET":
            res = await client.get(url, headers=headers)
        elif method == "POST":
            res = await client.post(url, headers=headers, json=endpoint.body)
        else:
            return None
            
        body_text = res.text
        
        # Regex for AWS keys or words like password/secret
        findings = []
        if re.search(r"AKIA[0-9A-Z]{16}", body_text):
            findings.append("AWS Access Key")
        if "password" in body_text.lower() and re.search(r"\"password\"\s*:\s*\"[^\"]+\"", body_text):
            findings.append("Password field exposed")
            
        if findings:
            return Finding(
                endpoint=url,
                method=method,
                test_name="Sensitive Data Exposure",
                severity="Critical",
                evidence_request=f"{method} {url}",
                evidence_response=f"Status: {res.status_code}\nLeaked Data Detected: {', '.join(findings)}",
                remediation="Sanitize all API responses. Never return passwords, API keys, or internal infrastructure details to the client."
            )
    except Exception:
        pass
        
    return None
