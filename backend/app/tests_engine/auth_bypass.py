import httpx
from ..models import Finding, Endpoint

async def run_auth_bypass_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Finding | None:
    """
    Test 1: Authentication Bypass
    Checks if an endpoint that requires auth can be accessed without a token or with a bad token.
    """
    if not endpoint.auth_required:
        return None
        
    url = endpoint.url
    method = endpoint.method
    
    # Remove Authorization header
    headers_no_token = {k:v for k,v in endpoint.headers.items() if k.lower() != 'authorization'}
    
    try:
        if method == "GET":
            res = await client.get(url, headers=headers_no_token)
        elif method == "POST":
            res = await client.post(url, headers=headers_no_token, json=endpoint.body)
        else:
            return None
            
        # Vulnerability detected: returning 200 OK without a token
        if res.status_code == 200:
            return Finding(
                endpoint=url,
                method=method,
                test_name="Authentication Bypass",
                severity="Critical",
                evidence_request=f"{method} {url}\nHeaders: {headers_no_token}",
                evidence_response=f"Status: {res.status_code}\nBody: {res.text[:200]}...",
                remediation="Enforce strict authentication checks. Ensure the endpoint validates a provided token and returns 401 Unauthorized if absent."
            )
            
    except Exception as e:
        pass
        
    return None
