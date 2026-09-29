import httpx
from ..models import Finding, Endpoint

async def run_sqli_test(endpoint: Endpoint, client: httpx.AsyncClient) -> Finding | None:
    """
    Test 5: SQL Injection
    Injects a single quote to detect database errors.
    """
    url = endpoint.url
    method = endpoint.method
    
    if "search" not in url.lower() and not endpoint.query_params:
        return None
        
    # Append a single quote to the URL
    if "?" in url:
        test_url = url + "%27" # url encoded '
    else:
        test_url = url + "?q=test%27"
        
    try:
        if method == "GET":
            res = await client.get(test_url, headers=endpoint.headers)
            
        body = res.text.lower()
        # Look for common SQL error signatures or just a 500 error triggered by the payload
        sql_errors = ["syntax error", "sqlite3", "unclosed quotation mark", "sql syntax", "unrecognized token", "internal server error"]
        
        if res.status_code == 500 or any(err in body for err in sql_errors):
            return Finding(
                endpoint=url,
                method=method,
                test_name="SQL Injection",
                severity="Critical",
                evidence_request=f"{method} {test_url}",
                evidence_response=f"Status: {res.status_code}\nBody snippet: {res.text[:200]}",
                remediation="Use parameterized queries or ORMs (like SQLAlchemy) instead of concatenating strings to build SQL queries."
            )
    except Exception:
        pass
        
    return None
