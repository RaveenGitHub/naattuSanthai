from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from digital_farming_mvp import generate_backend_mvp_plan
from diagnostics import diagnose_crop_issue, list_diagnosis_history
from routes import router
from schemas_auth import DiagnoseRequest, LoginRequest, PasswordResetRequest, UserCreateRequest
from security import authenticate, create_user, get_profile, list_users, reset_password, verify_token

ROOT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Digital Farming Support Center</title>
  <style>
    :root {
      --soil: #8f5e3c;
      --field: #2d7d46;
      --leaf: #9acb7b;
      --water: #4aa6d6;
      --sky: #edf8ff;
      --earth: #f6f1e8;
      --text: #17301d;
      --muted: #567163;
      --card: #ffffff;
      --line: #dfe9df;
      --warning: #d97706;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, var(--sky) 0%, var(--earth) 100%);
      color: var(--text);
    }
    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px 18px 48px;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 0 22px;
      border-bottom: 1px solid var(--line);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .logo {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--field), var(--water));
      color: white;
      font-size: 20px;
    }
    .nav {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .pill {
      background: #eef8f0;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 14px;
      color: var(--text);
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.3fr 0.7fr;
      gap: 24px;
      padding: 28px 0 18px;
    }
    .panel {
      background: rgba(255,255,255,0.7);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 24px;
      box-shadow: 0 10px 24px rgba(23, 48, 29, 0.05);
    }
    h1, h2, h3 { margin-top: 0; }
    .eyebrow {
      display: inline-block;
      background: #eaf7ea;
      color: var(--field);
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .hero h1 {
      font-size: clamp(2rem, 4vw, 3.5rem);
      line-height: 1.08;
      margin: 18px 0 12px;
    }
    .hero p {
      color: var(--muted);
      font-size: 1.04rem;
      max-width: 52ch;
      line-height: 1.6;
    }
    .cta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 24px;
    }
    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 18px;
      border-radius: 12px;
      font-weight: 700;
      text-decoration: none;
      border: 1px solid transparent;
    }
    .button.primary {
      background: var(--field);
      color: #fff;
    }
    .button.secondary {
      background: #fff;
      border-color: var(--line);
      color: var(--text);
    }
    .status-card {
      display: grid;
      gap: 18px;
    }
    .metric {
      background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
    }
    .metric strong {
      display: block;
      font-size: 2rem;
      margin-top: 8px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      margin-top: 18px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }
    .card h3 { margin-bottom: 10px; }
    .card p { margin: 0; color: var(--muted); line-height: 1.6; }
    .tag {
      display: inline-block;
      margin-top: 12px;
      background: #eafaf1;
      color: var(--field);
      padding: 7px 10px;
      border-radius: 10px;
      font-size: 12px;
      font-weight: 700;
    }
    @media (max-width: 760px) {
      .hero, .grid {
        grid-template-columns: 1fr;
      }
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>Digital Farming Support Center</span>
      </div>
      <nav class="nav" aria-label="Main navigation">
        <a class="pill" href="/">Home</a>
        <a class="pill" href="/dashboard">Dashboard</a>
        <a class="pill" href="/health">Status</a>
      </nav>
    </header>

    <main class="hero">
      <section class="panel">
        <span class="eyebrow">Smart farm operations</span>
        <h1>Grow healthy crops with timely, trusted guidance.</h1>
        <p>
          Help farmers, field officers, and agronomists make faster decisions with weather alerts,
          soil insights, crop recommendations, and market visibility in one simple experience.
        </p>
        <div class="cta-row">
          <a class="button primary" href="/dashboard">Open dashboard</a>
          <a class="button secondary" href="/mvp-plan">View product plan</a>
        </div>
      </section>

      <aside class="panel status-card" aria-label="Summary stats">
        <div class="metric">
          <span>Active fields</span>
          <strong>1,284</strong>
        </div>
        <div class="metric">
          <span>Crop health</span>
          <strong>92%</strong>
        </div>
        <div class="metric">
          <span>Alerts today</span>
          <strong>06</strong>
        </div>
      </aside>
    </main>

    <section class="grid" aria-label="Key services">
      <article class="card">
        <h3>Soil &amp; Irrigation</h3>
        <p>Track fertility, moisture, and irrigation timing so crops stay resilient across changing conditions.</p>
        <span class="tag">Field ready</span>
      </article>
      <article class="card">
        <h3>Weather &amp; Risk</h3>
        <p>Receive local alerts for rainfall, heat stress, and disease pressure before they affect harvest outcomes.</p>
        <span class="tag">Live updates</span>
      </article>
      <article class="card">
        <h3>Market Access</h3>
        <p>Compare local prices and plan better sale timing to improve farmer earnings and crop decisions.</p>
        <span class="tag">Buyer insights</span>
      </article>
    </section>
  </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Farm Dashboard</title>
  <style>
    :root {
      --bg: #f4f9f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --primary-deep: #1f5a35;
      --accent: #4aa6d6;
      --soil: #8f5e3c;
      --warning: #d97706;
      --text: #172d1d;
      --muted: #566f62;
      --line: #dfece0;
      --shadow: 0 12px 30px rgba(26, 52, 31, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    .wrapper {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px 18px 48px;
    }
    .topbar {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
    }
    .logo {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: #fff;
    }
    .nav {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .nav a {
      text-decoration: none;
      color: var(--text);
      background: #f4f8f4;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 14px;
      font-weight: 600;
    }
    .header-box {
      display: grid;
      grid-template-columns: 1.3fr 0.7fr;
      gap: 18px;
      margin-top: 24px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--shadow);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      margin-top: 20px;
    }
    .metric {
      background: linear-gradient(180deg, #f8fbf7 0%, #eef7f1 100%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }
    .metric .label {
      color: var(--muted);
      font-size: 14px;
    }
    .metric strong {
      display: block;
      margin-top: 8px;
      font-size: 2rem;
    }
    .status {
      display: inline-block;
      background: #ebf9ed;
      color: var(--primary);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 12px;
    }
    .bar {
      height: 12px;
      background: #eaf3ea;
      border-radius: 999px;
      overflow: hidden;
      margin-top: 14px;
    }
    .bar > div {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--primary), var(--accent));
      width: 72%;
    }
    .weather {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
      color: var(--muted);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
    }
    th, td {
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
    }
    th {
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    @media (max-width: 760px) {
      .header-box, .grid {
        grid-template-columns: 1fr;
      }
      .topbar {
        flex-direction: column;
        align-items: flex-start;
      }
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌿</div>
        <span>Farmer Field Dashboard</span>
      </div>
      <nav class="nav" aria-label="Dashboard navigation">
        <a href="/">Home</a>
        <a href="/dashboard">Overview</a>
        <a href="/health">Status</a>
      </nav>
    </header>

    <section class="header-box">
      <div class="panel">
        <div class="status">Field overview</div>
        <h2>Healthy crop performance across active farm zones</h2>
        <p style="color: var(--muted); line-height: 1.6; margin-bottom: 18px;">
          Monitor soil condition, irrigation timing, weather stress, and crop health in a simple, actionable view designed for field teams.
        </p>
        <div class="bar" aria-label="Crop health progress"><div></div></div>
        <div class="weather">
          <span>Weather: Clear, 29°C</span>
          <span>Rain chance: 18%</span>
        </div>
      </div>

      <div class="panel">
        <h3>Priority actions</h3>
        <ul style="line-height: 1.8; color: var(--muted); padding-left: 18px; margin: 0;">
          <li>Review irrigation timing for paddy blocks</li>
          <li>Check maize field disease alert</li>
          <li>Confirm mandi prices before harvest</li>
        </ul>
      </div>
    </section>

    <section class="grid" aria-label="Dashboard metrics">
      <div class="metric">
        <div class="label">Soil moisture</div>
        <strong>68%</strong>
      </div>
      <div class="metric">
        <div class="label">Weather</div>
        <strong>Stable</strong>
      </div>
      <div class="metric">
        <div class="label">Pest alerts</div>
        <strong>02</strong>
      </div>
    </section>

    <div class="panel" style="margin-top: 22px;">
      <h3>Latest field activity</h3>
      <table>
        <thead>
          <tr>
            <th>Crop</th>
            <th>Zone</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Rice</td>
            <td>North block</td>
            <td>Healthy</td>
            <td>Continue irrigation</td>
          </tr>
          <tr>
            <td>Groundnut</td>
            <td>South field</td>
            <td>Watchlist</td>
            <td>Inspect leaf health</td>
          </tr>
          <tr>
            <td>Maize</td>
            <td>East zone</td>
            <td>Alert</td>
            <td>Send agronomist review</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

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
def diagnose(request: DiagnoseRequest, authorization: Optional[str] = Header(default=None)):
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
def diagnose_history(authorization: Optional[str] = Header(default=None)):
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


@app.get("/api/users")
def get_users(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"success": True, "data": list_users(), "error": None}


@app.post("/api/users")
def create_user_endpoint(payload: UserCreateRequest, authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload_token = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload_token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    try:
        result = create_user(payload.username, payload.password, payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"success": True, "data": result, "error": None}


@app.get("/api/profile")
def get_user_profile(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    try:
        profile = get_profile(payload["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "data": profile, "error": None}


@app.post("/api/profile/reset-password")
def reset_user_password(payload: PasswordResetRequest, authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload_token = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    try:
        result = reset_password(payload_token["sub"], payload.current_password, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "data": result, "error": None}


@app.get("/")
def read_root(request: Request):
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header.lower():
        return HTMLResponse(content=ROOT_PAGE)
    return JSONResponse({"message": "Digital Farming Support Center API", "status": "ok"})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_PAGE


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/mvp-plan")
def get_mvp_plan():
    return {"plan": generate_backend_mvp_plan("Digital Farming Support Center")}
