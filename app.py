from datetime import datetime, timezone
from html import escape
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from database import get_connection, get_migration_status
from digital_farming_mvp import generate_backend_mvp_plan
from diagnostics import diagnose_crop_issue, list_diagnosis_history
from routes import router
from schemas_auth import (
    AuthResetPasswordRequest,
    DiagnoseRequest,
    ForgotPasswordRequest,
    LoginRequest,
    PasswordResetRequest,
    RegisterRequest,
    UserCreateRequest,
)
from security import (
    authenticate,
    create_user,
    get_profile,
    hash_password,
    list_audit_logs,
    list_users,
    record_audit_log,
    refresh_access_token,
    reset_password,
    unlock_user,
    verify_otp,
    verify_password,
    verify_token,
)
from services import (
    get_scheme_fetch_status,
    get_scheme_update_by_id,
    get_weather_fetch_status,
    list_archived_scheme_updates,
    list_latest_scheme_updates,
    list_market_prices,
    list_weather_alerts,
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
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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

APP_SHELL_PAGE = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Digital Farming Support Center</title>
  <style>
    :root {
      --bg: #f4f9f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --primary-soft: #ebf9ed;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 14px 32px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      padding: 0;
      min-height: 100%;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    body {
      overflow-x: hidden;
    }
    .shell {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 20px;
      background: rgba(255,255,255,0.96);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--line);
      box-shadow: 0 8px 18px rgba(23, 48, 29, 0.04);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 800;
      letter-spacing: 0.02em;
      white-space: nowrap;
    }
    .logo {
      width: 40px;
      height: 40px;
      display: grid;
      place-items: center;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--primary), var(--secondary));
      color: #fff;
      font-size: 18px;
    }
    .nav {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: flex-end;
    }
    .nav a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 9px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
      transition: all 0.2s ease;
    }
    .nav a:hover, .nav a.active {
      background: var(--primary-soft);
      border-color: rgba(45, 125, 70, 0.2);
      color: var(--primary);
    }
    .frame-wrap {
      flex: 1;
      padding: 18px;
      background: var(--bg);
    }
    iframe {
      width: 100%;
      height: calc(100vh - 110px);
      min-height: 720px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: #fff;
      box-shadow: var(--shadow);
    }
    @media (max-width: 820px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }
      .nav {
        justify-content: flex-start;
      }
      iframe {
        height: 78vh;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>Digital Farming Support Center</span>
      </div>
      <nav class="nav" aria-label="Main navigation">
        <a href="/" class="nav-link active" data-page="/">Home</a>
        <a href="/dashboard" class="nav-link" data-page="/dashboard">Dashboard</a>
        <a href="/services" class="nav-link" data-page="/services">Services</a>
        <a href="/weather-market" class="nav-link" data-page="/weather-market">Weather</a>
        <a href="/government-schemes" class="nav-link" data-page="/government-schemes">Schemes</a>
        <a href="/admin/overview" class="nav-link" data-page="/admin/overview">Admin</a>
      </nav>
    </header>

    <div class="frame-wrap">
      <iframe id="page-frame" title="Farm support content" src="/dashboard"></iframe>
    </div>
  </div>

  <script>
    const frame = document.getElementById('page-frame');
    const links = document.querySelectorAll('.nav-link');
    const setActiveLink = (page) => {
      links.forEach((link) => {
        const active = link.dataset.page === page;
        link.classList.toggle('active', active);
      });
    };
    links.forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const page = link.dataset.page || '/';
        setActiveLink(page);
        frame.src = page;
        if (history.pushState) {
          history.pushState({ page }, '', page === '/' ? '/' : page);
        }
      });
    });
    window.addEventListener('popstate', (event) => {
      const page = event.state && event.state.page ? event.state.page : '/dashboard';
      frame.src = page;
      setActiveLink(page);
    });
    window.addEventListener('load', () => {
      const initialPage = new URL(window.location.href).pathname || '/';
      if (initialPage && initialPage !== '/') {
        frame.src = initialPage;
        setActiveLink(initialPage);
      }
    });
  </script>
