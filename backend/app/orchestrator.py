import httpx
from typing import List
from .models import Endpoint, Finding
from .tests_engine.auth_bypass import run_auth_bypass_test
from .tests_engine.idor import run_idor_test
from .tests_engine.rate_limit import run_rate_limit_test
from .tests_engine.sensitive_data import run_sensitive_data_test
from .tests_engine.sqli import run_sqli_test

async def run_all_tests(endpoints: List[Endpoint]) -> List[Finding]:
    findings = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for ep in endpoints:
            f1 = await run_auth_bypass_test(ep, client)
            if f1: findings.append(f1)
            
            f2 = await run_idor_test(ep, client)
            if f2: findings.append(f2)
            
            f3 = await run_rate_limit_test(ep, client)
            if f3: findings.append(f3)
            
            f4 = await run_sensitive_data_test(ep, client)
            if f4: findings.append(f4)
            
            f5 = await run_sqli_test(ep, client)
            if f5: findings.append(f5)
            
    return findings
