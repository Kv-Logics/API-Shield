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

## Tech Stack
Frontend: React + Vite + Tailwind
Backend: FastAPI
Database: SQLite / PostgreSQL

## Setup Instructions
(Setup instructions coming soon...)

Status: In development