</body>
</html>
"""

app = FastAPI(title="Digital Farming Support Center")
app.include_router(router)

PROTECTED_PAGE_PATHS = {"/dashboard"}


@app.middleware("http")
async def require_authenticated_session(request: Request, call_next):
    path = request.url.path
    public_paths = {"/", "/login", "/register", "/forgot-password", "/reset-password", "/shell"}
    if path.startswith("/api/") or path.startswith("/auth/") or path in public_paths:
        return await call_next(request)

    if path in PROTECTED_PAGE_PATHS:
        token = request.cookies.get("digital_farming_session")
        if not token:
            return RedirectResponse(url="/login", status_code=302)
        try:
            verify_token(token)
        except Exception:
            return RedirectResponse(url="/login", status_code=302)
    return await call_next(request)


@app.post("/auth/login")
def login(payload: LoginRequest):
    user_row = None
    with get_connection() as conn:
        user_row = conn.execute(
            "SELECT password, status FROM users WHERE username = ?",
            (payload.username,),
        ).fetchone()

    if user_row and user_row["status"] == "locked":
        if verify_password(payload.password, user_row["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")

    try:
        result = authenticate(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    response = JSONResponse({"success": True, "token": result["token"], "role": result["role"]})
    response.set_cookie(
        key="digital_farming_session",
        value=result["token"],
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return response


@app.post("/api/v1/auth/login")
def api_v1_login(payload: LoginRequest):
    return login(payload)


@app.post("/api/v1/auth/register")
def api_v1_register(payload: RegisterRequest):
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    if not payload.email and not payload.phone:
        raise HTTPException(status_code=400, detail="Email or phone is required")

    if payload.email and "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address")
    if payload.phone and not payload.phone.isdigit():
        raise HTTPException(status_code=400, detail="Phone number must contain digits only")

    try:
        result = create_user(
            payload.username,
            payload.password,
            payload.role,
            email=(payload.email or "").strip() or None,
            phone=(payload.phone or "").strip() or None,
            full_name=(payload.full_name or "").strip(),
            status="pending_verification",
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "success": True,
        "data": {
            "username": result["username"],
            "role": result["role"],
            "status": result["status"],
            "email": payload.email,
            "phone": payload.phone,
            "otp_code": result.get("otp_code"),
        },
        "message": "Registration submitted successfully. Please complete activation.",
    }


@app.post("/api/v1/auth/forgot-password")
def api_v1_forgot_password(payload: ForgotPasswordRequest):
    email = (payload.email or "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid registered email address")
    return {
        "success": True,
        "message": "If the email is registered, a password reset link has been sent.",
    }


@app.post("/api/v1/auth/reset-password")
def api_v1_reset_password(payload: AuthResetPasswordRequest):
    if not payload.username or not payload.new_password:
        raise HTTPException(status_code=400, detail="Username and new password are required")

    with get_connection() as conn:
        row = conn.execute("SELECT username FROM users WHERE username = ?", (payload.username,)).fetchone()
        if row is None:
            raise HTTPException(status_code=400, detail="Invalid or unregistered username")
        conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_password(payload.new_password), payload.username),
        )

    record_audit_log(payload.username, "password_reset", "users", "success", "Password reset via auth reset flow")
    return {
        "success": True,
        "data": {"username": payload.username, "status": "updated"},
        "message": "Password reset completed successfully.",
    }


@app.post("/api/v1/auth/verify-otp")
def api_v1_verify_otp(payload: dict):
    username = str((payload or {}).get("username", "")).strip()
    otp_code = str((payload or {}).get("otp_code", "")).strip()
    try:
        result = verify_otp(username, otp_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "data": result,
        "message": "OTP verification completed successfully.",
    }


@app.post("/api/v1/auth/refresh")
def api_v1_refresh(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        result = refresh_access_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    return {
        "success": True,
        "data": {"token": result["token"], "role": result["role"], "type": result["type"]},
        "message": "Token refreshed successfully.",
    }


@app.post("/auth/refresh")
def auth_refresh(authorization: Optional[str] = Header(default=None)):
    return api_v1_refresh(authorization)


@app.post("/api/v1/auth/logout")
def api_v1_logout():
    response = JSONResponse({"success": True, "message": "Session closed successfully."})
    response.delete_cookie("digital_farming_session", path="/")
    return response


@app.post("/auth/logout")
def auth_logout():
    response = JSONResponse({"success": True, "message": "Session closed successfully."})
    response.delete_cookie("digital_farming_session", path="/")
    return response


def get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.strip():
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    scheme, sep, token = authorization.strip().partition(" ")
    if not sep or scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return token.strip()


@app.post("/api/diagnose")
def diagnose(request: DiagnoseRequest, authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    result = diagnose_crop_issue(request.crop_type, request.image_url, request.notes)
    return {"success": True, "data": result, "error": None}


@app.post("/api/diagnose/upload")
def diagnose_upload(
    crop_type: str = Form(...),
    notes: str = Form(""),
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")

    image_url = file.filename or "uploaded-crop-image"
    if file.content_type:
        image_url = f"{image_url}::{file.content_type}"

    result = diagnose_crop_issue(crop_type, image_url, notes)
    return {"success": True, "data": result, "error": None}


@app.get("/api/diagnose/history")
def diagnose_history(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    return {"success": True, "data": list_diagnosis_history(), "error": None}


@app.get("/api/users")
def get_users(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"success": True, "data": list_users(), "error": None}


@app.get("/api/audit/logs")
def get_audit_logs_endpoint(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"success": True, "data": list_audit_logs(), "error": None}


@app.post("/api/users")
def create_user_endpoint(payload: UserCreateRequest, authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
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


@app.post("/api/users/{username}/unlock")
def unlock_user_endpoint(username: str, authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = unlock_user(username)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "data": result, "error": None}


@app.get("/api/profile")
def get_user_profile(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
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
    token = get_bearer_token(authorization)
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
        return HTMLResponse(content=APP_SHELL_PAGE)
    return JSONResponse({"message": "Digital Farming Support Center API", "status": "ok"})


@app.get("/shell", response_class=HTMLResponse)
def app_shell():
    return APP_SHELL_PAGE


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_PAGE


@app.get("/services", response_class=HTMLResponse)
def services_page():
    return SERVICES_PAGE


@app.get("/api/admin/overview")
def admin_monitoring_overview(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    weather_status = get_weather_fetch_status()
    scheme_status = get_scheme_fetch_status()
    backup_status = get_migration_status()

    service_status = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "app": "digital-farming-support-center",
        "database": db_status,
    }

    alerts = []
    if service_status["status"] != "healthy":
        alerts.append("Database connection check failed.")
    if weather_status.get("quality_gate", {}).get("status") != "pass":
        alerts.append("Weather feed quality gate requires review.")
    if scheme_status.get("quality_gate", {}).get("status") != "pass":
        alerts.append("Scheme feed quality gate requires review.")
    if backup_status.get("backup_policy", {}).get("retention_days", 0) < 7:
        alerts.append("Backup retention policy is below the minimum recommended window.")
    if not alerts:
        alerts.append("All monitored services are operating within the expected health thresholds.")

    return {
        "success": True,
        "data": {
            "service_status": service_status,
            "database_status": db_status,
            "weather_status": weather_status,
            "scheme_status": scheme_status,
            "backup_status": backup_status,
            "alerts": alerts,
        },
        "error": None,
    }


@app.get("/api/admin/content-config")
def admin_content_config_api():
    return {
        "success": True,
        "data": {
            "special_news": [
                {
                    "title": "Kharif advisory window open",
                    "channel": "Operator bulletin",
                    "status": "active",
                    "published_at": "2026-09-10T08:00:00Z",
                },
                {
                    "title": "Rainfall risk alert for Villupuram cluster",
                    "channel": "Village WhatsApp",
                    "status": "scheduled",
                    "published_at": "2026-09-11T06:30:00Z",
                },
            ],
            "advertising": [
                {
                    "title": "Seed supplier campaign",
                    "target_group": "Farmers in Kallakurichi",
                    "status": "active",
                    "placement": "home-banner",
                },
                {
                    "title": "Irrigation subsidy promotion",
                    "target_group": "Pump-set owners",
                    "status": "draft",
                    "placement": "dashboard-card",
                },
            ],
        },
        "error": None,
    }


@app.get("/api/admin/source-registry")
def admin_source_registry_api():
    status = get_scheme_fetch_status()
    payload = {
        "sources": status.get("source_registry", {}).get("sources", []),
        "scheduler": status.get("scheduler", {
            "status": "active",
            "frequency": "every 12 hours",
            "cron_expression": "0 */12 * * *",
            "last_run": None,
            "next_run": None,
            "job_name": "government_scheme_fetch",
        }),
    }
    return {"success": True, "data": payload, "error": None}


@app.get("/api/admin/audit-logs")
def admin_audit_logs_api(authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"success": True, "data": list_audit_logs(), "error": None}


@app.get("/api/admin/review-queue")
def admin_review_queue_api():
    status = get_scheme_fetch_status()
    payload = status.get("review_queue", {"status": "pass", "flagged_count": 0, "pending_count": 0, "items": []})
    return {"success": True, "data": payload, "error": None}


@app.post("/api/admin/review-queue/{scheme_id}/resolve")
def admin_review_queue_resolve(scheme_id: str, payload: dict, authorization: Optional[str] = Header(default=None)):
    token = get_bearer_token(authorization)
    try:
        jwt_payload = verify_token(token)
    except Exception as exc:  # pragma: no cover - security exception path
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    if jwt_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    entry = get_scheme_update_by_id(scheme_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Scheme not found")

    decision = str((payload or {}).get("decision", "pending")).strip().lower()
    reviewer = str((payload or {}).get("reviewer", jwt_payload.get("sub", "admin")).strip() or jwt_payload.get("sub", "admin"))
    reason = str((payload or {}).get("reason", "Reviewed by admin")).strip() or "Reviewed by admin"

    record = {
        "id": f"REVIEW-{uuid4().hex}",
        "scheme_id": scheme_id,
        "decision": decision,
        "reviewer": reviewer,
        "reason": reason,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO scheme_review_actions (id, scheme_id, decision, reviewer, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["scheme_id"],
                record["decision"],
                record["reviewer"],
                record["reason"],
                record["created_at"],
            ),
        )

    record_audit_log(reviewer, "scheme_review_resolved", "scheme_review_actions", "success", f"Scheme {scheme_id} marked as {decision}.")
    return {"success": True, "data": {"scheme_id": scheme_id, "decision": decision, "reviewer": reviewer, "reason": reason}, "error": None}


@app.get("/admin/review-queue", response_class=HTMLResponse)
def admin_review_queue_page():
    review_queue = get_scheme_fetch_status().get("review_queue", {"status": "pass", "flagged_count": 0, "pending_count": 0, "items": []})
    items = review_queue.get("items", [])
    if not items:
        row_html = """
        <article class='empty-state'>
          <h3>No flagged records</h3>
          <p>There are currently no scheme records waiting for manual admin review.</p>
        </article>
        """
    else:
        row_html = "\n".join(
            """
            <article class='review-item'>
              <div class='item-meta'>
                <span class='chip'>{category}</span>
                <span class='severity severity-{severity}'>{severity}</span>
              </div>
              <h3>{title}</h3>
              <p><strong>Source:</strong> {source}</p>
              <ul>
                {issues}
              </ul>
            </article>
            """.format(
                category=escape(str(item.get("category", "general"))),
                severity=escape(str(item.get("severity", "medium"))),
                title=escape(str(item.get("title", "Untitled scheme"))),
                source=escape(str(item.get("source_name", "Unknown source"))),
                issues="".join(f"<li>{escape(str(issue))}</li>" for issue in item.get("issues", [])),
            )
            for item in items
        )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Review Queue</title>
  <style>
    :root {{
      --bg: #f4f8f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --primary-soft: #ebf9ed;
      --secondary: #4aa6d6;
      --warning: #d97706;
      --danger: #b42318;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 28px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 52px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 14px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    .hero {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 24px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 12px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ display: block; color: var(--muted); font-size: 0.8rem; margin-bottom: 8px; }}
    .stat strong {{ display: block; font-size: 1.8rem; }}
    h1 {{ margin: 22px 0 8px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 72ch; }}
    .review-list {{ display: grid; gap: 18px; margin-top: 20px; }}
    .review-item {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 20px; box-shadow: var(--shadow); }}
    .item-meta {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; }}
    .chip {{ display: inline-block; padding: 7px 10px; background: var(--primary-soft); color: var(--primary); border-radius: 999px; font-weight: 800; font-size: 12px; }}
    .severity {{ display: inline-block; padding: 7px 10px; border-radius: 999px; font-weight: 800; font-size: 12px; }}
    .severity-high {{ background: #fef3c7; color: #92400e; }}
    .severity-medium {{ background: #e0f2fe; color: #075985; }}
    .review-item h3 {{ margin: 0 0 12px; font-size: 1.25rem; }}
    .review-item p, .review-item li {{ color: var(--muted); line-height: 1.8; }}
    .review-item ul {{ margin: 10px 0 0; padding-left: 18px; }}
    .empty-state {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 24px; box-shadow: var(--shadow); }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🧭</div>
        <span>Review Queue / மதிப்பாய்வு வரிசை</span>
      </div>
      <nav class="nav">
        <a href="/admin/overview">Admin</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/release-runbook">Release Runbook</a>
        <a href="/admin/operations-checklist">Operations Checklist</a>
      </nav>
    </header>

    <h1>Review Queue</h1>
    <p class="lede">Flagged scheme records are routed here for manual validation before publication or wider farmer-facing rollout.</p>

    <section class="hero">
      <div class="panel">
        <h2>Queue status</h2>
        <div class="stats">
          <div class="stat"><span>Flagged records</span><strong>{review_queue.get('flagged_count', 0)}</strong></div>
          <div class="stat"><span>Pending review</span><strong>{review_queue.get('pending_count', 0)}</strong></div>
        </div>
      </div>
      <div class="panel">
        <h2>Operational note</h2>
        <p class="lede">{escape(str(review_queue.get('status', 'pass'))).upper()} — schemes with incomplete summary, missing eligibility, or generic content are held for manual check.</p>
      </div>
    </section>

    <section class="review-list">
      {row_html}
    </section>
  </div>
</body>
</html>
"""


