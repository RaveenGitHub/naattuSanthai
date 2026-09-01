# Disease Detection Module — Implementation Plan

## 1. Goal

Build a simple, reliable disease detection workflow that allows farmers to upload a crop image, receive AI-based diagnosis, and follow clear Tamil treatment and prevention guidance.

---

## 2. Delivery approach

This plan is structured into five phases:

- Image intake and scan screen
- AI inference and confidence logic
- Tamil diagnosis output and guidance
- Storage and history
- UX polish and rollout

---

## 3. Phase-by-phase implementation

## Phase 1 — Image intake and scan UI

### Objective

Create the first farmer-facing workflow: upload image, capture photo, and show loading state.

### Tasks

- create scan page with upload and camera actions
- add loading animation and status messaging
- validate file types and size limits
- prepare the result card shell

### Deliverables

- scan page UI
- upload pipeline hooks
- result shell

### Acceptance criteria

- user can upload or capture an image
- the app shows processing feedback
- the UI is mobile-friendly and clean in Tamil

---

## Phase 2 — AI inference and diagnosis engine

### Objective

Bring in a disease detection model and produce a likely diagnosis result.

### Tasks

- select model stack such as ONNX or TensorFlow Lite
- implement inference service for crop images
- map prediction labels to English disease names
- return confidence score
- define fallback for low-confidence predictions

### Deliverables

- inference service
- confidence logic
- result mapping layer

### Acceptance criteria

- model returns disease category or likely issue
- confidence score is included
- low-confidence results are flagged clearly

---

## Phase 3 — Tamil guidance layer

### Objective

Turn diagnosis output into farmer-friendly Tamil treatment and prevention content.

### Tasks

- add Tamil translation mapping for disease labels
- define treatment guidance rules by disease type
- define prevention and agronomic tips
- create simple, readable formatting for mobile screens

### Deliverables

- translated diagnosis text
- treatment steps
- prevention section
- Tamil-safe UI templates

### Acceptance criteria

- result page contains disease name, treatment, and prevention in Tamil
- recommendations are simple and actionable
- output remains readable on mobile

---

## Phase 4 — History and data storage

### Objective

Track all scans for review and follow-up.

### Tasks

- add DiseaseScanHistory table
- save image URL, diagnosis, treatment, prevention, and timestamp
- expose history endpoint and list screen
- ensure scan records are attachable to user or operator context

### Deliverables

- schema and storage layer
- scan history endpoint
- history UI or API listing

### Acceptance criteria

- each scan is saved with diagnosis and timestamp
- historical scan records are browsable
- prior issues can be reviewed later

---

## Phase 5 — UX polish and rollout

### Objective

Make the experience ready for pilots and field validation.

### Tasks

- improve Tamil wording and accessibility
- add optional voice readout support
- define QA for model confidence and treatment accuracy
- run farmer review pilot

### Deliverables

- polished result page
- optional voice support
- QA and feedback checklist

### Acceptance criteria

- user can interpret diagnosis without external explanation
- voice reading is optional and non-blocking
- pilot review confirms clarity and usefulness

---

## 4. Technical architecture

### Layers

1. Frontend page for scan and result display
2. API layer for upload and diagnosis handling
3. Inference service layer
4. Store and history layer
5. Manual review and confidence handling layer

### Recommended stack for MVP

- Python + FastAPI
- TensorFlow Lite or ONNX for on-device or lightweight inference
- SQLite for MVP history storage
- HTML/Tailwind or simple frontend templates for Tamil UI

---

## 5. Risks and mitigation

### Risk: low-quality images reduce classification accuracy

Mitigation:

- allow re-capture and image quality hints
- show caution when confidence is low

### Risk: wrong disease label for uncommon crop issues

Mitigation:

- keep diagnosis as likely issue, not definitive certainty
- include human review fallback

### Risk: treatment advice is too technical

Mitigation:

- simplify Tamil wording and provide practical steps
- keep treatment and prevention in short bullet form

---

## 6. Recommended next steps

1. Create the scan page and camera upload workflow
2. Add the database model for scan history
3. Integrate a lightweight inference model
4. Map model output to Tamil diagnosis and guidance
5. add confidence and manual-review warnings
6. pilot with a few farmers and field officers

---

## 7. Final recommendation

This feature should be implemented as a practical field diagnosis tool rather than a generic AI showcase. For farmers, clarity, confidence handling, and Tamil guidance are more important than model sophistication alone.
