import httpx
import asyncio
from ..models import Finding, Endpoint

async def run_rate_limit_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Finding | None:
    """
    Test 3: Rate Limiting
    Attempts to flood the login endpoint.
    """
    if "login" not in endpoint.url.lower():
        return None
        
    url = endpoint.url
    method = endpoint.method
    
    # We will send 10 requests concurrently
    async def send_req():
        try:
            return await client.post(url, json={"username": "bob", "password": "wrong"})
        except:
            return None
            
    tasks = [send_req() for _ in range(10)]
    responses = await asyncio.gather(*tasks)
    
    # Check if we got any 429 Too Many Requests
    got_429 = any(r and r.status_code == 429 for r in responses)
    
    # If we didn't get 429, the endpoint is missing rate limiting!
    if not got_429:
        return Finding(
            endpoint=url,
            method=method,
            test_name="Missing Rate Limiting",
            severity="High",
            evidence_request=f"Sent 10 rapid {method} requests to {url}",
            evidence_response="Did not receive a 429 Too Many Requests response.",
            remediation="Implement rate limiting (e.g., Token Bucket or Leaky Bucket algorithm) to prevent brute-force and DoS attacks."
        )
        
    return None
