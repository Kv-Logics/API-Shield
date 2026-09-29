import httpx
from ..models import Finding, Endpoint

async def run_idor_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Finding | None:
    """
    Test 2: IDOR
    Swaps the token and tests if one user can access another user's data by changing the ID.
    (This requires predefined users. For the demo, we use Alice's token and try to access student_id=2)
    """
    if "student_id" not in endpoint.query_params and "user_id" not in endpoint.url:
        return None
        
    url = endpoint.url
    method = endpoint.method
    headers = dict(endpoint.headers)
    
    # Force Alice's token for the test
    headers["Authorization"] = "Bearer token_alice"
    
    # If the URL contains student_id=1, change it to student_id=2
    if "?student_id=1" in url:
        test_url = url.replace("student_id=1", "student_id=2")
    else:
        test_url = url # Simplified for demo scope
        
    if test_url == url:
        return None

    try:
        if method == "GET":
            res = await client.get(test_url, headers=headers)
            
        # Vulnerability detected: Alice can access Bob's data (grade C)
        if res.status_code == 200 and "grades" in res.text:
            return Finding(
                endpoint=url,
                method=method,
                test_name="Insecure Direct Object Reference (IDOR)",
                severity="High",
                evidence_request=f"{method} {test_url}\nHeaders: {headers}",
                evidence_response=f"Status: {res.status_code}\nBody: {res.text[:200]}...",
                remediation="Implement robust authorization checks. Ensure the authenticated user has explicit permission to access the requested resource ID."
            )
    except Exception:
        pass
        
    return None
