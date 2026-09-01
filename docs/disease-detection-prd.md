# Disease Detection Page — Product Requirements Document (PRD)

## 1. Overview

This module enables farmers and field operators to upload crop images such as leaves, stems, fruits, or affected plant parts and receive AI-assisted diagnosis of likely diseases, pest attacks, and nutrient deficiencies. The output is translated into simple Tamil and paired with treatment and prevention guidance that is actionable for field use.

---

## 2. Objective

பயிர் இலை/தாவர படங்களை AI மூலம் ஸ்கேன் செய்து நோய், பூச்சி தாக்குதல், ஊட்டச்சத்து குறைபாடு ஆகியவற்றை கண்டறிந்து, தமிழில் உடனடி தீர்வு வழங்குதல்.

### Desired outcome

- Farmers can identify crop issues earlier before major damage occurs
- Field officers can support farmers with faster diagnosis
- Local-language guidance increases adoption and confidence
- Diagnostic results become part of an accessible farmer support workflow

---

## 3. Target Users

### Primary users

- Small and marginal farmers
- Field officers and extension workers
- Agronomists and crop specialists
- Cooperative and farm support staff

### User needs

- Upload a plant image quickly
- Understand the detected issue in clear Tamil
- View treatment and prevention steps in the same screen
- Know the confidence level of the diagnosis

---

## 4. Problem Statement

Farmers often detect crop issues too late, after visible damage has already spread. Without timely diagnosis, they may use ineffective inputs, delay action, or over-treat crops. A low-friction image-based diagnosis tool can help them identify likely disease and pest issues earlier and take action faster.

---

## 5. Goals and Success Metrics

### Goals

1. Support early diagnosis of common crop issues
2. Deliver Tamil-first, farmer-understandable guidance
3. Reduce crop loss through faster intervention
4. Provide transparent confidence and explainability
5. Keep the workflow simple and mobile-friendly

### Success metrics

- Diagnosis is delivered within seconds after upload
- Tamil guidance is readable and actionable
- Confidence score is displayed and understood
- Farmers can follow treatment and prevention steps without expert help
- Diagnostic history is available for repeated review

---

## 6. Functional Requirements

### 6.1 Image intake

- Allow image upload from gallery or camera
- Accept common crop images such as leaves, stems, fruits, and plant parts
- Support quick upload on mobile devices

### 6.2 AI diagnosis

- Run AI inference on uploaded image data
- Detect:
  - fungal diseases
  - bacterial diseases
  - viral diseases
  - pest infestations
  - nutrient deficiencies
- Return a confidence score for each result

### 6.3 Farmer guidance

- Translate diagnosis into Tamil
- Show treatment steps in Tamil
- Show preventive measures in Tamil
- Recommend next actions in simple farmer terminology

### 6.4 Scan history

- Save each diagnosis record
- Keep disease, treatment, prevention, and scan date
- Support review of previous scans for trend awareness

---

## 7. Non-Functional Requirements

- Mobile-first image upload experience
- Fast response on low-bandwidth devices
- Clear Tamil text and icons
- Low-latency AI inference for field use
- Reliable handling of low-quality images
- Storage of scan history with audit-friendly metadata

---

## 8. Trusted Data Sources

### Model training and validation sources

- TNAU Crop Disease Database
- ICAR (Indian Council of Agricultural Research)
- IARI (Indian Agricultural Research Institute)
- FAO Plant Health datasets
- Kaggle PlantVillage dataset
- Tamil Nadu Horticulture Department disease manuals

### Source rules

- Use datasets relevant to Indian crops and field conditions
- Ensure labels align with local agronomic language
- Validate the model against farmer-common diseases and local crop varieties

---

## 9. AI Processing Requirements

The AI system must support:

- image upload and preprocessing
- plant disease classification
- pest and nutrient deficiency detection
- confidence scoring
- Tamil translation of diagnosis
- Tamil treatment instructions
- Tamil prevention guidance

### Supported classes

- fungal disease
- bacterial disease
- viral disease
- pest infestation
- nutrient deficiency

### AI behavior

- Return one primary prediction as well as confidence indicator
- If confidence is low, show a cautious message and encourage expert review
- Store raw image metadata and diagnosis result for traceability

---

## 10. Data Storage Requirements

### DiseaseScanHistory

Fields:

- id
- image_url
- disease_detected_en
- disease_detected_ta
- treatment_ta
- prevention_ta
- scan_date

### Additional recommended metadata

- crop_name
- confidence_score
- model_version
- review_status
- user_role

---

## 11. UI Requirements

### Scan Page

- “படத்தை பதிவேற்றவும்”
- “கேமரா திறக்கவும்”
- loading animation
- Tamil result card after diagnosis

### Result Page

- disease name in Tamil
- treatment steps in Tamil
- prevention tips in Tamil
- confidence score
- optional “PDF சேமிக்க” support

### Tamil display rules

- use simple Tamil
- use icons for disease categories
- optional voice reading for diagnosis and instructions
- concise, step-by-step advice
- high readability on mobile devices

---

## 12. API Requirements

### Proposed endpoints

- POST /api/disease/scan
- GET /api/disease/history
- GET /api/disease/{id}

### Response contract

- diagnosis name
- confidence score
- treatment steps
- prevention steps
- image reference
- timestamp

---

## 13. Scope

### In scope

- upload and diagnosis of plant images
- AI detection for disease, pest, and nutrient issue categories
- Tamil treatment and prevention guidance
- scan history tracking
- mobile-first farmer UI

### Out of scope

- live remote disease advisory from a human expert only
- full supply-chain integration
- drone or satellite imagery integration in MVP
- payment or insurance settlement flows

---

## 14. Acceptance Criteria

1. A user can upload or capture a crop image
2. The system returns a disease or issue classification with confidence
3. Results are shown in clear Tamil
4. Treatment and prevention guidance are displayed
5. Scans are stored in history for later review
6. Low-confidence results are flagged for human verification
7. UI is simple and mobile-friendly for farmers

---

## 15. Risks and Mitigation

### Risk 1: wrong classification from low-quality image

Mitigation:

- show confidence score and caution message
- allow re-upload and manual expert review

### Risk 2: model bias or poor local crop coverage

Mitigation:

- use local datasets and validate against Tamil Nadu crop conditions
- review common false positives

### Risk 3: farmer confusion with complex treatment content

Mitigation:

- output simple Tamil steps and prevention tips
- use icons and step-by-step structure

---

## 16. Recommendation

The disease detection feature should be designed as a trusted field-support tool rather than a pure AI demo. Farmers need quick, clear, and actionable diagnostic guidance in Tamil, and the system should visibly handle uncertainty with confidence scores and human fallback guidance.
