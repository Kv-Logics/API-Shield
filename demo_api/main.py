import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Demo Vulnerable API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY, student_id INTEGER, course TEXT, grade TEXT)")
    
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM grades")
    
    cursor.execute("INSERT INTO users (id, username, password, secret) VALUES (1, 'alice', 'password123', 'AKIAIOSFODNN7EXAMPLE')")
    cursor.execute("INSERT INTO users (id, username, password, secret) VALUES (2, 'bob', 'password456', 'super_secret_token')")
    cursor.execute("INSERT INTO grades (id, student_id, course, grade) VALUES (1, 1, 'Math', 'A')")
    cursor.execute("INSERT INTO grades (id, student_id, course, grade) VALUES (2, 2, 'Math', 'C')")
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

# 1. Auth Bypass
@app.get("/api/protected")
def get_protected(authorization: Optional[str] = Header(None)):
    fix_auth = os.getenv("FIX_AUTH") == "1"
    if fix_auth:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
    return {"data": "This is protected data. You should not see this without a token!"}

# 2. IDOR
@app.get("/api/grades")
def get_grades(student_id: int, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    fix_idor = os.getenv("FIX_IDOR") == "1"
    if fix_idor:
        if authorization == "Bearer token_alice" and student_id != 1:
            raise HTTPException(status_code=403, detail="Forbidden")
        elif authorization == "Bearer token_bob" and student_id != 2:
            raise HTTPException(status_code=403, detail="Forbidden")
            
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
    grades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"grades": grades}

# 3. Rate Limit
class LoginReq(BaseModel):
    username: str
    password: str

login_attempts = {}

@app.post("/login")
def login(req: LoginReq):
    fix_rl = os.getenv("FIX_RATE_LIMIT") == "1"
    
    if fix_rl:
        import time
        now = time.time()
        if req.username not in login_attempts:
            login_attempts[req.username] = []
        login_attempts[req.username] = [t for t in login_attempts[req.username] if now - t < 5]
        if len(login_attempts[req.username]) >= 5:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        login_attempts[req.username].append(now)

    if req.username == "alice" and req.password == "password123":
        return {"token": "Bearer token_alice"}
    elif req.username == "bob" and req.password == "password456":
        return {"token": "Bearer token_bob"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 4. Sensitive Data Exposure
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    fix_sensitive = os.getenv("FIX_SENSITIVE") == "1"
    
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_dict = dict(user)
    if fix_sensitive:
        user_dict.pop("password", None)
        user_dict.pop("secret", None)
        
    return user_dict

# 5. SQL Injection
@app.get("/api/search")
def search_users(q: str):
    fix_sqli = os.getenv("FIX_SQLI") == "1"
    
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if fix_sqli:
            cursor.execute("SELECT id, username FROM users WHERE username LIKE ?", (f"%{q}%",))
        else:
            # Deliberately vulnerable string concatenation
            query = f"SELECT id, username FROM users WHERE username LIKE '%{q}%'"
            cursor.execute(query)
            
        results = [dict(row) for row in cursor.fetchall()]
        return {"results": results}
    except sqlite3.Error as e:
        # Returning DB errors directly is a hallmark of SQLi vulnerability
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
