from fastapi import FastAPI, Header, HTTPException

from digital_farming_mvp import generate_backend_mvp_plan
from diagnostics import diagnose_crop_issue, list_diagnosis_history
from routes import router
from schemas_auth import DiagnoseRequest, LoginRequest
from security import authenticate, verify_token

app = FastAPI(title="Digital Farming Support Center")
app.include_router(router)


@app.post("/auth/login")
def login(payload: LoginRequest):
    try:
        result = authenticate(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {"success": True, "token": result["token"], "role": result["role"]}


@app.post("/api/diagnose")
def diagnose(request: DiagnoseRequest, authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    result = diagnose_crop_issue(request.crop_type, request.image_url, request.notes)
    return {"success": True, "data": result, "error": None}


@app.get("/api/diagnose/history")
def diagnose_history(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    return {"success": True, "data": list_diagnosis_history(), "error": None}


@app.get("/")
def read_root():
    return {"message": "Digital Farming Support Center API", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/mvp-plan")
def get_mvp_plan():
    return {"plan": generate_backend_mvp_plan("Digital Farming Support Center")}
