### **📘 Backlog Implementation Items (Agriscience‑Grade Version)**

# **தமிழ்‑முதல் வேளாண்மை பயன்பாடு – செயல்படுத்தல் பின்னணி பட்டியல்**

---

# **EPIC 1 — Access Control Framework (Admin + Profile)**

### **User Story 1.1 — Admin Page Restriction**

**Description:**  
Admin page must be accessible only to authenticated admin users.

**Tasks:**

- Implement RBAC roles: `admin`, `farmer`, `volunteer`, `guest`.
- Add server‑side role validation for admin routes.
- Add client‑side guard for admin navigation.
- Add redirect logic for unauthorized access.
- Add audit logs for admin page access attempts.

**Acceptance Criteria:**

- Non‑admin users cannot access admin page.
- Direct URL access redirects to Home/Login.
- Admin page loads only with valid admin token.

---

### **User Story 1.2 — Profile Page Restriction**

**Description:**  
Profile page must be accessible only to logged‑in users and only for their own profile.

**Tasks:**

- Implement session token validation for profile route.
- Add user‑ID matching logic (user can view only their own profile).
- Add redirect logic for unauthorized profile access.
- Add session expiry handling for profile page.

**Acceptance Criteria:**

- Only logged‑in users can access profile page.
- User cannot view or edit another user’s profile.
- Direct URL access without session → redirect to Login.

---

# **EPIC 2 — Session Management & Security**

### **User Story 2.1 — Session End on App Close**

**Tasks:**

- Implement session token invalidation on app close.
- Add secure local storage cleanup.
- Add fallback redirect for expired sessions.

**Acceptance Criteria:**

- Closing the app ends the session.
- Profile/Admin pages cannot be accessed after session end.

---

### **User Story 2.2 — Restricted Page Protection**

**Tasks:**

- Add middleware to validate session token for restricted pages.
- Add unauthorized access handler.
- Add redirect to safe page.

**Acceptance Criteria:**

- Restricted pages require active session.
- Unauthorized access always redirects safely.

---

# **EPIC 3 — Profile Data Collection & Editing**

### **User Story 3.1 — Registration Profile Data Capture**

**Description:**  
Profile page must collect all agronomy‑relevant data during registration.

**Tasks:**

- Add mandatory fields:
  - Name, Mobile, Village, Region, Area
  - Primary Crop, Land Size, Water Source
- Add optional fields:
  - Farming Method, Secondary Crops, Tools, Irrigation Type
- Add select boxes for crop interest tracking.
- Add validation rules for all fields.

**Acceptance Criteria:**

- All mandatory fields must be filled before registration completes.
- Optional fields improve personalization but are not blocking.
- Data stored in backend profile model.

---

### **User Story 3.2 — Profile Editing After Login**

**Tasks:**

- Add profile edit UI.
- Add backend update API.
- Add auto‑filter refresh trigger after profile update.

**Acceptance Criteria:**

- User can edit all profile fields.
- Auto‑filter logic updates immediately after profile change.

---

# **EPIC 4 — Auto‑Filter Logic Implementation**

### **User Story 4.1 — Auto‑Filter Engine**

**Description:**  
All pages must show personalized information based on profile attributes.

**Tasks:**

- Build auto‑filter engine using profile attributes:
  - Village, Region, Area
  - Primary Crop
  - Land Size
  - Water Source
  - Farming Method
  - Secondary Crops
- Add fallback logic for missing attributes.
- Add filter integration for:
  - Dashboard
  - Advisory
  - Weather
  - Market
  - Soil
  - Disease Detection

**Acceptance Criteria:**

- Personalized data shown for logged‑in users.
- Default data shown for guest users.
- Filtering must be accurate and consistent across all pages.

---

### **User Story 4.2 — Page‑Specific Filter Integration**

**Tasks:**

- Dashboard → region + crop filters
- Advisory → crop + land size filters
- Weather → region filter
- Market → crop filter
- Soil → village/area filter
- Disease Detection → crop filter for recommendations

**Acceptance Criteria:**

- Each page applies relevant filters.
- No page shows incorrect or mismatched data.

---

# **EPIC 5 — Public Page Behavior**

### **User Story 5.1 — Guest User Experience**

**Tasks:**

- Ensure all public pages load without login.
- Show general (non‑filtered) data.
- Add CTA to encourage login for personalized insights.

**Acceptance Criteria:**

- Guest users can browse all public pages.
- No personalized data shown without login.

---

# **EPIC 6 — Error Handling & Redirect Logic**

### **User Story 6.1 — Unauthorized Access Handling**

**Tasks:**

- Add global unauthorized handler.
- Add redirect rules for restricted pages.
- Add user‑friendly error messages.

**Acceptance Criteria:**

- Unauthorized access never breaks the app.
- User always redirected safely.

---

# **EPIC 7 — Backend Enhancements**

### **User Story 7.1 — Profile Model Expansion**

**Tasks:**

- Add all agronomy fields to backend model.
- Add validation and sanitization.
- Add multi‑language support (Tamil + English).

**Acceptance Criteria:**

- Backend supports all required profile attributes.
- Data stored securely and consistently.

---

### **User Story 7.2 — Auto‑Filter API Layer**

**Tasks:**

- Add API endpoints for filtered data.
- Add caching for repeated queries.
- Add fallback for missing profile attributes.

**Acceptance Criteria:**

- API returns correct filtered data.
- API performance meets required benchmarks.

---

# **EPIC 8 — QA, Testing & Validation**

### **User Story 8.1 — Functional Testing**

**Tasks:**

- Test access control.
- Test profile editing.
- Test auto‑filter logic.
- Test session expiry.

### **User Story 8.2 — Field Validation (Agronomy Accuracy)**

**Tasks:**

- Validate crop‑specific filters with agronomy experts.
- Validate region‑specific weather/market mapping.
- Validate soil data mapping.

**Acceptance Criteria:**

- All personalized outputs scientifically accurate.
- Field experts approve data behavior.

---

# **EPIC 9 — Deployment & Monitoring**

### **User Story 9.1 — Logging & Monitoring**

**Tasks:**

- Add logs for access control events.
- Add logs for profile updates.
- Add monitoring for auto‑filter performance.

**Acceptance Criteria:**

- System logs all critical events.
- Monitoring dashboards available for admin.

---

# **Final Summary**

This backlog ensures:

- **Secure access control**
- **Accurate profile‑driven personalization**
- **Agronomy‑validated filtering**
- **Consistent UX for all user types**
- **Robust session and redirect handling**

This is the exact structure used in **enterprise agritech platforms**, ensuring your Tamil‑first agriculture app is production‑ready, scalable, and scientifically reliable.
