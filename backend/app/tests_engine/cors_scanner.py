import httpx
from typing import Optional
from ..models import Endpoint, Finding

async def run_cors_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Optional[Finding]:
    """
    Tests for permissive CORS headers (e.g. Access-Control-Allow-Origin: * with credentials).
    """
    headers = dict(endpoint.headers or {})
    headers["Origin"] = "https://evil-attacker-site.com"
    
    try:
        response = await client.request(
            method=endpoint.method,
            url=endpoint.url,
            headers=headers,
            timeout=5.0
        )
        
        allow_origin = response.headers.get("Access-Control-Allow-Origin", "")
        allow_credentials = response.headers.get("Access-Control-Allow-Credentials", "")
        
        if allow_origin == "*" or (allow_origin == "https://evil-attacker-site.com" and allow_credentials.lower() == "true"):
            return Finding(
                endpoint=endpoint.url,
                method=endpoint.method,
                test_name="Permissive CORS Misconfiguration",
                severity="HIGH" if allow_credentials.lower() == "true" else "MEDIUM",
                evidence_request=f"Origin: https://evil-attacker-site.com",
                evidence_response=f"Access-Control-Allow-Origin: {allow_origin}\nAccess-Control-Allow-Credentials: {allow_credentials}",
                remediation="Configure specific, trusted origins in Access-Control-Allow-Origin header instead of wildcard '*' or reflecting arbitrary origins."
            )
    except Exception:
        pass
        
    return None
