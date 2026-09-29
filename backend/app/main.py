from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from typing import Dict

from .models import ScanReport, Endpoint
from .parser import parse_postman_collection
from .orchestrator import run_all_tests

app = FastAPI(title="APIShield Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for demo
scans_db: Dict[str, ScanReport] = {}

async def execute_scan(scan_id: str, file_path: str):
    try:
        endpoints = parse_postman_collection(file_path)
        
        # Enforce ALLOWED_TARGETS
        allowed = os.getenv("ALLOWED_TARGETS")
        if allowed:
            allowed_hosts = [h.strip() for h in allowed.split(",")]
            endpoints = [ep for ep in endpoints if any(h in ep.url for h in allowed_hosts)]
            
        findings = await run_all_tests(endpoints)
        
        scans_db[scan_id].status = "completed"
        scans_db[scan_id].progress = 100
        scans_db[scan_id].findings = findings
        
    except Exception as e:
        scans_db[scan_id].status = f"failed: {str(e)}"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/scans")
async def create_scan(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    scan_id = str(uuid.uuid4())
    scans_db[scan_id] = ScanReport(scan_id=scan_id, target_url="Uploaded Collection", status="running", progress=0)
    
    file_path = f"/tmp/{scan_id}.json"
    if os.name == 'nt':
        file_path = f"{scan_id}.json"
        
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    background_tasks.add_task(execute_scan, scan_id, file_path)
    return {"scan_id": scan_id}

@app.get("/scans/{scan_id}")
def get_scan_status(scan_id: str):
    if scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans_db[scan_id]

@app.get("/scans/{scan_id}/report")
def get_scan_report(scan_id: str):
    if scan_id not in scans_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans_db[scan_id]