@app.get("/admin/audit-logs", response_class=HTMLResponse)
def admin_audit_logs_page():
    logs = list_audit_logs()
    rows = "".join(
        """
        <tr>
          <td>{username}</td>
          <td>{action}</td>
          <td>{resource}</td>
          <td>{outcome}</td>
          <td>{details}</td>
          <td>{created_at}</td>
        </tr>
        """.format(
            username=escape(str(item.get("username", "unknown"))),
            action=escape(str(item.get("action", "unknown"))),
            resource=escape(str(item.get("resource", "unknown"))),
            outcome=escape(str(item.get("outcome", "unknown"))),
            details=escape(str(item.get("details", ""))),
            created_at=escape(str(item.get("created_at", ""))),
        )
        for item in logs
    ) if logs else """
        <tr>
          <td colspan='6'>No audit events recorded yet.</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Audit Logs</title>
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
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 18px 52px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 72ch; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow); border: 1px solid var(--line); margin-top: 20px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 12px 14px; text-align: left; vertical-align: top; color: var(--text); }}
    th {{ background: #f7faf6; font-weight: 700; }}
    td {{ color: var(--muted); }}
    @media (max-width: 760px) {{ .topbar {{ flex-direction: column; align-items: flex-start; }} table {{ display: block; overflow-x: auto; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🧾</div>
        <span>Audit Logs / ஆடிட் பதிவுகள்</span>
      </div>
      <nav class="nav">
        <a href="/admin/overview">Admin</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/review-queue">Review Queue</a>
        <a href="/admin/source-registry">Source Registry</a>
      </nav>
    </header>

    <h1>Audit Logs</h1>
    <p class="lede">Every privileged action is recorded here so admins can review authentication, scheme review, and operational changes with an auditable trail.</p>

    <table>
      <thead>
        <tr>
          <th>User</th>
          <th>Action</th>
          <th>Resource</th>
          <th>Outcome</th>
          <th>Details</th>
          <th>Created At</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


@app.get("/admin/source-registry", response_class=HTMLResponse)
def admin_source_registry_page():
    status = get_scheme_fetch_status()
    sources = status.get("source_registry", {}).get("sources", [])
    scheduler = status.get("scheduler", {
        "status": "active",
        "frequency": "every 12 hours",
        "cron_expression": "0 */12 * * *",
        "last_run": None,
        "next_run": None,
        "job_name": "government_scheme_fetch",
    })
    source_rows = "".join(
        """
        <article class='card'>
          <div class='meta-row'>
            <span class='badge'>{name}</span>
            <span class='pill'>{type}</span>
          </div>
          <h3>{title}</h3>
          <p><strong>Source URL:</strong> <a href='{url}'>{url}</a></p>
          <p><strong>Trust level:</strong> {trust}</p>
          <p><strong>Last sync:</strong> {last_sync}</p>
        </article>
        """.format(
            name=escape(str(source.get("name", "Unknown source"))),
            type=escape(str(source.get("type", "general"))),
            title=escape(str(source.get("name", "Unknown source"))),
            url=escape(str(source.get("source_url", "#"))),
            trust=escape(str(source.get("trust_level", "medium"))),
            last_sync=escape(str(source.get("last_sync") or "Not synced yet")),
        )
        for source in sources
    ) or "<article class='card empty'><h3>No registered sources</h3><p>There are no trusted scheme sources configured yet.</p></article>"

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Source Registry</title>
  <style>
    :root {{
      --bg: #f4f8f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --accent: #eafaf0;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 52px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 72ch; }}
    .hero {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ display: block; font-size: 0.8rem; color: var(--muted); margin-bottom: 8px; }}
    .stat strong {{ display: block; font-size: 1.8rem; }}
    .card-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: var(--shadow); }}
    .card p {{ color: var(--muted); line-height: 1.7; }}
    .meta-row {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }}
    .badge {{ display: inline-block; border-radius: 999px; background: var(--accent); color: var(--primary); padding: 6px 10px; font-weight: 700; }}
    .pill {{ display: inline-block; border-radius: 999px; background: #edf5ff; color: #0f5f8c; padding: 6px 10px; font-weight: 700; }}
    a {{ color: var(--primary); }}
    @media (max-width: 760px) {{ .hero, .card-grid, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🧾</div>
        <span>Source Registry / மூலப் பதிவு</span>
      </div>
      <nav class="nav">
        <a href="/admin/overview">Admin</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/review-queue">Review Queue</a>
        <a href="/admin/content-config">Content Config</a>
      </nav>
    </header>

    <h1>Source Registry</h1>
    <p class="lede">The trusted source registry tracks active government and public scheme feeds, their compliance posture, and the scheduler that refreshes them.</p>

    <section class="hero">
      <div class="panel">
        <h2>Scheduler</h2>
        <div class="stats">
          <div class="stat"><span>Status</span><strong>{scheduler.get('status', 'active')}</strong></div>
          <div class="stat"><span>Frequency</span><strong>{scheduler.get('frequency', 'every 12 hours')}</strong></div>
          <div class="stat"><span>Cron</span><strong>{scheduler.get('cron_expression', '0 */12 * * *')}</strong></div>
        </div>
        <p class="lede">Job: {scheduler.get('job_name', 'government_scheme_fetch')} | Last run: {scheduler.get('last_run') or 'not yet'} | Next run: {scheduler.get('next_run') or 'scheduled'}</p>
      </div>
      <div class="panel">
        <h2>Operational note</h2>
        <p class="lede">Trusted feeds are checked for duplication, source drift, and publication quality before a record is surfaced to farmers.</p>
      </div>
    </section>

    <section class="card-grid">
      {source_rows}
    </section>
  </div>
</body>
</html>
"""


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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/release-runbook">Release Runbook</a>
        <a href="/admin/operations-checklist">Operations Checklist</a>
        <a href="/admin/content-config">Content Config</a>
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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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
    treatment_steps = "".join(f"<li>{escape(str(step))}</li>" for step in result.get("treatment_steps", [recommendation]))
    prevention_steps = "".join(f"<li>{escape(str(step))}</li>" for step in result.get("prevention_steps", ["Monitor the field closely and keep notes for the next review cycle."]))
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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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
          {treatment_steps}
        </ul>
      </article>

      <article class="card">
        <h3>தடுப்பு</h3>
        <ul>
          {prevention_steps}
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
    crop_recommendations_html = "".join(
        f"<li>{escape(str(item))}</li>" for item in assessment.get("crop_recommendations", [])
    )
    irrigation_guidance_html = "".join(
        f"<li>{escape(str(item))}</li>" for item in assessment.get("irrigation_guidance", [])
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
        <a href="/weather">வானிலை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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

    <section class="hero" style="margin-top: 18px;">
      <div class="panel">
        <span class="pill">பயிர் பரிந்துரை</span>
        <h2>பயிர் பரிந்துரை / Crop recommendations</h2>
        <ul>
          {crop_recommendations_html}
        </ul>
      </div>
      <div class="panel">
        <span class="pill">நீர் மேலாண்மை</span>
        <h2>நீர் மேலாண்மை / Irrigation guidance</h2>
        <ul>
          {irrigation_guidance_html}
        </ul>
      </div>
    </section>
  </div>
</body>
</html>
"""


@app.get("/soil-testing", response_class=HTMLResponse)
def soil_testing_page():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>மண் சோதனை</title>
  <style>
    :root {
      --bg: #f7f5ee;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --soil: #8f5e3c;
      --text: #17301d;
      --muted: #567163;
      --line: #ddebdc;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }
    .container { max-width: 900px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 0 20px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--soil)); color: white; }
    .nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .nav a { text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }
    .panel {
      margin-top: 26px; background: var(--panel); border: 1px solid var(--line); border-radius: 20px;
      box-shadow: var(--shadow); padding: 24px;
    }
    h1 { margin-top: 0; margin-bottom: 10px; font-size: clamp(2rem, 4vw, 2.7rem); }
    .lede { color: var(--muted); line-height: 1.8; }
    form { display: grid; gap: 18px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .field { display: flex; flex-direction: column; gap: 8px; }
    label { font-weight: 700; }
    input, select {
      border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; font-size: 1rem; color: var(--text); background: #fff;
    }
    .actions { display: flex; gap: 12px; flex-wrap: wrap; }
    button {
      border: none; border-radius: 12px; padding: 12px 18px; font-size: 1rem; font-weight: 700; cursor: pointer;
      background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white;
    }
    .secondary { background: #eff5ef; color: var(--text); border: 1px solid var(--line); }
    @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>மண் சோதனை</span>
      </div>
      <nav class="nav" aria-label="மண் சோதனை வழிசெலுத்தல்">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <section class="panel">
      <h1>மண் சோதனை மற்றும் உர திட்டம்</h1>
      <p class="lede">தற்போதைய மண் நிலையை எளிய படிவத்தில் உள்ளிடவும். pH, நைட்ரஜன், பாஸ்பரஸ் மற்றும் பொட்டாசியம் மதிப்புகள் அடிப்படையில் பயிர் சார்ந்த பரிந்துரை உருவாக்கப்படும்.</p>

      <form method="get" action="/soil-health">
        <div class="grid">
          <div class="field">
            <label for="crop">பயிர்</label>
            <select id="crop" name="crop">
              <option value="groundnut">நிலக்கடலை</option>
              <option value="rice">நெல்</option>
              <option value="tomato">தக்காளி</option>
              <option value="cotton">பருத்தி</option>
            </select>
          </div>
          <div class="field">
            <label for="ph">pH</label>
            <input id="ph" name="ph" type="number" step="0.1" value="6.5" placeholder="6.5" />
          </div>
          <div class="field">
            <label for="nitrogen">நைட்ரஜன்</label>
            <input id="nitrogen" name="nitrogen" type="number" step="1" value="25" placeholder="25" />
          </div>
          <div class="field">
            <label for="phosphorus">பாஸ்பரஸ்</label>
            <input id="phosphorus" name="phosphorus" type="number" step="1" value="20" placeholder="20" />
          </div>
          <div class="field">
            <label for="potassium">பொட்டாசியம்</label>
            <input id="potassium" name="potassium" type="number" step="1" value="180" placeholder="180" />
          </div>
        </div>

        <div class="actions">
          <button type="submit">சேமி</button>
          <button type="reset" class="secondary">மீட்டமை</button>
        </div>
      </form>
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
            return """
            <article class='empty-state'>
                <h3>உள்ளடக்கம் இல்லை</h3>
                <p>தற்போது தேர்ந்தெடுத்த வடிகட்டி அல்லது தேடல் அளவுருக்களுக்கு பொருந்தும் திட்டங்கள் எதுவும் இல்லை.</p>
            </article>
            """

        cards = []
        for item in items:
            title = escape(str(item.get("title_ta") or item.get("title_en") or "அரசு திட்டம்"))
            summary = escape(str(item.get("summary_ta") or item.get("summary_en") or "அரசியல் மற்றும் நிதி உதவி விவரங்கள் விரைவில் கிடைக்கும்."))
            scheme_id = escape(str(item.get("id", "")))
            category_name = escape(str(item.get("category", "")).title())
            eligibility = escape(str(item.get("eligibility_ta") or item.get("eligibility_en") or "தகுதி விவரங்கள் விரைவில் இடம் பெறும்."))
            steps = escape(str(item.get("apply_steps_ta") or item.get("apply_steps_en") or "விண்ணப்ப படிகள் விரைவில் இடம் பெறும்."))
            year_group = str(item.get("year_group") or "").strip()
            status_badge = f"{year_group}" if year_group else "புதியது"
            cards.append(
                """
                <article class='scheme-card'>
                  <div class='meta-row'>
                    <span class='pill'>{category_name}</span>
                    <span class='badge'>{status_badge}</span>
                  </div>
                  <h3>{title}</h3>
                  <p>{summary}</p>
                  <ul>
                    <li><strong>தகுதி:</strong> {eligibility}</li>
                    <li><strong>விண்ணப்பம்:</strong> {steps}</li>
                  </ul>
                  <a class='cta' href='/scheme-page/{scheme_id}'>மேலும் படிக்க</a>
                </article>
                """.format(
                    category_name=category_name,
                    status_badge=status_badge,
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
    latest_count = len(latest_entries)
    archive_count = len(archived_entries)
    template = """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>அரசு திட்டங்கள்</title>
  <style>
    :root {{
      --bg: #f4f9f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --primary-soft: #ebf9ed;
      --secondary: #4aa6d6;
      --accent: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 14px 32px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 56px; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 8px 0 22px;
      border-bottom: 1px solid var(--line);
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 800; letter-spacing: 0.02em; }}
    .logo {{ width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; box-shadow: var(--shadow); }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .nav a {{
      text-decoration: none;
      color: var(--text);
      background: #f4f8f4;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 700;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    .nav a.active, .nav a:hover {{
      background: linear-gradient(135deg, var(--primary-soft), #edf8ff);
      color: var(--primary);
      border-color: rgba(45, 125, 70, 0.25);
      box-shadow: 0 8px 18px rgba(45, 125, 70, 0.12);
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.5fr 0.9fr;
      gap: 20px;
      align-items: stretch;
      margin-top: 24px;
    }}
    .hero-copy, .hero-panel {{
      background: rgba(255,255,255,0.78);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: var(--shadow);
      padding: 24px;
    }}
    .eyebrow {{
      display: inline-block;
      padding: 7px 12px;
      border-radius: 999px;
      background: var(--primary-soft);
      color: var(--primary);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 16px;
    }}
    h1 {{ margin: 0 0 14px; font-size: clamp(2.1rem, 4vw, 3.2rem); line-height: 1.15; }}
    .intro {{ color: var(--muted); line-height: 1.85; max-width: 70ch; margin: 0; }}
    .hero-panel {{ display: grid; gap: 14px; align-content: center; }}
    .stat-box {{
      background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
    }}
    .stat-box span {{ display: block; color: var(--muted); font-size: 0.82rem; margin-bottom: 8px; }}
    .stat-box strong {{ display: block; font-size: clamp(1.8rem, 3vw, 2.3rem); line-height: 1.1; }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      margin: 24px 0 18px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.7);
      box-shadow: 0 10px 22px rgba(23, 48, 29, 0.04);
    }}
    .search, .filter {{
      flex: 1;
      min-width: 180px;
      max-width: 260px;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 14px;
      font-size: 0.96rem;
      background: var(--panel);
      color: var(--text);
    }}
    .filter {{ max-width: 220px; }}
    .primary-btn, .secondary-btn {{
      border: none;
      border-radius: 12px;
      padding: 12px 18px;
      font-weight: 800;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    .primary-btn {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .secondary-btn {{ background: var(--panel); border: 1px solid var(--line); color: var(--text); }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin: 10px 0 24px;
    }}
    .summary-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 8px 20px rgba(23, 48, 29, 0.04);
    }}
    .summary-card .label {{ display: block; color: var(--muted); font-size: 0.78rem; letter-spacing: 0.03em; text-transform: uppercase; margin-bottom: 8px; }}
    .summary-card strong {{ font-size: 1.8rem; }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 10px;
      margin-bottom: 14px;
    }}
    .section-head h2 {{ margin: 0; font-size: 1.45rem; }}
    .section-head span {{ color: var(--muted); font-weight: 700; }}
    .scheme-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    .scheme-card, .empty-state {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--shadow);
    }}
    .meta-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .pill {{
      display: inline-block;
      background: var(--primary-soft);
      color: var(--primary);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
    }}
    .badge {{
      display: inline-block;
      background: #fff3da;
      color: var(--accent);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 11px;
      font-weight: 800;
    }}
    .scheme-card h3 {{ margin: 0 0 10px; font-size: 1.25rem; line-height: 1.45; }}
    .scheme-card p, .scheme-card li, .empty-state p {{ color: var(--muted); line-height: 1.8; }}
    .scheme-card ul {{ margin: 16px 0 0; padding-left: 18px; }}
    .scheme-card li {{ margin-bottom: 6px; }}
    .cta {{
      display: inline-flex;
      margin-top: 16px;
      padding: 10px 14px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--primary), var(--secondary));
      color: #fff;
      text-decoration: none;
      font-weight: 800;
    }}
    .empty-state h3 {{ margin-top: 0; margin-bottom: 10px; }}
    @media (max-width: 760px) {{
      .hero, .summary-grid, .scheme-grid {{ grid-template-columns: 1fr; }}
      .topbar {{ flex-direction: column; align-items: flex-start; }}
      .toolbar {{ flex-direction: column; align-items: stretch; }}
      .search, .filter {{ max-width: none; }}
      .section-head {{ flex-direction: column; align-items: flex-start; }}
    }}
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
        <a href="/" class="nav-link" data-page="/">முகப்பு</a>
        <a href="/dashboard" class="nav-link" data-page="/dashboard">டாஷ்போர்டு</a>
        <a href="/services" class="nav-link" data-page="/services">சேவைகள்</a>
        <a href="/government-schemes" class="nav-link active" data-page="/government-schemes">அரசுத் திட்டங்கள்</a>
      </nav>
    </header>

    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Farmer support</div>
        <h1>அரசு திட்டங்கள் மற்றும் நிதி உதவிகள்</h1>
        <p class="intro">
          விவசாயிகளுக்கு கிடைக்கும் புதிய மானியங்கள், பயிர் காப்பீடு, நிதி உதவிகள், பயிற்சி திட்டங்கள் மற்றும் அரசு ஒப்புதல்கள் ஆகியவற்றை தமிழில் எளிதாகப் புரியும் வகையில் ஒரே இடத்தில் வழங்கப்படுகிறது.
        </p>
      </div>
      <aside class="hero-panel" aria-label="திட்ட விரைவு குறிப்பு">
        <div class="stat-box">
          <span>மொத்த அறிவிப்புகள்</span>
          <strong>{latest_count}</strong>
        </div>
        <div class="stat-box">
          <span>காப்பக பதிவுகள்</span>
          <strong>{archive_count}</strong>
        </div>
        <div class="stat-box">
          <span>நேரடி உதவி</span>
          <strong>24/7</strong>
        </div>
      </aside>
    </section>

    <form class="toolbar" method="get" action="/government-schemes">
      <input class="search" type="text" name="search" value="__SEARCH__" aria-label="தேடுக" placeholder="தேடுக" />
      <select class="filter" name="category" aria-label="வகை">
        <option value="">வகை: அனைத்தும்</option>
        <option value="subsidy" __SUBSIDY_SELECTED__>subsidy</option>
        <option value="insurance" __INSURANCE_SELECTED__>insurance</option>
      </select>
      <button type="submit" class="primary-btn">வடிகட்டு</button>
      <a class="secondary-btn" href="/government-schemes">அனைத்தும்</a>
    </form>

    <section class="summary-grid" aria-label="திட்ட சுருக்கம்">
      <div class="summary-card">
        <span class="label">புதிய அறிவிப்புகள்</span>
        <strong>{latest_count}</strong>
      </div>
      <div class="summary-card">
        <span class="label">காப்பகப் பதிவுகள்</span>
        <strong>{archive_count}</strong>
      </div>
      <div class="summary-card">
        <span class="label">நிறைவு நிலை</span>
        <strong>சேவை</strong>
      </div>
    </section>

    <div class="section-head">
      <h2>புதிய அறிவிப்புகள்</h2>
      <span>Last 7 Days</span>
    </div>
    <section class="scheme-grid">
      __LATEST_HTML__
    </section>

    <div class="section-head" style="margin-top: 32px;">
      <h2>காப்பக அறிவிப்புகள்</h2>
      <span>Archive</span>
    </div>
    <section class="scheme-grid">
      __ARCHIVE_HTML__
    </section>
  </div>
  <script>
    const activePath = window.location.pathname || '/';
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach((link) => {
      const page = link.dataset.page || '/';
      link.classList.toggle('active', page === activePath || (page === '/' && activePath === '/'));
    });
  </script>
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
      --bg: #f4f9f1;
      --panel: #ffffff;
      --primary: #2d7d46;
      --primary-soft: #ebf9ed;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 14px 32px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
      color: var(--text);
    }}
    .container {{ max-width: 980px; margin: 0 auto; padding: 28px 18px 56px; }}
    .nav {{ margin-bottom: 18px; }}
    .nav a {{
      text-decoration: none;
      color: var(--text);
      background: #f4f8f4;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 700;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 18px;
    }}
    .tag {{
      display: inline-block;
      background: var(--primary-soft);
      color: var(--primary);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .status {{
      display: inline-block;
      background: #fff3da;
      color: #9a5d00;
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 12px;
      font-weight: 800;
    }}
    h1 {{ font-size: clamp(2rem, 4vw, 3rem); margin: 0 0 18px; line-height: 1.2; }}
    .summary {{
      background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 22px;
    }}
    .summary strong {{ display: block; margin-bottom: 6px; }}
    p, li {{ color: var(--muted); line-height: 1.9; }}
    ul {{ padding-left: 18px; }}
    .section {{ margin-top: 24px; }}
    .section h2 {{ margin: 0 0 10px; font-size: 1.2rem; }}
    .source-box {{
      margin-top: 22px;
      padding: 18px;
      border: 1px solid var(--line);
      background: #f8fbf8;
      border-radius: 16px;
    }}
    @media (max-width: 640px) {{
      .panel {{ padding: 20px; }}
      .meta-row {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="nav">
      <a href="/government-schemes">← அரசுத் திட்டங்கள்</a>
    </div>
    <div class="panel">
      <div class="meta-row">
        <span class="tag">{entry['category']}</span>
        <span class="status">சேவை கிடைக்கிறது</span>
      </div>

      <h1>{entry['title_ta']}</h1>

      <div class="summary">
        <strong>சுருக்கம்</strong>
        <p>{entry['summary_ta']}</p>
      </div>

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

      <div class="source-box">
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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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


@app.get("/weather", response_class=HTMLResponse)
def weather_page(
    region: str = "Kallakurichi",
    period: str = "daily",
    district: str = "",
    taluk: str = "",
    village: str = "",
):
    region_name = (region or "Kallakurichi").strip() or "Kallakurichi"
    district_name = (district or "").strip() or "Villupuram"
    taluk_name = (taluk or "").strip() or "Kallakurichi"
    village_name = (village or "").strip() or "Periyar Nagar"
    period_name = (period or "daily").strip().lower() or "daily"
    forecasts = list_weather_forecast(period_name, region_name)
    if not forecasts:
        forecasts = list_weather_forecast(period_name, "Kallakurichi")
    if not forecasts:
        forecasts = [{
            "region": region_name,
            "period": period_name,
            "summary_ta": "இன்று வானம் மேகமூட்டமாக இருக்கும். மழை சாத்தியம் உள்ளது.",
            "temperature_c": 29.0,
            "rainfall_mm": 18.0,
            "humidity_pct": 68,
            "wind_kmh": 18.0,
            "advisory_ta": "மண்ணின் ஈரப்பதத்தை பரிசோதித்து, குறைந்தபட்ச பாசன அட்டவணையை பின்பற்றவும்.",
        }]

    forecast = forecasts[0]
    summary = escape(str(forecast.get("summary_ta", "இன்று வானம் மேகமூட்டமாக இருக்கும். மழை சாத்தியம் உள்ளது.")))
    advisory = escape(str(forecast.get("advisory_ta", "மண்ணின் ஈரப்பதத்தை பரிசோதித்து, குறைந்தபட்ச பாசன அட்டவணையை பின்பற்றவும்.")))
    temp = float(forecast.get("temperature_c", 29.0))
    rainfall = float(forecast.get("rainfall_mm", 18.0))
    humidity = float(forecast.get("humidity_pct", 68.0))
    wind = float(forecast.get("wind_kmh", 18.0))
    alerts = list_weather_alerts(village_name)
    if not alerts:
        alerts = list_weather_alerts(region_name)
    if not alerts:
        alerts = list_weather_alerts("Kallakurichi")
    alert = alerts[0] if alerts else None
    alert_title = escape(str(getattr(alert, "alert_type", "Rainstorm") if alert else "Rainstorm"))
    alert_severity = escape(str(getattr(alert, "severity", "High") if alert else "High"))
    alert_message = escape(str(getattr(alert, "message", "Heavy rainfall expected. Protect standing crops and delay field work.") if alert else "Heavy rainfall expected. Protect standing crops and delay field work."))

    if period_name == "weekly":
        weekly_cards = "".join(
            [
                f"<div class='metric'><span>{day}</span><strong>{temp_val}°C</strong><small>{rain_val} mm / மழை</small></div>"
                for day, temp_val, rain_val in [
                    ("திங்கள்", 30, 18),
                    ("செவ்வாய்", 31, 22),
                    ("புதன்", 29, 26),
                    ("வியாழன்", 30, 15),
                    ("வெள்ளி", 32, 12),
                    ("சனி", 31, 14),
                    ("ஞாயிறு", 29, 20),
                ]
            ]
        )
        period_section = f"""
        <section class=\"hero\">
          <div class=\"panel\">
            <h2>7 நாள் முன்னறிவிப்பு / 7-day forecast</h2>
            <div class=\"metrics\" style=\"grid-template-columns: repeat(auto-fit, minmax(116px, 1fr));\">{weekly_cards}</div>
          </div>
          <div class=\"panel\">
            <h2>எச்சரிக்கை / Warning</h2>
            <ul>
              <li><strong>{alert_title}</strong> ({alert_severity})</li>
              <li>{alert_message}</li>
            </ul>
            <h2 style=\"margin-top:18px;\">பயிர் பரிந்துரை / Crop Advisory</h2>
            <ul>
              <li>மழை மற்றும் வெப்பநிலை மாற்றத்தை கணக்கிட்டு, பாசன நேரத்தை மாற்றியமைக்கவும்.</li>
              <li>நெல், கரும்பு, மற்றும் பருத்தி பயிர்களுக்கு 7 நாள் மழை மாறுபாட்டை கருத்தில் கொண்டு உரமிடுதல் திட்டமிடவும்.</li>
            </ul>
          </div>
        </section>
        """
    elif period_name == "monthly":
        period_section = f"""
        <section class=\"hero\">
          <div class=\"panel\">
            <h2>மாதாந்திர பருவ முன்னறிவிப்பு / Monthly seasonal forecast</h2>
            <div class=\"metrics\">
              <div class=\"metric\"><span>மழை எதிர்பார்ப்பு</span><strong>{rainfall + 20:.0f} mm</strong></div>
              <div class=\"metric\"><span>சராசரி வெப்பநிலை</span><strong>{temp + 1:.0f}°C</strong></div>
              <div class=\"metric\"><span>பருவ காலம்</span><strong>தெற்கு பருவம்</strong></div>
            </div>
          </div>
          <div class=\"panel\">
            <h2>எச்சரிக்கை / Warning</h2>
            <ul>
              <li><strong>{alert_title}</strong> ({alert_severity})</li>
              <li>{alert_message}</li>
            </ul>
            <h2 style=\"margin-top:18px;\">பயிர் பரிந்துரை / Crop plan</h2>
            <ul>
              <li>மாத இறுதியில் மழை மற்றும் வெப்பநிலை மாறுபாடு காரணமாக, நீர் மேலாண்மை திட்டத்தை புதுப்பிக்கவும்.</li>
              <li>நெல், கரும்பு, மற்றும் பயறு வகை பயிர்களுக்கு உர இடுதல் மற்றும் சாகுபடி நேரம் மறு ஆய்வு செய்யப்பட வேண்டும்.</li>
            </ul>
          </div>
        </section>
        """
    else:
        period_section = f"""
        <section class=\"hero\">
          <div class=\"panel\">
            <h2>இன்றைய நிலை / Current Status</h2>
            <div class=\"metrics\">
              <div class=\"metric\"><span>வெப்பநிலை</span><strong>{temp:.0f}°C</strong></div>
              <div class=\"metric\"><span>மழை</span><strong>{rainfall:.0f} mm</strong></div>
              <div class=\"metric\"><span>ஈரப்பதம்</span><strong>{humidity:.0f}%</strong></div>
            </div>
            <div class=\"metrics\" style=\"margin-top:14px;\">
              <div class=\"metric\"><span>காற்று</span><strong>{wind:.0f} km/h</strong></div>
              <div class=\"metric\"><span>காலம்</span><strong>{period_name.upper()}</strong></div>
              <div class=\"metric\"><span>மண்டலம்</span><strong>{escape(region_name)}</strong></div>
            </div>
          </div>

          <div class=\"panel\">
            <h2>எச்சரிக்கை / Warning</h2>
            <ul>
              <li><strong>{alert_title}</strong> ({alert_severity})</li>
              <li>{alert_message}</li>
            </ul>
            <h2 style=\"margin-top:18px;\">பரிந்துரை / Advisory</h2>
            <ul>
              <li>{advisory}</li>
              <li>மண் ஈரப்பதத்தை தொடர்ந்து கண்காணிக்கவும்.</li>
            </ul>
          </div>
        </section>
        """

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>வானிலை முன்னறிவிப்பு</title>
  <style>
    :root {{
      --bg: #f4f8f2;
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
      margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text);
    }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .metric {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .metric span {{ color: var(--muted); }}
    .metric strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    .meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
    .meta-item {{ border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; background: #fbfdfb; font-size: 0.95rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .metrics, .meta {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌤️</div>
        <span>{escape(region_name)} வானிலை / Weather</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>வானிலை முன்னறிவிப்பு</h1>
    <p class="lede">{summary}</p>

    <div class="meta">
      <div class="meta-item"><strong>District:</strong> {escape(district_name)}</div>
      <div class="meta-item"><strong>Taluk:</strong> {escape(taluk_name)}</div>
      <div class="meta-item"><strong>Village:</strong> {escape(village_name)}</div>
    </div>

    {period_section}
  </div>
</body>
</html>
"""


@app.get("/weather-quality", response_class=HTMLResponse)
def weather_quality_page():
    status = get_weather_fetch_status()
    source_list = " | ".join(status.get("source_whitelist", [])) or "IMD"
    fallback_list = " | ".join(status.get("fallback_sources", [])) or "Regional field station"
    retention = status.get("archive_policy", {})
    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weather Quality</title>
  <style>
    :root {{
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .meta {{ display: grid; gap: 12px; margin-top: 18px; }}
    .meta-item {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; background: #fbfdfb; }}
    ul {{ color: var(--muted); line-height: 1.9; padding-left: 18px; margin: 0; }}
    @media (max-width: 760px) {{ .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🛰️</div>
        <span>Trusted weather sources / நம்பகமான வானிலை மூலங்கள்</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>வானிலை தரக் கட்டுப்பாடு</h1>
    <p class="lede">அதிகாரப்பூர்வ வானிலை ஆதாரங்கள், தக்கவைப்பு கொள்கை மற்றும் அட்மின் கண்காணிப்பு ஆகியவற்றை ஒரே பார்வையில் சரிபார்க்கிறது.</p>

    <section class="panel">
      <h2>Trusted weather sources / நம்பகமான மூலங்கள்</h2>
      <div class="meta">
        <div class="meta-item"><strong>Whitelist:</strong> {escape(source_list)}</div>
        <div class="meta-item"><strong>Fallback / Secondary:</strong> {escape(fallback_list)}</div>
        <div class="meta-item"><strong>Current feed:</strong> {escape(str(status.get('last_source_name') or 'IMD'))}</div>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>Retention and archive / தக்கவைப்பு மற்றும் காப்பகம்</h2>
      <ul>
        <li>Latest window: {retention.get('latest_window_days', 7)} days</li>
        <li>Archive after: {retention.get('archive_after_days', 7)} days</li>
        <li>Monthly retention: {retention.get('monthly_retention_months', 12)} months</li>
        <li>Status: {escape(str(retention.get('status', 'pass')))}</li>
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/market-intelligence", response_class=HTMLResponse)
def market_intelligence_page(crop: str = "rice", market: str = "Kallakurichi"):
    from digital_farming.services.market_intelligence import get_market_intelligence

    intelligence = get_market_intelligence(crop=crop, market=market)
    crop_name = escape(str(crop or "நெல்").strip() or "நெல்")
    market_name = escape(str(market or "கல்லக்குறிச்சி"))
    trend = escape(str(intelligence.get("market_trend", "Moderate")))
    base_price = float(intelligence.get("base_price_per_kg", 0.0))
    recommendation = escape(str(intelligence.get("recommended_action", "Monitor local buyer demand and negotiate before the next supply surge.")))
    buyer_insights = "".join(f"<li>{escape(str(item))}</li>" for item in intelligence.get("buyer_insights", []))

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>சந்தை நுண்ணறிவு</title>
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
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ color: var(--muted); }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">📈</div>
        <span>{market_name} சந்தை / Market</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>{crop_name} பயிர் சந்தை நுண்ணறிவு</h1>
    <p class="lede">சந்தை போக்கு, விலை நிலை, மற்றும் விற்பனை முடிவுகளுக்கு தேவையான குறிப்புகளை தமிழில் காண்பிக்கிறது.</p>

    <section class="hero">
      <div class="panel">
        <h2>விலை நிலை / Price</h2>
        <div class="stats">
          <div class="stat"><span>விலை</span><strong>₹{base_price:.2f} / கிலோ</strong></div>
          <div class="stat"><span>போக்கு</span><strong>{trend}</strong></div>
          <div class="stat"><span>சந்தை</span><strong>{market_name}</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>பரிந்துரை / Recommendation</h2>
        <ul>
          <li>{recommendation}</li>
          <li>விற்பனை நேரம், தரம், மற்றும் திரட்டு செலவுகளை ஒரே பார்வையில் மதிப்பிடவும்.</li>
        </ul>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>கையகப்படுத்துபவர் குறிப்புகள் / Buyer insights</h2>
      <ul>
        {buyer_insights}
      </ul>
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
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
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
          <div class="metric"><span>மழை</span><strong>{float(forecast.get('rainfall_mm', 18.0)):.0f} mm</strong></div>
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


@app.get("/sustainability", response_class=HTMLResponse)
def sustainability_page(
    farm_size_ha: float = 5.0,
    soil_carbon_tons: float = 2.4,
    water_use_liters: float = 4200.0,
    energy_use_kwh: float = 320.0,
):
    from digital_farming.services.sustainability import assess_carbon_and_sustainability

    report = assess_carbon_and_sustainability(
        farm_size_ha=farm_size_ha,
        soil_carbon_tons=soil_carbon_tons,
        water_use_liters=water_use_liters,
        energy_use_kwh=energy_use_kwh,
    )

    recommendations = "".join(f"<li>{escape(str(item))}</li>" for item in report.get("recommendations", []))
    regenerative_actions = "".join(f"<li>{escape(str(item))}</li>" for item in report.get("regenerative_actions", []))
    regeneration_status = escape(str(report.get("regeneration_status", "Regenerative performance is being monitored.")))
    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>நிலையான விவசாயம்</title>
  <style>
    :root {{
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ color: var(--muted); }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌱</div>
        <span>நிலையான விவசாயம்</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>நிலையான விவசாய மதிப்பீடு</h1>
    <p class="lede">மண்ணின் கார்பன், நீர் பயன்பாடு மற்றும் ஆற்றல் திறன் ஆகியவற்றை ஒரே பார்வையில் மதிப்பிட்டு, அடுத்த பருவத்திற்கான முன்னேற்றத்தை திட்டமிடுகிறது.</p>

    <section class="hero">
      <div class="panel">
        <h2>கார்பன் மற்றும் நீர் செயல்திறன்</h2>
        <div class="stats">
          <div class="stat"><span>கார்பன் ஸ்கோர்</span><strong>{report['carbon_score']}</strong></div>
          <div class="stat"><span>நீர் திறன்</span><strong>{report['water_efficiency_m3_per_ha']} m³/ha</strong></div>
          <div class="stat"><span>ஆற்றல்</span><strong>{report['energy_use_kwh_per_ha']} kWh/ha</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>நிலை / Status</h2>
        <ul>
          <li>{escape(str(report.get('carbon_status', 'Carbon status available')))}</li>
          <li>Regenerative status / மறு உற்பத்தி நிலை: {regeneration_status}</li>
          <li>குடும்ப அல்லது குழு நிலை: {float(report.get('farm_size_ha', 0.0))} ஹெக்டேர்ஸ்</li>
          <li>மண் கார்பன்: {float(report.get('soil_carbon_tons', 0.0))} டன்</li>
        </ul>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>Regenerative actions / மீளுருவாக்கும் நடவடிக்கைகள்</h2>
      <ul>
        {regenerative_actions}
      </ul>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>பரிந்துரை / Recommendation</h2>
      <ul>
        {recommendations}
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/traceability", response_class=HTMLResponse)
def traceability_page(
    farmer: str = "Kumaran",
    batch: str = "RICE-24A",
    location: str = "Kallakurichi",
    quality_grade: str = "A",
):
    from digital_farming.services.traceability import build_traceability_summary

    traceability = build_traceability_summary(
        farmer=farmer,
        batch=batch,
        location=location,
        quality_grade=quality_grade,
    )

    steps = "".join(f"<li>{escape(str(step))}</li>" for step in traceability.get("procurement_steps", []))
    custody_steps = "".join(f"<li>{escape(str(step))}</li>" for step in traceability.get("chain_of_custody", []))
    lot_lifecycle = "".join(f"<li>{escape(str(step))}</li>" for step in traceability.get("lot_lifecycle", []))
    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>குழு மற்றும் லாட் கண்காணிப்பு</title>
  <style>
    :root {{
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ color: var(--muted); }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">📦</div>
        <span>கால்நடை/பயிர் கண்காணிப்பு</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/register">பதிவு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>கால்காணிப்பு மற்றும் லாட் கண்காணிப்பு</h1>
    <p class="lede">பயிர், விவசாயி, இருப்பிடம் மற்றும் தரம் ஆகியவற்றை ஒரே வரிசையில் புரிந்து கொண்டு, கொள்முதல் மற்றும் பரிமாற்ற செயல்முறையை தெளிவாக்குகிறது.</p>

    <section class="hero">
      <div class="panel">
        <h2>லாட் விவரம் / Batch</h2>
        <div class="stats">
          <div class="stat"><span>விவசாயி</span><strong>{escape(str(traceability.get('farmer', farmer)))}</strong></div>
          <div class="stat"><span>பேட்ச்</span><strong>{escape(str(traceability.get('batch', batch)))}</strong></div>
          <div class="stat"><span>வகுப்பு / Grade</span><strong>{escape(str(traceability.get('quality_grade', quality_grade)))}</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>நிலை / Status</h2>
        <ul>
          <li>{escape(str(traceability.get('traceability_status', 'Traceability verified')))}</li>
          <li>இடம்: {escape(str(traceability.get('location', location)))}</li>
          <li>தொடர்பு முறை: lot trace confirmed</li>
        </ul>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>Chain of custody / பாதுகாப்பு சங்கிலி</h2>
      <ul>
        {custody_steps}
      </ul>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>Lot lifecycle / லாட் வாழ்க்கைச் சுழற்சி</h2>
      <ul>
        {lot_lifecycle}
      </ul>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>விளையாட்டு / Procurement steps</h2>
      <ul>
        {steps}
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/admin/content-config", response_class=HTMLResponse)
def admin_content_config_page():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Content Configuration</title>
  <style>
    :root {{
      --bg: #f4f8f2;
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
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .chip {{ display: inline-block; padding: 5px 10px; border-radius: 999px; background: #ebf9ef; color: var(--primary); font-weight: 700; margin-bottom: 10px; }}
    ul {{ margin: 10px 0 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">📣</div>
        <span>Content Configuration / உள்ளடக்க கட்டுப்பாடு</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/admin/overview">Admin</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/release-runbook">Release Runbook</a>
        <a href="/admin/operations-checklist">Operations Checklist</a>
      </nav>
    </header>

    <h1>Special News & Advertising</h1>
    <p class="lede">This content management screen allows admins to review special news announcements and advertising placements intended for the farmer experience.</p>

    <section class="grid">
      <article class="panel">
        <span class="chip">Special News</span>
        <h2>சிறப்பு செய்திகள்</h2>
        <ul>
          <li>Kharif advisory window open for registered farmer groups.</li>
          <li>Operator bulletin for seasonal rainfall risk is scheduled for release.</li>
          <li>Priority broadcast channel remains the village operator network.</li>
        </ul>
      </article>

      <article class="panel">
        <span class="chip">Advertising</span>
        <h2>விளம்பரம்</h2>
        <ul>
          <li>Seed supplier campaign is active on the home banner.</li>
          <li>Irrigation subsidy promotion is in draft mode for dashboard placement.</li>
          <li>All advertising blocks remain within approved regional targeting.</li>
        </ul>
      </article>
    </section>
  </div>
</body>
</html>
"""


@app.get("/admin/release-runbook", response_class=HTMLResponse)
def admin_release_runbook_page():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Release Runbook</title>
  <style>
    :root {{
      --bg: #f4f8f2;
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
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); margin-top: 20px; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🚀</div>
        <span>Release Runbook / ரிலீஸ் ரன்ன்புக்</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/operations-checklist">Operations Checklist</a>
      </nav>
    </header>

    <h1>Release Runbook</h1>
    <p class="lede">இந்த வெளியீட்டு விரிவுரை, மேம்பாடு, அரை-சோதனை, சுகாதார சரிபார்ப்பு, மற்றும் மீட்டெடுப்பு நடைமுறைகளை ஒரே இடத்தில் காட்டுகிறது.</p>

    <section class="panel">
      <h2>Deployment checklist / நிறுவல் பட்டியல்</h2>
      <ul>
        <li>Confirm environment values are loaded from .env or the deployment runtime.</li>
        <li>Validate Python dependencies and pinned versions before the release.</li>
        <li>Verify the app boots with uvicorn or the configured container command.</li>
        <li>Check weather, scheme, and admin health endpoints before promoting release.</li>
        <li>Document the release owner, region, and deployment timestamp for audit tracking.</li>
      </ul>
    </section>

    <section class="panel">
      <h2>Health check / சுகாதார சரிபார்ப்பு</h2>
      <ul>
        <li>Run the backend health endpoint and confirm the service status is healthy.</li>
        <li>Verify weather source compliance and scheme source compliance remain in pass or warning states.</li>
        <li>Inspect latest fetch dates for weather and scheme records before release sign-off.</li>
        <li>Review admin quality gate output and confirm all critical metrics are within expected thresholds.</li>
      </ul>
    </section>

    <section class="panel">
      <h2>Rollback plan / மீட்டெடுப்பு திட்டம்</h2>
      <ul>
        <li>Revert to the previous tagged build if any user-facing route returns error or data mismatch.</li>
        <li>Restore the previous database snapshot when a migration or seed operation introduces instability.</li>
        <li>Turn off fetch jobs or source updates until the affected source is reviewed and revalidated.</li>
        <li>Notify admins, support staff, and operators with the issue summary and rollback status.</li>
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/admin/operations-checklist", response_class=HTMLResponse)
def admin_operations_checklist_page():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Operations Checklist</title>
  <style>
    :root {{
      --bg: #f7f6f0;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --warning: #d97706;
      --text: #17301d;
      --muted: #567163;
      --line: #e0e9e1;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eff9f0 0%, #f8f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); margin-top: 20px; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🧰</div>
        <span>Operations Checklist / இயக்கத் தேர்வுப்பட்டி</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/admin/overview">Admin</a>
        <a href="/admin/quality-gate">Quality Gate</a>
        <a href="/admin/release-runbook">Release Runbook</a>
      </nav>
    </header>

    <h1>Operations Checklist</h1>
    <p class="lede">தேவையான தரவு காப்புப்பிரதி, மைக்ரேஷன், செயல்பாட்டு சோதனை மற்றும் வெளியீட்டு சீரான செயல்பாட்டை உறுதிசெய்வதற்கான அட்மின் சின்னம் பட்டியல்.</p>

    <section class="panel">
      <h2>Backup readiness / காப்பு தயார்</h2>
      <ul>
        <li>Take a fresh database snapshot before every release or schema change.</li>
        <li>Archive farm, weather, and scheme data to a recoverable storage target.</li>
        <li>Validate that backup restoration works in a staging or test environment.</li>
        <li>Confirm the backup process is time-stamped and ownership is assigned.</li>
      </ul>
    </section>

    <section class="panel">
      <h2>Migration readiness / மைக்ரேஷன் தயார்</h2>
      <ul>
        <li>Review schema migration scripts before applying them to the live environment.</li>
        <li>Verify that seed data and existing records remain compatible after migration.</li>
        <li>Run a dry-run or preflight validation before production rollout.</li>
        <li>Capture rollback steps for every migration to support controlled recovery.</li>
      </ul>
    </section>

    <section class="panel">
      <h2>Release sign-off / வெளியீட்டு ஒப்புதல்</h2>
      <ul>
        <li>Check weather and scheme source compliance statuses in the admin quality gate.</li>
        <li>Confirm health checks, fetch status, and alert coverage are in the expected range.</li>
        <li>Approve only after the rollback, backup, and migration checks are recorded.</li>
        <li>Document final owner, location, and validation timestamp for the deployment record.</li>
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/admin/quality-gate", response_class=HTMLResponse)
def admin_quality_gate_page():
    weather_status = get_weather_fetch_status()
    scheme_status = get_scheme_fetch_status()
    quality_gate = {
        "overall_status": "healthy" if weather_status.get("total_records", 0) > 0 and scheme_status.get("total_schemes", 0) > 0 else "warning",
        "weather": weather_status,
        "schemes": scheme_status,
    }

    weather_source_status = quality_gate["weather"].get("source_compliance", {}).get("status", "warning")
    scheme_source_status = quality_gate["schemes"].get("source_compliance", {}).get("status", "warning")
    ai_validation = quality_gate["schemes"].get("ai_validation", {})
    ai_status = ai_validation.get("status", "warning")
    readability_state = ai_validation.get("readability_check", "warning")

    weather_regions = " | ".join(f"{key}:{value}" for key, value in (quality_gate["weather"].get("regions") or {}).items()) or "இல்லை"
    scheme_categories = " | ".join(f"{key}:{value}" for key, value in (quality_gate["schemes"].get("categories") or {}).items()) or "இல்லை"

    source_names = [
        quality_gate["weather"].get("last_source_name"),
        quality_gate["schemes"].get("last_source_name"),
    ]
    source_names = [item for item in source_names if item]
    sources_text = " | ".join(source_names) if source_names else "மூலம் எதுவும் பதிவு செய்யப்படவில்லை"

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Quality Gate</title>
  <style>
    :root {{
      --bg: #f4f8f2;
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
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ color: var(--muted); }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🛡️</div>
        <span>Quality Gate / தரக் கட்டுப்பாடு</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/admin/overview">Admin</a>
        <a href="/admin/release-runbook">Release Runbook</a>
        <a href="/admin/operations-checklist">Operations Checklist</a>
      </nav>
    </header>

    <h1>Quality Gate</h1>
    <p class="lede">வானிலை தரவு, அரசு திட்ட புதுப்பிப்புகள், மற்றும் மூலநிலை ஆகியவற்றின் நம்பகத்தன்மை மற்றும் தர மதிப்பீடு ஆகியவற்றை ஒரே பார்வையில் சோதிக்கிறது.</p>

    <section class="hero">
      <div class="panel">
        <h2>தர நிலை / Health</h2>
        <div class="stats">
          <div class="stat"><span>ஒட்டுமொத்த நிலை</span><strong>{escape(str(quality_gate['overall_status']))}</strong></div>
          <div class="stat"><span>வானிலை பதிவுகள்</span><strong>{quality_gate['weather'].get('total_records', 0)}</strong></div>
          <div class="stat"><span>அரசு திட்டங்கள்</span><strong>{quality_gate['schemes'].get('total_schemes', 0)}</strong></div>
        </div>
      </div>

      <div class="panel">
        <h2>மூலம் / Source</h2>
        <ul>
          <li>{escape(sources_text)}</li>
          <li>வானிலை: {escape(weather_regions)}</li>
          <li>அரசு திட்டங்கள்: {escape(scheme_categories)}</li>
        </ul>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>வானிலை / Weather</h2>
      <ul>
        <li>மீண்டும் புதுப்பித்த நேரம்: {escape(str(quality_gate['weather'].get('last_updated_at', 'பதிவு இல்லை')))}</li>
        <li>தினசரி பதிவுகள்: {quality_gate['weather'].get('daily_records', 0)}</li>
        <li>மண்டலங்கள்: {escape(weather_regions)}</li>
      </ul>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>அரசு திட்டங்கள் / Schemes</h2>
      <ul>
        <li>சமீபத்திய வெளியீடுகள்: {quality_gate['schemes'].get('latest_count', 0)}</li>
        <li>இறுதி புதுப்பிப்பு: {escape(str(quality_gate['schemes'].get('last_updated_at', 'பதிவு இல்லை')))}</li>
        <li>வகைகள்: {escape(scheme_categories)}</li>
      </ul>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>AI validation / செயற்கை நுண்ணறிவு மதிப்பீடு</h2>
      <ul>
        <li>AI status: {escape(str(ai_status))}</li>
        <li>Readability / படித்தல்: {escape(str(readability_state))}</li>
        <li>Summary quality score: {ai_validation.get('summary_quality_score', 0)}</li>
        <li>Manual review required: {escape(str(ai_validation.get('manual_review_required', False)))}</li>
        <li>Source compliance: weather={escape(str(weather_source_status))}, schemes={escape(str(scheme_source_status))}</li>
      </ul>
    </section>
  </div>
</body>
</html>
"""


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Login | Digital Farming</title>
  <style>
    :root {
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --danger: #b42318;
      --shadow: 0 16px 40px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; color: var(--text);
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 32px 18px 52px; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; gap: 10px; flex-wrap: wrap; }
    .nav a { text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }
    .auth-shell { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 28px; margin-top: 28px; }
    .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: 28px; box-shadow: var(--shadow); }
    .eyebrow { display: inline-block; padding: 6px 10px; border-radius: 999px; background: #ebf9ef; color: var(--primary); font-weight: 700; font-size: 12px; }
    h1 { font-size: clamp(2rem, 4vw, 3rem); margin: 16px 0 10px; }
    p { color: var(--muted); line-height: 1.8; }
    form { display: grid; gap: 18px; }
    label { display: grid; gap: 8px; font-weight: 600; }
    input { width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line); background: #fbfdfb; font: inherit; }
    button {
      border: none; border-radius: 12px; padding: 14px 18px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; font-weight: 700; cursor: pointer;
    }
    .cta-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
    .secondary-link { color: var(--text); display: inline-flex; align-items: center; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; text-decoration: none; font-weight: 600; }
    .error { color: var(--danger); font-size: 0.92rem; display: none; }
    .feature-list { list-style: none; padding: 0; margin: 18px 0 0; display: grid; gap: 12px; }
    .feature-list li { background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; }
    @media (max-width: 760px) { .auth-shell { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>Digital Farming Support Center</span>
      </div>
      <nav class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/government-schemes">Schemes</a>
        <a href="/register">Register</a>
      </nav>
    </header>

    <div class="auth-shell">
      <div class="panel">
        <span class="eyebrow">Secure access</span>
        <h1>Welcome back</h1>
        <p>Sign in to review field insights, advisory recommendations, weather risk, and government scheme updates.</p>

        <form id="login-form" method="post" action="/auth/login">
          <label>
            Username
            <input type="text" name="username" placeholder="operator1" required />
          </label>
          <label>
            Password
            <input type="password" name="password" placeholder="Enter your password" required />
          </label>
          <div class="error" id="auth-error">Invalid username or password.</div>
          <button type="submit">Login</button>
        </form>

        <div class="cta-row">
          <a class="secondary-link" href="/forgot-password">Forgot password</a>
          <a class="secondary-link" href="/register">Register new user</a>
        </div>
      </div>

      <aside class="panel">
        <span class="eyebrow">Why farmers trust this</span>
        <ul class="feature-list">
          <li>Daily crop health and irrigation recommendations</li>
          <li>Weather and risk alerts for the active season</li>
          <li>Guidance on government schemes and eligibility</li>
          <li>Secure account access for verified field operators</li>
        </ul>
      </aside>
    </div>
  </div>

  <script>
    const form = document.getElementById('login-form');
    const errorBox = document.getElementById('auth-error');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const payload = { username: formData.get('username'), password: formData.get('password') };
      try {
        const response = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Login failed');
        }
        localStorage.setItem('digital_farming_token', data.token);
        window.location.href = '/dashboard';
      } catch (error) {
        errorBox.style.display = 'block';
        errorBox.textContent = error.message || 'Invalid username or password.';
      }
    });
  </script>
</body>
</html>
"""


@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Forgot password</title>
  <style>
    :root {
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }
    .container { max-width: 820px; margin: 0 auto; padding: 36px 18px 48px; }
    .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: 28px; box-shadow: var(--shadow); }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; gap: 10px; flex-wrap: wrap; }
    .nav a { text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }
    h1 { margin: 18px 0 10px; }
    p { color: var(--muted); line-height: 1.8; }
    form { display: grid; gap: 18px; }
    label { display: grid; gap: 8px; font-weight: 600; }
    input { width: 100%; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px; font: inherit; }
    button { border: none; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 12px; padding: 14px 18px; font-weight: 700; cursor: pointer; }
    .muted-links { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
    .muted-links a { color: var(--primary); font-weight: 600; text-decoration: none; }
    @media (max-width:760px) { .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🔐</div>
        <span>Password Recovery</span>
      </div>
      <nav class="nav">
        <a href="/login">Login</a>
        <a href="/register">Register</a>
      </nav>
    </header>
    <div class="panel">
      <h1>Forgot password</h1>
      <p>Enter your registered email address to receive a secure reset link. The system validates the email and only sends the reset link if the account is registered.</p>
      <form action="/api/v1/auth/forgot-password" method="post">
        <label>
          Email address
          <input type="email" name="email" placeholder="name@farmers.org" required />
        </label>
        <button type="submit">Send reset link</button>
      </form>
      <div class="muted-links">
        <a href="/login">Back to login</a>
        <a href="/register">Create a new account</a>
      </div>
    </div>
  </div>
</body>
</html>
"""


@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Reset password</title>
  <style>
    :root {
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }
    .container { max-width: 820px; margin: 0 auto; padding: 36px 18px 48px; }
    .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: 28px; box-shadow: var(--shadow); }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; gap: 10px; flex-wrap: wrap; }
    .nav a { text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }
    h1 { margin: 18px 0 10px; }
    p { color: var(--muted); line-height: 1.8; }
    form { display: grid; gap: 18px; }
    label { display: grid; gap: 8px; font-weight: 600; }
    input { width: 100%; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px; font: inherit; }
    button { border: none; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 12px; padding: 14px 18px; font-weight: 700; cursor: pointer; }
    .muted-links { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }
    .muted-links a { color: var(--primary); font-weight: 600; text-decoration: none; }
    @media (max-width:760px) { .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🔄</div>
        <span>Reset password</span>
      </div>
      <nav class="nav">
        <a href="/login">Login</a>
        <a href="/forgot-password">Forgot password</a>
      </nav>
    </header>
    <div class="panel">
      <h1>Set a new password</h1>
      <p>Use the registered username and choose a new secure password. Passwords are hashed before storage.</p>
      <form action="/api/v1/auth/reset-password" method="post">
        <label>
          Username
          <input type="text" name="username" placeholder="operator1" required />
        </label>
        <label>
          New password
          <input type="password" name="new_password" placeholder="Choose a strong password" required />
        </label>
        <button type="submit">Update password</button>
      </form>
      <div class="muted-links">
        <a href="/login">Return to login</a>
      </div>
    </div>
  </div>
</body>
</html>
"""


@app.get("/register", response_class=HTMLResponse)
def register_page():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>விவசாயி பதிவு</title>
  <style>
    :root {
      --bg: #f4f8f2;
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
      margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text);
    }
    .container { max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 700; }
    .logo { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }
    .nav { display: flex; gap: 10px; flex-wrap: wrap; }
    .nav a { text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }
    h1 { margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }
    .lede { color: var(--muted); line-height: 1.8; max-width: 75ch; }
    .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 24px; box-shadow: var(--shadow); }
    form { display: grid; gap: 18px; }
    .row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    label { display: grid; gap: 8px; font-weight: 600; }
    input, select, textarea {
      width: 100%; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px; font: inherit; background: #fbfdfb; color: var(--text);
    }
    button {
      border: none; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 12px; padding: 14px 18px; font-weight: 700; cursor: pointer;
    }
    ul { color: var(--muted); line-height: 1.9; padding-left: 18px; }
    @media (max-width: 760px) { .row { grid-template-columns: 1fr; } .topbar { flex-direction: column; align-items: flex-start; } }
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">🌾</div>
        <span>விவசாயி பதிவு / Farmer Registration</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/profile">சுயவிபரம்</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>பதிவு படிவம் / Registration Form</h1>
    <p class="lede">உங்கள் விவசாயப் பதிவு, கிராமம், நிலம், பயிர் மற்றும் தொடர்புத் தகவல்களை உள்ளிட்டு, அடுத்தகட்ட சேவைகளை அணுகவும்.</p>

    <div class="panel">
      <form action="/api/v1/auth/register" method="post">
        <div class="row">
          <label>
            Username
            <input type="text" name="username" placeholder="farmer_01" required />
          </label>
          <label>
            Password
            <input type="password" name="password" placeholder="Minimum 8 characters" required />
          </label>
        </div>

        <div class="row">
          <label>
            Full name / விவசாயி பெயர்
            <input type="text" name="full_name" placeholder="உதாரணம்: குமரன்" />
          </label>
          <label>
            Email / மின்னஞ்சல்
            <input type="email" name="email" placeholder="name@example.com" />
          </label>
        </div>

        <div class="row">
          <label>
            Phone / கைபேசி எண்
            <input type="tel" name="phone" value="" placeholder="9876543210" />
          </label>
          <label>
            Role / பங்கு
            <select name="role">
              <option value="farmer">Farmer / விவசாயி</option>
              <option value="operator">Operator / ஆபரேட்டர்</option>
              <option value="admin">Admin / நிர்வாகி</option>
            </select>
          </label>
        </div>

        <label>
          Village / கிராமம்
          <input type="text" name="village" placeholder="கல்லக்குறிச்சி" />
        </label>

        <button type="submit">Create account / பதிவு செய்யவும்</button>
      </form>
    </div>

    <div class="panel" style="margin-top: 20px;">
      <h2>அடுத்த படிகள் / Next steps</h2>
      <ul>
        <li>பயிர் விவரம் மற்றும் மண் நிலை பதிவு செய்யப்படும்.</li>
        <li>சேவைகளின் அடிப்படையில் இலக்கு பரிந்துரைகள் வழங்கப்படும்.</li>
        <li>வானிலை, சந்தை மற்றும் அரசு திட்ட தகவல்கள் உங்களுக்காகத் தயாராகும்.</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""


@app.get("/profile", response_class=HTMLResponse)
def profile_page(username: str = "operator1"):
    try:
        profile = get_profile(username)
    except ValueError:
        profile = {"username": username, "role": "operator"}

    role_label = {
        "farmer": "விவசாயி",
        "operator": "ஆபரேட்டர்",
        "admin": "நிர்வாகி",
    }.get(profile.get("role", "operator"), "ஆபரேட்டர்")

    return f"""
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>சுயவிபரம்</title>
  <style>
    :root {{
      --bg: #f4f8f2;
      --panel: #ffffff;
      --primary: #2d7d46;
      --secondary: #4aa6d6;
      --text: #17301d;
      --muted: #567163;
      --line: #dfe9df;
      --shadow: 0 12px 30px rgba(23, 48, 29, 0.08);
      --warning: #d97706;
      --success: #2d7d46;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Nirmala UI', 'Segoe UI', Arial, sans-serif; background: linear-gradient(180deg, #eefaf0 0%, #f7f5ef 100%); color: var(--text); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 28px 18px 48px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; }}
    .logo {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .nav a {{ text-decoration: none; color: var(--text); background: #f4f8f4; border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font-weight: 600; }}
    h1 {{ margin: 28px 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .lede {{ color: var(--muted); line-height: 1.8; max-width: 75ch; }}
    .hero {{ display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .stat {{ background: linear-gradient(180deg, #f7faf6 0%, #edf9f2 100%); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .stat span {{ color: var(--muted); }}
    .stat strong {{ display: block; margin-top: 8px; font-size: 1.8rem; }}
    .meta {{ display: grid; gap: 12px; margin-top: 14px; }}
    .meta-item {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; background: #fbfdfb; }}
    .muted {{ color: var(--muted); }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }}
    @media (max-width: 760px) {{ .hero, .stats {{ grid-template-columns: 1fr; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header class="topbar">
      <div class="brand">
        <div class="logo">👤</div>
        <span>சுயவிபரம் / Profile</span>
      </div>
      <nav class="nav">
        <a href="/">முகப்பு</a>
        <a href="/dashboard">டாஷ்போர்டு</a>
        <a href="/weather">வானிலை</a>
        <a href="/soil-health">மண் சோதனை</a>
        <a href="/disease-detection">நோய் கண்டறிதல்</a>
        <a href="/government-schemes">அரசு திட்டங்கள்</a>
        <a href="/market-intelligence">சந்தை</a>
        <a href="/sustainability">நிலைத்தன்மை</a>
        <a href="/traceability">கண்காணிப்பு</a>
        <a href="/register">பதிவு</a>
        <a href="/admin/overview">Admin</a>
      </nav>
    </header>

    <h1>பயனர் சுயவிபரம்</h1>
    <p class="lede">விவசாயி மற்றும் நில மேலாண்மை தகவல்களை ஒரே இடத்தில் ஆய்வு செய்து, அடுத்த நடவடிக்கையை திட்டமிட உதவுகிறது.</p>

    <section class="hero">
      <div class="panel">
        <h2>சுருக்கம் / Summary</h2>
        <div class="stats">
          <div class="stat"><span>பயனர்</span><strong>{escape(str(profile.get('username', username)))}</strong></div>
          <div class="stat"><span>பங்கு</span><strong>{escape(role_label)}</strong></div>
          <div class="stat"><span>நிலம்</span><strong>3.5 ha</strong></div>
        </div>
        <div class="meta">
          <div class="meta-item"><strong>கிராமம்:</strong> <span class="muted">கல்லக்குறிச்சி</span></div>
          <div class="meta-item"><strong>முக்கிய பயிர்:</strong> <span class="muted">நெல்</span></div>
          <div class="meta-item"><strong>மண் நிலை:</strong> <span class="muted">சக்திவாய்ந்த, pH 6.8</span></div>
        </div>
      </div>

      <div class="panel">
        <h2>நிலை / Status</h2>
        <ul>
          <li>சமீபத்திய மண் ஆய்வு: வெள்ளிக்கிழமை, 24 மணி நேரத்திற்கு முன்பு.</li>
          <li>பாசன அட்டவணை: 3 முறை பரிந்துரைக்கப்பட்டது.</li>
          <li>வானிலை எச்சரிக்கை: மிதமான மழை முன்னறிவிப்பு.</li>
          <li>அரசு திட்டங்கள்: 2 புதிய உதவிகள் பொருந்துகின்றன.</li>
        </ul>
      </div>
    </section>

    <section class="panel" style="margin-top: 20px;">
      <h2>அடுத்த படிகள் / Next Steps</h2>
      <ul>
        <li>மண் தரவை மறுபரிசீலனை செய்து, உர திட்டத்தை புதுப்பிக்கவும்.</li>
        <li>வானிலை மற்றும் சந்தை முன்னறிவிப்புகளை தொடர்ந்து கண்காணிக்கவும்.</li>
        <li>அரசு உதவித் திட்டங்கள் மற்றும் நீர் மேலாண்மை நடவடிக்கைகளை ஒருங்கிணைக்கவும்.</li>
      </ul>
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
