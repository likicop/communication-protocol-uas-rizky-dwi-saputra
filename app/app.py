from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from datetime import datetime
from collections import deque
import uuid
import time

app = FastAPI(
    title="SmartTask Incident Monitoring API",
    description="UAS Communication Protocol - Monitoring Mini REST + Logs",
    version="1.0.0"
)

incidents = []
request_logs = []
metrics = {"total_requests": 0, "success_requests": 0, "failed_requests": 0, "rate_limit_errors": 0}
rate_limit_window = deque()
RATE_LIMIT_MAX_REQUEST = 5
RATE_LIMIT_SECONDS = 10

class IncidentCreate(BaseModel):
    title: str
    department: str
    priority: str
    assigned_to: str
    impact: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={
        "success": False,
        "error_code": "INVALID_REQUEST_BODY",
        "message": "Request body is invalid or required fields are missing",
        "required_fields": ["title", "department", "priority", "assigned_to", "impact"],
        "timestamp": datetime.now().isoformat()
    })

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    if request.url.path in ["/openapi.json", "/favicon.ico"]:
        return await call_next(request)
    request_id = f"REQ-{str(uuid.uuid4())[:8].upper()}"
    start_time = time.time()
    metrics["total_requests"] += 1
    response = await call_next(request)
    response_time_ms = round((time.time() - start_time) * 1000, 2)
    request_logs.append({
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "method": request.method,
        "endpoint": request.url.path,
        "status_code": response.status_code,
        "response_time_ms": response_time_ms
    })
    if response.status_code < 400:
        metrics["success_requests"] += 1
    else:
        metrics["failed_requests"] += 1
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/health", tags=["System"])
def health_check():
    return {"service": "SmartTask Incident Monitoring API", "status": "healthy", "environment": "development", "protocol": "HTTP REST", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.post("/incidents", status_code=201, tags=["Incident"])
def create_incident(incident: IncidentCreate):
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{len(incidents)+1:03d}"
    new_incident = {"incident_id": incident_id, "title": incident.title, "department": incident.department, "priority": incident.priority, "assigned_to": incident.assigned_to, "impact": incident.impact, "status": "OPEN", "created_at": datetime.now().isoformat()}
    incidents.append(new_incident)
    return {"success": True, "message": "Incident ticket created successfully", "data": new_incident}

@app.get("/incidents", tags=["Incident"])
def get_incidents():
    return {"total_incidents": len(incidents), "data": incidents}

@app.get("/incidents/{incident_id}", tags=["Incident"])
def get_incident_detail(incident_id: str):
    incident = next((item for item in incidents if item["incident_id"] == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail={"success": False, "error_code": "INCIDENT_NOT_FOUND", "message": f"Incident {incident_id} was not found", "timestamp": datetime.now().isoformat()})
    return {"success": True, "data": incident}

@app.delete("/incidents/{incident_id}", tags=["Incident"])
def delete_incident(incident_id: str):
    incident = next((item for item in incidents if item["incident_id"] == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail={"success": False, "error_code": "INCIDENT_NOT_FOUND", "message": f"Incident {incident_id} was not found", "timestamp": datetime.now().isoformat()})
    incidents.remove(incident)
    return {"success": True, "message": f"Incident {incident_id} deleted successfully"}

@app.get("/metrics", tags=["Monitoring"])
def get_metrics():
    total = metrics["total_requests"]
    failed = metrics["failed_requests"]
    error_rate = round((failed / total) * 100, 2) if total > 0 else 0
    critical_count = len([item for item in incidents if item["priority"].lower() == "critical"])
    open_count = len([item for item in incidents if item["status"] == "OPEN"])
    return {"api_statistics": {"total_requests": metrics["total_requests"], "successful_requests": metrics["success_requests"], "failed_requests": metrics["failed_requests"], "rate_limit_errors": metrics["rate_limit_errors"], "error_rate_percent": error_rate}, "incident_statistics": {"total_incidents": len(incidents), "open_incidents": open_count, "critical_incidents": critical_count}, "last_request": request_logs[-1] if request_logs else None}

@app.get("/logs", tags=["Monitoring"])
def get_logs():
    return {"total_logs": len(request_logs), "logs": request_logs[-20:]}

@app.get("/rate-limit-test", tags=["Reliability"])
def rate_limit_test():
    now = time.time()
    while rate_limit_window and now - rate_limit_window[0] > RATE_LIMIT_SECONDS:
        rate_limit_window.popleft()
    if len(rate_limit_window) >= RATE_LIMIT_MAX_REQUEST:
        metrics["rate_limit_errors"] += 1
        raise HTTPException(status_code=429, detail={"success": False, "error_code": "RATE_LIMIT_EXCEEDED", "message": "Maximum request limit exceeded. Please try again later.", "limit": f"{RATE_LIMIT_MAX_REQUEST} requests per {RATE_LIMIT_SECONDS} seconds", "timestamp": datetime.now().isoformat()})
    rate_limit_window.append(now)
    return {"success": True, "message": "Rate limit test request accepted", "current_request_count_in_window": len(rate_limit_window), "limit": f"{RATE_LIMIT_MAX_REQUEST} requests per {RATE_LIMIT_SECONDS} seconds"}

@app.post("/webhook/incident-created", tags=["Integration"])
def webhook_incident_created(payload: dict):
    return {"success": True, "message": "Webhook payload received by SmartTask Incident Monitoring API", "payload": payload, "received_at": datetime.now().isoformat()}
