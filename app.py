from html import escape
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from database import get_connection
from digital_farming_mvp import generate_backend_mvp_plan
from diagnostics import diagnose_crop_issue, list_diagnosis_history
from routes import router
from schemas_auth import DiagnoseRequest, LoginRequest, PasswordResetRequest, UserCreateRequest
from security import authenticate, create_user, get_profile, list_audit_logs, list_users, reset_password, verify_token
from services import (
    get_scheme_fetch_status,
    get_scheme_update_by_id,
    get_weather_fetch_status,
    list_archived_scheme_updates,
    list_latest_scheme_updates,
    list_market_prices,
    list_weather_forecast,
)

ROOT_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>டிஜிட்டல் விவசாய ஆதரவு மையம்</title>
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
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
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
      font-size: 1.05rem;
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
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.2;
      margin: 18px 0 12px;
    }
    .hero p {
      color: var(--muted);
      font-size: 1.04rem;
      max-width: 52ch;
      line-height: 1.8;
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
    .card p { margin: 0; color: var(--muted); line-height: 1.7; }
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
        <span>டிஜிட்டல் விவசாய ஆதரவு மையம்</span>
      </div>
      <nav class="nav" aria-label="முக்கிய வழிசெலுத்தல்">
        <a class="pill" href="/">முகப்பு</a>
        <a class="pill" href="/dashboard">டாஷ்போர்டு</a>
        <a class="pill" href="/health">நிலை</a>
      </nav>
    </header>

    <main class="hero">
      <section class="panel">
        <span class="eyebrow">செயல்திறன் நிறைந்த விவசாயம்</span>
        <h1>சரியான நேரத்தில், நம்பகமான ஆலோசனையுடன் நல்ல பயிர்களை வளர்க்கலாம்.</h1>
        <p>
          விவசாயிகள், புல அலுவலர்கள், மற்றும் வேளாண்மை நிபுணர்கள் ஒரே இடத்தில் மழை முன்னறிவிப்பு,
          மண் நிலை, பயிர் பரிந்துரை, வானிலை எச்சரிக்கை மற்றும் சந்தை தகவல்களை அணுகி விரைவாக முடிவுகளை எடுக்கலாம்.
        </p>
        <div class="cta-row">
          <a class="button primary" href="/dashboard">டாஷ்போர்டை திற</a>
          <a class="button secondary" href="/mvp-plan">திட்டத்தை பார்க்க</a>
        </div>
      </section>

      <aside class="panel status-card" aria-label="சுருக்க புள்ளிவிவரங்கள்">
        <div class="metric">
          <span>செயலில் உள்ள புலங்கள்</span>
          <strong>1,284</strong>
        </div>
        <div class="metric">
          <span>பயிர் ஆரோக்கியம்</span>
          <strong>92%</strong>
        </div>
        <div class="metric">
          <span>இன்றைய எச்சரிக்கைகள்</span>
          <strong>06</strong>
        </div>
      </aside>
    </main>

    <section class="grid" aria-label="முக்கிய சேவைகள்">
      <article class="card">
        <h3>மண் &amp; நீர்ப்பாசன மேலாண்மை</h3>
        <p>மண் வளம், ஈரப்பதம் மற்றும் பாசன நேரத்தை கண்காணித்து பயிர்கள் உறுதியாக வளர உதவுகிறது.</p>
        <span class="tag">தயார்</span>
      </article>
      <article class="card">
        <h3>வானிலை &amp; ஆபத்து எச்சரிக்கை</h3>
        <p>மழை, வெப்பம், புயல் மற்றும் நோய் அழுத்தம் குறித்து முன்கூட்டியே எச்சரிக்கைகள் வழங்குகிறது.</p>
        <span class="tag">நேரடி புதுப்பிப்புகள்</span>
      </article>
      <article class="card">
        <h3>சந்தை அணுகல்</h3>
        <p>அருகிலுள்ள விலை நிலைகளை ஒப்பிட்டு, விற்பனை நேரத்தை திட்டமிட உதவுகிறது.</p>
        <span class="tag">வாங்குபவர் தகவல்</span>
      </article>
    </section>
  </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>விவசாயிகள் டாஷ்போர்டு</title>
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
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
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
        <span>விவசாயி புல டாஷ்போர்டு / Farmer Field Dashboard</span>
      </div>
      <nav class="nav" aria-label="டாஷ்போர்டு வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">கண்ணோட்டம்</a>
        <a href="/health">நிலை</a>
      </nav>
    </header>

    <section class="header-box">
      <div class="panel">
        <div class="status">புல கண்ணோட்டம் / Field overview</div>
        <h2>பயிர்ப் பராமரிப்பு நல்ல நிலையில் உள்ளது / Healthy crop performance</h2>
        <p style="color: var(--muted); line-height: 1.8; margin-bottom: 18px;">
          மண் நிலை, பாசன நேரம், வானிலை அழுத்தம், மற்றும் பயிர் ஆரோக்கியத்தை ஒரே பார்வையில் காண்பித்து, புலக்குழு முடிவுகளை எளிதாக்குகிறது.
        </p>
        <div class="bar" aria-label="பயிர் ஆரோக்கிய முன்னேற்றம் / Crop health progress"><div></div></div>
        <div class="weather">
          <span>வானிலை / Weather: தெளிவானது, 29°C</span>
          <span>மழை சாத்தியம் / Rain chance: 18%</span>
        </div>
      </div>

      <div class="panel">
        <h3>முன்னுரிமை நடவடிக்கைகள்</h3>
        <ul style="line-height: 1.8; color: var(--muted); padding-left: 18px; margin: 0;">
          <li>நெல் விளைநிலங்களின் பாசன நேரத்தை சரிபார்க்கவும்</li>
          <li>சோளம் புலத்தில் நோய் எச்சரிக்கையை பார்க்கவும்</li>
          <li>அறுவடைக்கு முன் மண்டி விலைகளை உறுதிப்படுத்தவும்</li>
        </ul>
      </div>
    </section>

    <section class="grid" aria-label="டாஷ்போர்டு அளவீடுகள்">
      <div class="metric">
        <div class="label">மண் ஈரப்பதம்</div>
        <strong>68%</strong>
      </div>
      <div class="metric">
        <div class="label">வானிலை</div>
        <strong>நிலையானது</strong>
      </div>
      <div class="metric">
        <div class="label">பூச்சி எச்சரிக்கைகள்</div>
        <strong>02</strong>
      </div>
    </section>

    <div class="panel" style="margin-top: 22px;">
      <h3>சமீபத்திய புல நடவடிக்கைகள்</h3>
      <table>
        <thead>
          <tr>
            <th>பயிர்</th>
            <th>மண்டலம்</th>
            <th>நிலை</th>
            <th>நடவடிக்கை</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>நெல்</td>
            <td>வடக்கு பகுதி</td>
            <td>சரியானது</td>
            <td>பாசனத்தை தொடரவும்</td>
          </tr>
          <tr>
            <td>நிலக்கடலை</td>
            <td>தெற்கு புலம்</td>
            <td>கவனத்தில்</td>
            <td>இலை ஆரோக்கியத்தை ஆய்வு செய்யவும்</td>
          </tr>
          <tr>
            <td>சோளம்</td>
            <td>கிழக்கு மண்டலம்</td>
            <td>எச்சரிக்கை</td>
            <td>வேளாண்மை நிபுணரை அனுப்பவும்</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

SERVICES_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>விவசாய சேவைகள்</title>
  <style>
    :root {
      --bg: #f4f9f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #172d1d;
      --muted: #566f62;
      --line: #dfece0;
      --shadow: 0 12px 30px rgba(26, 52, 31, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #edf8ef 0%, #f7f7ef 100%);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 40px; height: 40px; border-radius: 12px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .nav a {
      text-decoration: none; color: var(--text); background: #f3f8f3; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600;
    }
    h1 { margin: 26px 0 12px; font-size: clamp(2rem, 4vw, 3rem); }
    .intro { color: var(--muted); line-height: 1.8; max-width: 75ch; }
    .grid {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 24px;
    }
    .card {
      background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 20px; box-shadow: var(--shadow);
    }
    .card h3 { margin-top: 0; margin-bottom: 10px; }
    .card p { margin: 0; color: var(--muted); line-height: 1.7; }
    .tag { display: inline-block; margin-top: 12px; background: #eafaf1; color: var(--primary); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; }
    @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>விவசாய சேவைகள்</span>
      </div>
      <nav class="nav" aria-label="சேவைகள் வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/health">நிலை</a>
      </nav>
    </header>

    <h1>விவசாயிகளுக்கு தேவையான முக்கிய சேவைகள்</h1>
    <p class="intro">
      மண் பரிசோதனை, வானிலை முன்னறிவிப்பு, பயிர் ஆலோசனை, பூச்சி கண்டறிதல் மற்றும் அரசு திட்டங்கள் உள்ளிட்ட சேவைகள் ஒரே இடத்தில் வழங்கப்படுகின்றன.
    </p>

    <section class="grid">
      <article class="card">
        <h3>மண் பரிசோதனை</h3>
        <p>மண் pH, ஊட்டச்சத்து, ஈரப்பதம் மற்றும் உர பரிந்துரைகளை அறிந்து, பயிர் வளர்ச்சியை மேம்படுத்த உதவுகிறது.</p>
        <span class="tag">மண் நிலை</span>
      </article>
      <article class="card">
        <h3>வானிலை</h3>
        <p>மழை, வெப்பம், காற்று வேகம் மற்றும் பாசன நேரத்தை முன்னறிந்து விவசாய நடவடிக்கைகளை திட்டமிட உதவுகிறது.</p>
        <span class="tag">எச்சரிக்கை</span>
      </article>
      <article class="card">
        <h3>பயிர் ஆலோசனை</h3>
        <p>பருவம், பயிர் தேர்வு, விதை, உர மேலாண்மை மற்றும் அறுவடை நேரம் குறித்து சிறந்த ஆலோசனைகளை வழங்குகிறது.</p>
        <span class="tag">திட்டமிடல்</span>
      </article>
      <article class="card">
        <h3>நோய் கண்டறிதல்</h3>
        <p>இலை புகைப்படங்கள் மற்றும் விவரங்களை பகுப்பாய்வு செய்து, பூச்சி மற்றும் நோய் தாக்குதலை முன்கூட்டி கண்டறிகிறது.</p>
        <span class="tag">AI</span>
      </article>
      <article class="card">
        <h3>சந்தை விலை</h3>
        <p>அருகிலுள்ள மண்டி விலைகளை ஒப்பிட்டு, சிறந்த விற்பனை நேரத்தை அறிவிக்கிறது.</p>
        <span class="tag">மண்டி தகவல்</span>
      </article>
      <article class="card">
        <h3>அரசு திட்டங்கள்</h3>
        <p>மானியம், காப்பீடு, கடன் மற்றும் பயிர் சார்ந்த உதவித் திட்டங்களை எளிதாகப் புரிந்து பயன்படுத்த உதவுகிறது.</p>
        <span class="tag">உதவி</span>
      </article>
    </section>
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


@app.get("/api/audit/logs")
def get_audit_logs_endpoint(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"success": True, "data": list_audit_logs(), "error": None}


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


@app.get("/services", response_class=HTMLResponse)
def services_page():
    return SERVICES_PAGE


@app.get("/admin/overview", response_class=HTMLResponse)
def admin_overview_page():
    weather_status = get_weather_fetch_status()
    scheme_status = get_scheme_fetch_status()
    weather_total = weather_status.get("total_records", 0)
    scheme_total = scheme_status.get("total_schemes", 0)
    expected_quality = min(
        100,
        max(
            70,
            int(round(((weather_status.get("daily_records", 0) + scheme_status.get("latest_count", 0)) / max(1, weather_total + scheme_total)) * 100)),
        ),
    )

    weather_last = weather_status.get("last_updated_at") or "பதிவு இல்லை"
    scheme_last = scheme_status.get("last_updated_at") or "பதிவு இல்லை"
    weather_regions = " | ".join(f"{k}:{v}" for k, v in (weather_status.get("regions") or {}).items()) or "இல்லை"
    scheme_categories = " | ".join(f"{k}:{v}" for k, v in (scheme_status.get("categories") or {}).items()) or "இல்லை"

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin Overview</title>
  <style>
    :root {{
      --bg: #f4f8f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --warning: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #deebdf;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f4ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 12px; font-size: clamp(2rem, 4vw, 3rem); }}
    .intro {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat strong {{ display: block; font-size: 1.8rem; margin-top: 8px; }}
    .metric-line {{ height: 12px; background: #edf3ee; border-radius: 999px; overflow: hidden; margin-top: 14px; }}
    .metric-line > div {{ height: 100%; width: {expected_quality}%; background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: inherit; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }}
    .card h3 {{ margin-top: 0; margin-bottom: 12px; }}
    .card ul {{ color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }}
    @media (max-width: 760px) {{ .hero, .grid, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🛡️</div>
        <span>Admin Overview / அட்மின் கண்ணோட்டம்</span>
      </div>
      <nav class="nav" aria-label="Admin navigation">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>அட்மின் செயல்பாடு மற்றும் தர மேலாண்மை</h1>
    <p class="intro">
      வானிலை தரவு, அரசு திட்ட புதுப்பிப்புகள், மற்றும் AI/செயல்பாட்டு தரவு ஆகியவற்றின் நிலையை ஒரே பார்வையில் கண்காணித்து, தரக் கட்டுப்பாட்டை உறுதிப்படுத்துகிறது.
    </p>

    <section class="hero">
      <div class="panel">
        <h2>தரம் / Quality</h2>
        <div class="stats">
          <div class="stat"><span>Quality Score</span><strong>{expected_quality}%</strong></div>
          <div class="stat"><span>Weather Records</span><strong>{weather_total}</strong></div>
          <div class="stat"><span>Scheme Records</span><strong>{scheme_total}</strong></div>
        </div>
        <div class="metric-line" aria-label="Quality score"><div></div></div>
      </div>

      <div class="panel">
        <h2>செயல்பாடு / Activity</h2>
        <ul>
          <li>வானிலை புதுப்பிப்பு: {weather_last}</li>
          <li>அரசு திட்ட புதுப்பிப்பு: {scheme_last}</li>
          <li>புல கண்காணிப்பு: 14 farms active</li>
        </ul>
      </div>
    </section>

    <section class="grid">
      <article class="card">
        <h3>வானிலை / Weather</h3>
        <ul>
          <li>Daily records: {weather_status.get('daily_records', 0)}</li>
          <li>Weekly records: {weather_status.get('weekly_records', 0)}</li>
          <li>Monthly records: {weather_status.get('monthly_records', 0)}</li>
          <li>Regions: {weather_regions}</li>
        </ul>
      </article>

      <article class="card">
        <h3>அரசு திட்டங்கள் / Government schemes</h3>
        <ul>
          <li>Latest entries: {scheme_status.get('latest_count', 0)}</li>
          <li>Archived entries: {scheme_status.get('archived_count', 0)}</li>
          <li>Categories: {scheme_categories}</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


ADVISORY_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>பயிர் ஆலோசனை</title>
  <style>
    :root {
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eef8ec 0%, #f7f5ee 100%);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .nav a {
      text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600;
    }
    h1 { margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }
    .intro { color: var(--muted); font-size: 1.05rem; line-height: 1.8; max-width: 75ch; }
    .hero {
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px;
    }
    .panel {
      background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow);
    }
    .stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
    .stat { background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }
    .stat strong { display: block; font-size: 1.8rem; margin-top: 8px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }
    .card h3 { margin-top: 0; margin-bottom: 12px; }
    .card ul { color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }
    @media (max-width: 760px) { .hero, .grid, .stats { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌿</div>
        <span>பயிர் ஆலோசனை</span>
      </div>
      <nav class="nav" aria-label="பயிர் ஆலோசனை வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>மிகச் சிறந்த பருவ பயிர் முடிவுகளுக்கு ஆலோசனை</h1>
    <p class="intro">
      பருவம், மண் நிலை, நீர் மேலாண்மை, மற்றும் தாவர ஆரோக்கியம் ஆகியவற்றின் அடிப்படையில் விவசாயிகளுக்கு தனிப்பயன் பரிந்துரைகளை வழங்குகிறது.
    </p>

    <section class="hero">
      <div class="panel">
        <h2>தற்போதைய பரிந்துரை</h2>
        <p style="color: var(--muted); line-height: 1.8; margin: 0;">
          தற்போதைய பருவத்தில் நெல் மற்றும் கரும்புக்கு நீர் மேலாண்மை, உர பயன்பாடு மற்றும் பூச்சி கண்காணிப்பு முக்கியம். மழை முன்னறிவிப்பைக் கொண்டு பாசன அட்டவணையை மாற்றியமைக்கவும்.
        </p>
        <div class="stats">
          <div class="stat"><span>மண் ஈரப்பதம்</span><strong>68%</strong></div>
          <div class="stat"><span>வானிலை</span><strong>சீரானது</strong></div>
          <div class="stat"><span>அறுவடை தேதி</span><strong>18 நாட்கள்</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>முக்கிய பரிந்துரைகள்</h2>
        <ul style="color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0;">
          <li>மழை இல்லாத நாட்களில் பாசன நேரத்தை சரிசெய்யவும்</li>
          <li>மண் சோதனை முடிவுகளின் அடிப்படையில் உரத்தை பயன்படுத்தவும்</li>
          <li>பூச்சி தாக்குதல் இருந்தால் உடனடியாக ஆலோசனை பெறவும்</li>
          <li>பயிர் பாதுகாப்புக்கு இரசாயன மற்றும் இயற்கை முறைகளை இணைக்கவும்</li>
        </ul>
      </div>
    </section>

    <section class="grid">
      <article class="card">
        <h3>பருவம்</h3>
        <ul>
          <li>கோரைவெப்பநிலை மற்றும் மழை அளவின்படி பயிர் தேர்வு செய்யவும்</li>
          <li>விவசாய பருவத்துக்கு பொருந்தும் விதை வகையை தேர்ந்தெடுக்கவும்</li>
          <li>தெளிவான நேரத்தில் விதைப்பு செய்யவும்</li>
        </ul>
      </article>

      <article class="card">
        <h3>நீர் மேலாண்மை</h3>
        <ul>
          <li>பாசனத்தை குறைந்தபட்சம் 2-3 நாட்களுக்கு ஒருமுறை கண்காணிக்கவும்</li>
          <li>சேற்றின் மேல் நீர் தேங்காமல் பார்த்துக் கொள்ளவும்</li>
          <li>நீர்ப்பாசன தேவையின் அடிப்படையில் நேரம் மாற்றவும்</li>
        </ul>
      </article>

      <article class="card">
        <h3>உரம்</h3>
        <ul>
          <li>மண் சோதனை முடிவுக்கு ஏற்ற உர விகிதத்தை பயன்படுத்து</li>
          <li>நைட்ரஜன், பாஸ்பரஸ், பொட்டாசியம் தரவுகளை சரிபார்க்கவும்</li>
          <li>மிகை உற்பத்தியை தவிர்க்கவும்</li>
        </ul>
      </article>

      <article class="card">
        <h3>பூச்சி &amp; நோய்</h3>
        <ul>
          <li>இலைக் காயங்கள் அல்லது பச்சை நிற மாறுபாடு கண்டால் பரிசோதிக்கவும்</li>
          <li>பூச்சி எச்சரிக்கைகள் வந்தால் உடனடியாக சிகிச்சை மேற்கொள்ளவும்</li>
          <li>விதை மற்றும் பயிர் சரிபார்ப்பை தவறாமல் செய்யவும்</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/advisory", response_class=HTMLResponse)
def advisory_page():
    return ADVISORY_PAGE


@app.get("/disease-detection", response_class=HTMLResponse)
def disease_detection_page(
    crop_type: str = "Rice",
    image_url: str = "https://example.com/crop-scan.jpg",
    notes: str = "Yellowing leaves and spots observed",
):
    result = diagnose_crop_issue(crop_type, image_url, notes)
    diagnosis = escape(str(result.get("diagnosis", "General stress pattern detected")))
    recommendation = escape(str(result.get("recommendation", "Inspect the field and review nutrient balance.")))
    confidence = escape(str(result.get("confidence", "High")))
    manual_review = "Manual review required" if str(result.get("confidence", "High")).lower() in {"low", "medium"} else "Assessment ready"
    crop_label = escape(str(crop_type or "Rice"))
    notes_text = escape(str(notes or "No additional notes provided."))
    image_text = escape(str(image_url or "https://example.com/crop-scan.jpg"))
    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>நோய் கண்டறிதல்</title>
  <style>
    :root {{
      --bg: #fffaf3;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #e9dfd0;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #f9f6ef 0%, #f5f7f1 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f5f7f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 12px; font-size: clamp(2rem, 4vw, 3rem); }}
    .intro {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }}
    .stat {{ background: linear-gradient(180deg, #fbfaf7 0%, #f4f8f3 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat strong {{ display: block; font-size: 1.8rem; margin-top: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }}
    .card h3 {{ margin-top: 0; margin-bottom: 12px; }}
    .card ul {{ color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }}
    form {{ display: grid; gap: 12px; }}
    label {{ display: grid; gap: 6px; font-weight: 600; }}
    input, textarea, select {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; font: inherit; color: var(--text); background: #fff; }}
    textarea {{ min-height: 120px; resize: vertical; }}
    button {{
      background: linear-gradient(135deg, var(--primary), var(--secondary));
      color: white; border: none; border-radius: 12px; padding: 12px 18px; font-weight: 700; cursor: pointer;
    }}
    @media (max-width: 760px) {{ .hero, .grid, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🩺</div>
        <span>நோய் கண்டறிதல்</span>
      </div>
      <nav class="nav" aria-label="நோய் கண்டறிதல் வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>பயிரின் நோய் மற்றும் அழுத்த நிலையை விரைவாக கண்டறியுங்கள்</h1>
    <p class="intro">
      இலை, தண்டு அல்லது பழம் படங்களை பதிவேற்றுவதன் மூலம் நிச்சயமற்ற அல்லது சாத்தியமான நோய், பூச்சி தாக்குதல், அல்லது ஊட்டச்சத்து குறைபாட்டை ஆரம்பத்தில் கண்டறிந்து, தமிழில் செயல்படக்கூடிய சிகிச்சை வழிமுறைகளை வழங்குகிறது.
    </p>

    <section class="hero">
      <div class="panel">
        <h2>படத்தை பதிவேற்று</h2>
        <form method="get" action="/disease-detection">
          <label>
            பயிர் வகை
            <select name="crop_type">
              <option value="Rice" {('selected' if crop_label.lower() == 'rice' else '')}>நெல்</option>
              <option value="Groundnut" {('selected' if crop_label.lower() == 'groundnut' else '')}>நிலக்கடலை</option>
              <option value="Cotton" {('selected' if crop_label.lower() == 'cotton' else '')}>பருத்தி</option>
              <option value="Tomato" {('selected' if crop_label.lower() == 'tomato' else '')}>தக்காளி</option>
            </select>
          </label>
          <label>
            பட URL
            <input type="text" name="image_url" value="{image_text}" />
          </label>
          <label>
            அவதானிப்பு குறிப்புகள்
            <textarea name="notes">{notes_text}</textarea>
          </label>
          <button type="submit">கண்டறிதலை ஆரம்பி</button>
        </form>
      </div>

      <div class="panel">
        <h2>தற்போதைய முடிவு</h2>
        <div class="stats">
          <div class="stat"><span>கணிப்பு</span><strong>{diagnosis}</strong></div>
          <div class="stat"><span>நம்பிக்கை</span><strong>{confidence}</strong></div>
          <div class="stat"><span>முன்னெச்சரிக்கை</span><strong>{manual_review}</strong></div>
        </div>
        <p style="color: var(--muted); line-height: 1.8; margin-top: 18px;"><strong>சிகிச்சை:</strong> {recommendation}</p>
      </div>
    </section>

    <section class="grid">
      <article class="card">
        <h3>சிகிச்சை</h3>
        <ul>
          <li>முன்னெச்சரிக்கைக்கு பரிந்துரைக்கப்பட்ட நுண்ணுயிர் தயாரிப்பை பயன்படுத்தவும்.</li>
          <li>தண்ணீர் தேங்குவதைத் தவிர்க்கவும்.</li>
          <li>பரவலுக்கு அருகிலுள்ள இலைகளை அகற்றவும்.</li>
        </ul>
      </article>

      <article class="card">
        <h3>தடுப்பு</h3>
        <ul>
          <li>பயிர் இடைவெளியை சரியாக பராமரிக்கவும்.</li>
          <li>காற்றோட்டத்தை மேம்படுத்தவும்.</li>
          <li>மண் மற்றும் நீர் மேலாண்மையை தொடர்ந்து கண்காணிக்கவும்.</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/disease-history", response_class=HTMLResponse)
def disease_history_page():
    records = list_diagnosis_history(limit=20)
    if not records:
        rows_html = "<tr><td colspan='4'>No diagnosis history available yet.</td></tr>"
    else:
        rows_html = "".join(
            f"<tr><td>{escape(str(item.get('crop_type', '')))}</td><td>{escape(str(item.get('diagnosis', '')))}</td><td>{escape(str(item.get('confidence', '')))}</td><td>{escape(str(item.get('created_at', '')))}</td></tr>"
            for item in records
        )

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>கண்டறிதல் வரலாறு</title>
  <style>
    :root {{
      --bg: #f4f8f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f4ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); margin-top: 24px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 18px; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; }}
    @media (max-width: 760px) {{ .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🩺</div>
        <span>கண்டறிதல் வரலாறு / Diagnosis History</span>
      </div>
      <nav class="nav" aria-label="History navigation">
        <a href="/">முகப்பு</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
      </nav>
    </header>

    <section class="panel">
      <h1>கண்டறிதல் வரலாறு</h1>
      <p style="color: var(--muted); line-height: 1.8;">முன்னர் செய்யப்பட்ட நோய்/அழுத்த கணிப்புகள் இங்கே காண்பிக்கப்படுகின்றன. குறைந்த நம்பிக்கை முடிவுகள் கைமுறை மதிப்பாய்வு பரிந்துரைக்கப்படுகின்றன.</p>
      <table>
        <thead>
          <tr>
            <th>பயிர்</th>
            <th>கணிப்பு</th>
            <th>நம்பிக்கை</th>
            <th>முடிவு நேரம்</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </section>
  </div>
</body>
</html>
"""


@app.get("/soil-health", response_class=HTMLResponse)
def soil_health_page(
    crop: str = "groundnut",
    ph: float = 6.5,
    nitrogen: float = 25,
    phosphorus: float = 20,
    potassium: float = 180,
):
    from digital_farming.services.soil_health import assess_soil_health

    assessment = assess_soil_health(
        crop=crop,
        ph=ph,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
    )

    crop_label = escape(str(crop or "பயிர்").strip() or "பயிர்")
    soil_status = escape(str(assessment.get("soil_status", "")))
    ph_status = escape(str(assessment.get("ph_status", "")))
    nitrogen_status = escape(str(assessment.get("nitrogen_status", "")))
    phosphorus_status = escape(str(assessment.get("phosphorus_status", "")))
    potassium_status = escape(str(assessment.get("potassium_status", "")))
    action_items = "".join(
        f"<li>{escape(str(item))}</li>" for item in assessment.get("nutrient_actions", [])
    )
    recommendation_summary = escape(str(assessment.get("recommendation_summary", "")))
    fertilizer_plan_items = "".join(
        f"<li><strong>{escape(str(item.get('nutrient', 'உரம்')))}:</strong> {escape(str(item.get('dose', '')))} — {escape(str(item.get('reason', '')))}</li>"
        for item in assessment.get("fertilizer_plan", [])
    )

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>மண் சோதனை</title>
  <style>
    :root {{
      --bg: #f8f6f0;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --soil: #8f5e3c;
      --text: #17301d;
      --muted: #567163;
      --line: #deebdf;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f4ec 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--soil)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .pill {{ display: inline-block; background: #ebf9ed; color: var(--primary); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; margin-bottom: 14px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }}
    .metric {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .metric span {{ color: var(--muted); font-size: 14px; }}
    .metric strong {{ display: block; font-size: 1.5rem; margin-top: 8px; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .metrics {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌱</div>
        <span>மண் சோதனை &amp; உர மேலாண்மை</span>
      </div>
      <nav class="nav" aria-label="மண் சோதனை வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>{crop_label} பயிருக்கு மண் நிலை அறிக்கை</h1>
    <p class="lede">
      மண் pH, நைட்ரஜன், பாஸ்பரஸ் மற்றும் பொட்டாசியம் நிலைகள் அடிப்படையில் தற்போதைய நிலை, ஆபத்து அல்லது தேவையான உர நடவடிக்கைகள் திட்டமிடப்பட்டுள்ளன.
    </p>

    <section class="hero">
      <div class="panel">
        <span class="pill">சோதனை முடிவு</span>
        <h2>மண் நிலை: {soil_status}</h2>
        <div class="metrics">
          <div class="metric"><span>pH நிலை</span><strong>{ph_status}</strong></div>
          <div class="metric"><span>நைட்ரஜன்</span><strong>{nitrogen_status}</strong></div>
          <div class="metric"><span>பாஸ்பரஸ்</span><strong>{phosphorus_status}</strong></div>
          <div class="metric"><span>பொட்டாசியம்</span><strong>{potassium_status}</strong></div>
        </div>
      </div>

      <div class="panel">
        <span class="pill">விரைவான பரிந்துரை</span>
        <h2>உரம் &amp; மேலாண்மை</h2>
        <p><strong>பரிந்துரை:</strong> {recommendation_summary}</p>
        <h3>உர திட்டம்</h3>
        <ul>
          {fertilizer_plan_items}
        </ul>
        <h3>நடவடிக்கை பட்டியல்</h3>
        <ul>
          {action_items}
        </ul>
      </div>
    </section>
  </div>
</body>
</html>
"""


GOVERNMENT_SCHEMES_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>அரசு திட்டங்கள்</title>
  <style>
    :root {
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --warning: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .nav a {
      text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600;
    }
    h1 { margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }
    .intro { color: var(--muted); line-height: 1.8; max-width: 75ch; }
    .toolbar {
      display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0 16px; align-items: center;
    }
    .search, .filter {
      flex: 1; min-width: 180px; max-width: 260px;
      border: 1px solid var(--line); background: var(--panel); border-radius: 12px; padding: 12px 14px;
      font-size: 0.95rem; color: var(--text);
    }
    .tabs {
      display: flex; gap: 12px; margin: 12px 0 18px; flex-wrap: wrap;
    }
    .tab {
      border: 1px solid var(--line); background: var(--panel); border-radius: 12px; padding: 10px 16px; font-weight: 700; color: var(--text);
    }
    .tab.active {
      background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff;
      border-color: transparent;
    }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .card {
      background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: var(--shadow);
    }
    .card h3 { margin-top: 0; margin-bottom: 12px; }
    .card p, .card li { color: var(--muted); line-height: 1.8; }
    .pill {
      display: inline-block; background: #ebf9ed; color: var(--primary); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; margin-bottom: 12px;
    }
    .cta {
      display: inline-block; margin-top: 12px; padding: 10px 14px; border-radius: 10px; background: var(--primary); color: #fff; text-decoration: none; font-weight: 700;
    }
    ul { margin: 0; padding-left: 18px; }
    @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } .toolbar { flex-direction: column; align-items: stretch; } .search, .filter { max-width: none; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">💡</div>
        <span>அரசுத் திட்டங்கள்</span>
      </div>
      <nav class="nav" aria-label="அரசு திட்டங்கள் வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>அரசு திட்டங்கள் மற்றும் நிதி உதவிகள்</h1>
    <p class="intro">
      விவசாயிகளுக்கு கிடைக்கும் புதிய மானியங்கள், பயிர் காப்பீடு, நிதி உதவிகள், பயிற்சி திட்டங்கள் மற்றும் அரசு ஒப்புதல்கள் ஆகியவற்றை தமிழில் எளிதாகப் புரியும் வகையில் வழங்கப்படுகிறது.
    </p>

    <div class="toolbar">
      <input class="search" type="text" value="தேடுக" aria-label="தேடுக" />
      <select class="filter" aria-label="வகை">
        <option>வகை: அனைத்தும்</option>
        <option>subsidy</option>
        <option>insurance</option>
      </select>
    </div>

    <div class="tabs" aria-label="அரசு திட்டங்கள் பட்டிகள்">
      <div class="tab active">புதிய அறிவிப்புகள் (Last 7 Days)</div>
      <div class="tab">காப்பக அறிவிப்புகள் (Archive)</div>
    </div>

    <section class="grid">
      <article class="card">
        <span class="pill">சமீபத்தியது</span>
        <h3>PM-Kisan 16வது தவணை</h3>
        <p>சிறு மற்றும் குறைந்த நிலம் கொண்ட விவசாயிகளுக்கு ரூ.2,000 நேரடி நிதி உதவி வழங்கப்படுகிறது.</p>
        <ul>
          <li>தகுதி: 2 ஹெக்டேர் வரை நிலம்</li>
          <li>விண்ணப்பம்: Aadhaar + e-KYC</li>
        </ul>
        <a class="cta" href="/scheme-page/SCHEME-NEW-001">மேலும் படிக்க</a>
      </article>

      <article class="card">
        <span class="pill">காப்பீடு</span>
        <h3>தமிழ்நாடு பயிர் காப்பீடு மேம்பாடு</h3>
        <p>பயிர் இழப்பு ஏற்பட்டால் காப்பீட்டு நிதி மற்றும் நிலையான நிபுணர் ஆலோசனை வழங்கப்படுகிறது.</p>
        <ul>
          <li>தகுதி: பதிவு செய்யப்பட்ட விவசாயிகள்</li>
          <li>விண்ணப்பம்: அறிக்கை மற்றும் ஆவணங்கள்</li>
        </ul>
        <a class="cta" href="/scheme-page/SCHEME-ARCH-001">மேலும் படிக்க</a>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/government-schemes", response_class=HTMLResponse)
def government_schemes_page(category: Optional[str] = None, search: Optional[str] = None):
    latest_entries = list_latest_scheme_updates(category=category, search=search)
    archived_entries = list_archived_scheme_updates(category=category, search=search)
    category_value = escape(category or "")
    search_value = escape(search or "")

    def render_cards(items):
        if not items:
            return "<div class='card'><h3>உள்ளடக்கம் இல்லை</h3><p>தற்போது தேர்ந்தெடுத்த வடிகட்டி அல்லது தேடல் அளவுருக்களுக்கு பொருந்தும் திட்டங்கள் எதுவும் இல்லை.</p></div>"
        cards = []
        for item in items:
            title = escape(str(item.get("title_ta", "")))
            summary = escape(str(item.get("summary_ta", "")))
            scheme_id = escape(str(item.get("id", "")))
            category_name = escape(str(item.get("category", "")))
            eligibility = escape(str(item.get("eligibility_ta", "")))
            steps = escape(str(item.get("apply_steps_ta", "")))
            cards.append(
                """
                <article class='card'>
                  <span class='pill'>{category_name}</span>
                  <h3>{title}</h3>
                  <p>{summary}</p>
                  <ul>
                    <li>தகுதி: {eligibility}</li>
                    <li>விண்ணப்பம்: {steps}</li>
                  </ul>
                  <a class='cta' href='/scheme-page/{scheme_id}'>மேலும் படிக்க</a>
                </article>
                """.format(
                    category_name=category_name,
                    title=title,
                    summary=summary,
                    eligibility=eligibility,
                    steps=steps,
                    scheme_id=scheme_id,
                )
            )
        return "\n".join(cards)

    latest_html = render_cards(latest_entries)
    archive_html = render_cards(archived_entries)
    template = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>அரசு திட்டங்கள்</title>
  <style>
    :root {{
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --warning: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .intro {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0 16px; align-items: center; }}
    .search, .filter {{ flex: 1; min-width: 180px; max-width: 260px; border: 1px solid var(--line); background: var(--panel); border-radius: 12px; padding: 12px 14px; font-size: 0.95rem; color: var(--text); }}
    .tabs {{ display: flex; gap: 12px; margin: 12px 0 18px; flex-wrap: wrap; }}
    .tab {{ border: 1px solid var(--line); background: var(--panel); border-radius: 12px; padding: 10px 16px; font-weight: 700; color: var(--text); }}
    .tab.active {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; border-color: transparent; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: var(--shadow); }}
    .card h3 {{ margin-top: 0; margin-bottom: 12px; }}
    .card p, .card li {{ color: var(--muted); line-height: 1.8; }}
    .pill {{ display: inline-block; background: #ebf9ed; color: var(--primary); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; margin-bottom: 12px; }}
    .cta {{ display: inline-block; margin-top: 12px; padding: 10px 14px; border-radius: 10px; background: var(--primary); color: #fff; text-decoration: none; font-weight: 700; }}
    ul {{ margin: 0; padding-left: 18px; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} .toolbar {{ flex-direction: column; align-items: stretch; }} .search, .filter {{ max-width: none; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">💡</div>
        <span>அரசுத் திட்டங்கள்</span>
      </div>
      <nav class="nav" aria-label="அரசு திட்டங்கள் வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>அரசு திட்டங்கள் மற்றும் நிதி உதவிகள்</h1>
    <p class="intro">
      விவசாயிகளுக்கு கிடைக்கும் புதிய மானியங்கள், பயிர் காப்பீடு, நிதி உதவிகள், பயிற்சி திட்டங்கள் மற்றும் அரசு ஒப்புதல்கள் ஆகியவற்றை தமிழில் எளிதாகப் புரியும் வகையில் வழங்கப்படுகிறது.
    </p>

    <form class="toolbar" method="get" action="/government-schemes">
      <input class="search" type="text" name="search" value="__SEARCH__" aria-label="தேடுக" placeholder="தேடுக" />
      <select class="filter" name="category" aria-label="வகை">
        <option value="">வகை: அனைத்தும்</option>
        <option value="subsidy" __SUBSIDY_SELECTED__>subsidy</option>
        <option value="insurance" __INSURANCE_SELECTED__>insurance</option>
      </select>
      <button type="submit" class="cta" style="border:none;cursor:pointer;">வடிகட்டு</button>
    </form>

    <div class="tabs" aria-label="அரசு திட்டங்கள் பட்டிகள்">
      <div class="tab active">புதிய அறிவிப்புகள் (Last 7 Days)</div>
      <div class="tab">காப்பக அறிவிப்புகள் (Archive)</div>
    </div>

    <section class="grid">
      __LATEST_HTML__
    </section>

    <div class="tabs" aria-label="காப்பக அறிவிப்புகள் பட்டிகள்" style="margin-top: 28px;">
      <div class="tab active">காப்பக அறிவிப்புகள்</div>
    </div>
    <section class="grid">
      __ARCHIVE_HTML__
    </section>
  </div>
</body>
</html>
"""
    return (
        template
        .replace("__SEARCH__", search_value)
        .replace("__SUBSIDY_SELECTED__", "selected" if category_value == "subsidy" else "")
        .replace("__INSURANCE_SELECTED__", "selected" if category_value == "insurance" else "")
        .replace("__LATEST_HTML__", latest_html)
        .replace("__ARCHIVE_HTML__", archive_html)
    )


@app.get("/scheme-page/{scheme_id}", response_class=HTMLResponse)
def scheme_detail_page(scheme_id: str):
    entry = get_scheme_update_by_id(scheme_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{entry['title_ta']}</title>
  <style>
    :root {{
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 950px; margin: 0 auto; padding: 28px 18px 48px; }}
    .panel {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: 24px; box-shadow: var(--shadow);
    }}
    .tag {{
      display: inline-block; background: #ebf9ed; color: var(--primary); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; margin-bottom: 12px;
    }}
    h1 {{ font-size: clamp(1.9rem, 4vw, 2.7rem); margin: 10px 0 18px; }}
    p, li {{ color: var(--muted); line-height: 1.8; }}
    ul {{ padding-left: 20px; }}
    .section {{ margin-top: 20px; }}
    .section h2 {{ margin-bottom: 10px; font-size: 1.2rem; }}
    .nav {{ margin-bottom: 18px; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="nav">
      <a href="/government-schemes">← அரசுத் திட்டங்கள்</a>
    </div>
    <div class="panel">
      <span class="tag">{entry['category']}</span>
      <h1>{entry['title_ta']}</h1>
      <p><strong>சுருக்கம்:</strong> {entry['summary_ta']}</p>

      <div class="section">
        <h2>தகுதி</h2>
        <p>{entry['eligibility_ta']}</p>
      </div>

      <div class="section">
        <h2>நன்மைகள்</h2>
        <p>{entry['benefits_ta']}</p>
      </div>

      <div class="section">
        <h2>விண்ணப்ப படிகள்</h2>
        <p>{entry['apply_steps_ta']}</p>
      </div>

      <div class="section">
        <h2>மூலம்</h2>
        <p>{entry['source_name']}</p>
      </div>
    </div>
  </div>
</body>
</html>
"""


WEATHER_MARKET_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>வானிலை மற்றும் சந்தை</title>
  <style>
    :root {
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .nav a {
      text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600;
    }
    h1 { margin: 28px 0 12px; font-size: clamp(2rem, 4vw, 3rem); }
    .intro { color: var(--muted); line-height: 1.8; max-width: 75ch; }
    .hero {
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px;
    }
    .panel {
      background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow);
    }
    .metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
    .metric { background: linear-gradient(180deg, #f8faf7 0%, #edf8f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }
    .metric strong { display: block; margin-top: 8px; font-size: 1.8rem; }
    .cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }
    .card h3 { margin-top: 0; margin-bottom: 10px; }
    .card ul { color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; }
    @media (max-width: 760px) { .hero, .cards, .metrics { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌤️</div>
        <span>வானிலை மற்றும் சந்தை</span>
      </div>
      <nav class="nav" aria-label="வானிலை மற்றும் சந்தை வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>வானிலை முன்னறிவிப்பு மற்றும் சந்தை விலை மேலாண்மை</h1>
    <p class="intro">
      மழை, வெப்பநிலை, காற்றின் வேகம் மற்றும் அருகிலுள்ள மண்டி விலை ஆகியவற்றை ஒரே இடத்தில் பார்த்து, வர்த்தக மற்றும் சாகுபடி முடிவுகளை எளிதாக்குகிறது.
    </p>

    <section class="hero">
      <div class="panel">
        <h2>இன்றைய வானிலை</h2>
        <div class="metrics">
          <div class="metric"><span>வெப்பநிலை</span><strong>29°C</strong></div>
          <div class="metric"><span>மழை</span><strong>18%</strong></div>
          <div class="metric"><span>காற்று</span><strong>18 km/h</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>எச்சரிக்கை</h2>
        <ul style="color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0;">
          <li>மாலை நேரத்தில் மழை சாத்தியம் அதிகம்</li>
          <li>மண்ணின் ஈரப்பதம் சற்று குறைந்துள்ளது</li>
          <li>காற்று வேகம் வரம்பை மீறவில்லை</li>
        </ul>
      </div>
    </section>

    <section class="cards">
      <article class="card">
        <h3>சந்தை விலை</h3>
        <table>
          <thead>
            <tr><th>பயிர்</th><th>விலை</th></tr>
          </thead>
          <tbody>
            <tr><td>நெல்</td><td>₹2,140 / குவிண்டால்</td></tr>
            <tr><td>கரும்பு</td><td>₹3,350 / குவிண்டால்</td></tr>
            <tr><td>மிளகாய்</td><td>₹5,900 / குவிண்டால்</td></tr>
          </tbody>
        </table>
      </article>

      <article class="card">
        <h3>வணிக பரிந்துரை</h3>
        <ul>
          <li>இன்று மிளகாயை விற்பது நல்ல வாய்ப்பு</li>
          <li>நெல் விலை சிறிது நிலையானது</li>
          <li>கரும்பு அறுவடை தேதி நெருங்குகிறது</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/weather-market", response_class=HTMLResponse)
def weather_market_page(region: str = "Kallakurichi"):
    region_name = (region or "Kallakurichi").strip() or "Kallakurichi"
    daily_forecast = list_weather_forecast("daily", region_name)
    if not daily_forecast:
        daily_forecast = list_weather_forecast("daily", "Kallakurichi")

    forecast = daily_forecast[0] if daily_forecast else {
        "region": region_name,
        "summary_ta": "இன்று வானம் மேகமூட்டமாக இருக்கும். மழை சாத்தியம் உள்ளது.",
        "temperature_c": 29.0,
        "rainfall_mm": 18.0,
        "wind_kmh": 18.0,
    }
    market_rows = list_market_prices()
    market_rows_html = "".join(
        f"<tr><td>{escape(str(getattr(item, 'crop_name', 'மாற்று பயிர்')))}<br><small>{escape(str(getattr(item, 'market_name', 'மண்டி')).replace('Mandi', 'மண்டி').replace('Market', 'மார்க்கெட்'))}</small></td><td>₹{float(getattr(item, 'price_per_kg', 0.0)):.2f} / கிலோ</td></tr>"
        for item in market_rows[:4]
    )
    if not market_rows_html:
        market_rows_html = """
        <tr><td>நெல்<br><small>கல்லக்குறிச்சி மண்டி</small></td><td>₹24.50 / கிலோ</td></tr>
        <tr><td>கரும்பு<br><small>மார்க்கெட் மண்டி</small></td><td>₹33.50 / கிலோ</td></tr>
        <tr><td>மிளகாய்<br><small>மண்டி சந்தை</small></td><td>₹59.00 / கிலோ</td></tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>வானிலை மற்றும் சந்தை</title>
  <style>
    :root {{
      --bg: #f5f9f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{
      display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 22px; border-bottom: 1px solid var(--line);
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{
      text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600;
    }}
    h1 {{ margin: 28px 0 12px; font-size: clamp(2rem, 4vw, 3rem); }}
    .intro {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px;
    }}
    .panel {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow);
    }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .metric {{ background: linear-gradient(180deg, #f8faf7 0%, #edf8f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .metric strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }}
    .card h3 {{ margin-top: 0; margin-bottom: 10px; }}
    .card ul {{ color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; }}
    @media (max-width: 760px) {{ .hero, .cards, .metrics {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌤️</div>
        <span>{escape(region_name)} - வானிலை மற்றும் சந்தை</span>
      </div>
      <nav class="nav" aria-label="வானிலை மற்றும் சந்தை வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/services">சேவைகள்</a>
      </nav>
    </header>

    <h1>வானிலை முன்னறிவிப்பு மற்றும் சந்தை விலை மேலாண்மை</h1>
    <p class="intro">
      {escape(str(forecast.get('summary_ta', 'இன்று வானம் மேகமூட்டமாக இருக்கும். மழை சாத்தியம் உள்ளது.')))}
    </p>

    <section class="hero">
      <div class="panel">
        <h2>இன்றைய வானிலை</h2>
        <div class="metrics">
          <div class="metric"><span>வெப்பநிலை</span><strong>{float(forecast.get('temperature_c', 29.0)):.0f}°C</strong></div>
          <div class="metric"><span>மழை</span><strong>{float(forecast.get('rainfall_mm', 18.0)):.0f}%</strong></div>
          <div class="metric"><span>காற்று</span><strong>{float(forecast.get('wind_kmh', 18.0)):.0f} km/h</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>எச்சரிக்கை</h2>
        <ul style="color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0;">
          <li>{escape(str(forecast.get('summary_ta', 'மழை சாத்தியம் உள்ளது')))}</li>
          <li>மண்ணின் ஈரப்பதம் பரிசோதிக்கப்பட வேண்டும்</li>
          <li>பாசன அட்டவணையை வெப்பநிலை மற்றும் மழை முன்னறிவிப்புடன் இணைக்கவும்</li>
        </ul>
      </div>
    </section>

    <section class="cards">
      <article class="card">
        <h3>சந்தை விலை</h3>
        <table>
          <thead>
            <tr><th>பயிர்</th><th>விலை</th></tr>
          </thead>
          <tbody>
            {market_rows_html}
          </tbody>
        </table>
      </article>

      <article class="card">
        <h3>வணிக பரிந்துரை</h3>
        <ul>
          <li>இன்று {escape(region_name)} பகுதியில் வானிலை கண்காணிப்பு முக்கியம்</li>
          <li>சந்தை விலைகள் மற்றும் மழை முன்னறிவிப்பு ஆகியவற்றை ஒரே பார்வையில் பார்க்கவும்</li>
          <li>பயிர் விற்பனை மற்றும் பாசன அட்டவணையை ஒருங்கிணைக்கவும்</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/health")
def health_check():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"

    return {
        "status": "healthy",
        "service": "digital-farming-support-center",
        "database": {"status": database_status},
    }


@app.get("/mvp-plan")
def get_mvp_plan():
    return {"plan": generate_backend_mvp_plan("Digital Farming Support Center")}
