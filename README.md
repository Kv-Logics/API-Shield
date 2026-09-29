# APIShield
An automated REST API security testing tool.

## Project Overview
APIShield is a robust security testing tool that helps developers find vulnerabilities in their REST APIs. Simply provide a base URL or upload an OpenAPI specification, and APIShield will run a suite of automated security tests.

## Security Tests
1. **Authentication Bypass**: Checks if endpoints requiring authentication can be accessed without a token or with an invalid token.
2. **IDOR (Insecure Direct Object Reference)**: Tests if a user can access another user's resources by modifying identifiers in the request.
3. **Rate Limiting**: Attempts brute-force attacks to ensure the API correctly throttles excessive requests.
4. **Sensitive Data Exposure**: Scans response bodies and headers for leaked secrets like API keys, passwords, and tokens.
5. **SQL Injection**: Sends malicious SQL payloads in parameters and bodies to detect database vulnerabilities.
6. **CORS Misconfiguration**: Detects overly permissive Cross-Origin Resource Sharing rules allowing unauthorized origins.

## Tech Stack
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python FastAPI + HTTPX + ReportLab (PDF Generator)
- **Demo Target**: Vulnerable FastAPI Demo Service

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Demo Target API Setup
```bash
cd demo_api
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Status
Active Development & Security Enhancements
