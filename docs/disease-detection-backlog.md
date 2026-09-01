# Disease Detection Module — Sprint and User Story Backlog

## 1. Product outcome

The Disease Detection module should let farmers and operators upload crop images, identify likely disease or nutrient issues, and receive fast Tamil guidance for treatment and prevention.

---

## 2. Epic structure

### Epic 1 — Image intake and scan workflow

#### Story DD-01: As a farmer, I want to upload a crop image so that I can diagnose crop damage quickly.

- Acceptance criteria:
  - user can choose an image from gallery or camera
  - upload completes successfully
  - loading state is visible while processing
- Repo status: Planned

#### Story DD-02: As a field officer, I want a simple scan screen so that I can support multiple farmers without complex steps.

- Acceptance criteria:
  - scan page is clear and mobile-optimized
  - camera and upload actions are easy to discover
  - error states are understandable
- Repo status: Planned

### Epic 2 — AI diagnosis and confidence handling

#### Story DD-03: As a farmer, I want the system to detect the likely issue so that I can take action early.

- Acceptance criteria:
  - AI returns a likely disease, pest, or nutrient issue
  - confidence score is displayed
  - primary detection is shown in Tamil
- Repo status: Planned

#### Story DD-04: As an operator, I want low-confidence results to be treated carefully so that uncertain diagnoses do not mislead farmers.

- Acceptance criteria:
  - low-confidence results show warning messaging
  - system suggests human review or re-upload
  - diagnosis is marked carefully in logs
- Repo status: Planned

### Epic 3 — Treatment and prevention guidance

#### Story DD-05: As a farmer, I want treatment steps in Tamil so that I can act without technical language barriers.

- Acceptance criteria:
  - treatment advice is written in simple Tamil
  - steps are easy to follow in field conditions
  - action list is displayed alongside diagnosis
- Repo status: Planned

#### Story DD-06: As a farmer, I want prevention tips so that I can reduce future risk to the crop.

- Acceptance criteria:
  - prevention guidance is displayed after diagnosis
  - actions are practical and crop-relevant
  - tips are easy to understand on mobile
- Repo status: Planned

### Epic 4 — History and review

#### Story DD-07: As an operator, I want a scan history so that I can review prior diagnoses and treatment actions.

- Acceptance criteria:
  - previous scans are stored with date and diagnosis
  - history list shows the disease and time of scan
  - records remain accessible for follow-up
- Repo status: Planned

### Epic 5 — Product, UX, and accessibility

#### Story DD-08: As a farmer, I want a simple Tamil UI so that I can use the page without reading technical instructions.

- Acceptance criteria:
  - UI uses simple Tamil words and readable layout
  - icons and visual hierarchy aid understanding
  - result page is easy to scan
- Repo status: Planned

#### Story DD-09: As a user, I want optional voice guidance so that I can get instructions in spoken Tamil.

- Acceptance criteria:
  - voice readout can be enabled optionally
  - feature does not block the main diagnosis flow
- Repo status: Planned

---

## 3. Sprint plan

### Sprint 1 — Scan workflow foundation

- DD-01
- DD-02

### Sprint 2 — Diagnosis and confidence logic

- DD-03
- DD-04

### Sprint 3 — Treatment and prevention outputs

- DD-05
- DD-06

### Sprint 4 — History and UX polish

- DD-07
- DD-08
- DD-09

---

## 4. Current repo status mapping

| Area                      | Status  | Notes                                              |
| ------------------------- | ------- | -------------------------------------------------- |
| Disease scan UI           | Planned | Not yet implemented in repo                        |
| AI diagnosis pipeline     | Planned | Requires model selection and inference integration |
| Treatment output in Tamil | Planned | Needs content and translation rules                |
| Prevention guidance       | Planned | Needs agronomic rule set                           |
| History storage           | Planned | DiseaseScanHistory schema not yet added            |
| Mobile-first Tamil UX     | Planned | Not yet implemented                                |
| Confidence warning flow   | Planned | No diagnostic confidence handling yet              |
| Optional voice reading    | Planned | Not yet implemented                                |

---

## 5. Recommended next sprint focus

1. Build the scan page and image upload flow
2. Add scan history database model
3. Integrate a lightweight disease model or placeholder inference service
4. Return Tamil diagnosis and guidance
5. Add low-confidence handling and UX cues

This keeps the feature aligned with the product outcome while remaining practical for MVP delivery.
