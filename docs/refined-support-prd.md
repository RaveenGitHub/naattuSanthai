# **📘 Refined Support PRD (Agriscience‑Grade Version)**

# **தமிழ்‑முதல் வேளாண்மை பயன்பாடு – மேம்பட்ட ஆதரவு PRD**

---

## **1. Feature Overview / அம்சத்தின் சுருக்கம்**

இந்த PRD, பயன்பாட்டின் **அணுகல் கட்டுப்பாடு**, **சுயவிவர மேலாண்மை**, **அமர்வு பாதுகாப்பு**, மற்றும் **தானியங்கி தகவல் வடிகட்டல் (Auto‑Filtering)** ஆகியவற்றை தொழில்துறை தரநிலைக்கு ஏற்ப வரையறுக்கிறது.  
இது விவசாயிகளின் புலத் தேவைகள், பிராந்திய வேறுபாடுகள், மற்றும் பயிர்‑சார்ந்த தகவல் துல்லியத்தை உறுதிப்படுத்தும் வகையில் வடிவமைக்கப்பட்டுள்ளது.

---

## **2. Access Control Requirements / அணுகல் கட்டுப்பாட்டு தேவைகள்**

### **2.1 Admin Page Access (Admin பக்க அணுகல்)**

- Admin Page என்பது **அங்கீகரிக்கப்பட்ட Admin பயனருக்கு மட்டும்** கிடைக்க வேண்டும்.
- Non‑admin users (விவசாயி, தன்னார்வலர், பொதுப் பயனர்) இந்தப் பக்கத்தை அணுக முடியாது.
- Direct URL access முயற்சிகள் → **அணுகல் மறுக்கப்பட்டு Home/Login பக்கத்துக்கு மாற்றப்பட வேண்டும்**.
- Admin Page‑இல் RBAC (Role‑Based Access Control) கட்டாயம் செயல்படுத்தப்பட வேண்டும்.

### **2.2 Profile Page Access (சுயவிவர பக்க அணுகல்)**

- Profile Page என்பது **Login செய்த பயனருக்கு மட்டும்** கிடைக்கும்.
- பயனர் **தன் சுயவிவரத்தை மட்டும்** பார்க்கவும் திருத்தவும் முடியும்.
- Direct URL மூலம் மற்ற பயனரின் profile‑ஐ திறக்க முயன்றால் → **அணுகல் தடுக்கப்பட வேண்டும்**.
- App close / session expiry ஆகியவற்றின் போது profile page‑க்கு direct access **முழுமையாக முடக்கப்பட வேண்டும்**.

### **2.3 Public Pages Access (பொது பக்கங்கள்)**

- Home, Dashboard, Services, Advisory, Weather‑Market போன்ற பக்கங்கள்  
  → **எப்போதும் அனைத்து பயனர்களுக்கும்** காணக்கூடியதாக இருக்க வேண்டும்.
- Login செய்த பயனருக்கு மட்டும் **தனிப்பட்ட (personalized) தகவல்** auto‑filtered ஆக காட்டப்படும்.
- Guest users → **பொது (default) தகவல்** காண்பிக்கப்படும்.

---

## **3. Session & Security Requirements / அமர்வு & பாதுகாப்பு**

- App close செய்தால் session token **உடனடியாக செல்லாது**.
- Session timeout (future enhancement) → inactivity‑based expiry.
- Restricted pages must validate active session token.
- Unauthorized access → **redirect to Home/Login**.
- Sensitive data must never be cached without encryption.

---

## **4. Auto‑Filter Logic / தானியங்கி தகவல் வடிகட்டல்**

Login செய்த பயனரின் profile தகவல்களை அடிப்படையாகக் கொண்டு,  
அவர்கள் பார்க்கும் அனைத்து பக்கங்களிலும் தகவல் **தானாக வடிகட்டப்பட்டு** காட்டப்பட வேண்டும்.

### **4.1 Auto‑Filter Inputs (வடிகட்டலுக்கான உள்ளீடுகள்)**

பின்வரும் profile attributes auto‑filter‑க்கு பயன்படுத்தப்படும்:

- **Village / கிராமம்**
- **Region / மண்டலம்**
- **Area / பகுதி**
- **Primary Crop / முதன்மை பயிர்**
- **Land Size / நில அளவு**
- **Water Source / நீர் ஆதாரம்**
- **Farming Method (Manual / Machine)**
- **Secondary Crops Interested / கூடுதல் பயிர் ஆர்வம்**

### **4.2 Auto‑Filter Behavior (வடிகட்டல் செயல்பாடு)**

- Profile‑இல் உள்ள attribute‑களுடன் பொருந்தும் தரவு → **தனிப்பட்ட (personalized) தகவல்**.
- Profile‑இல் attribute இல்லாதால் → **பொது (default) தகவல்**.
- Advisory, Weather, Market, Soil, Disease Detection போன்ற பக்கங்களில்  
  → பயனரின் profile‑இன் அடிப்படையில் **துல்லியமான, புல‑சார்ந்த தகவல்** காட்டப்படும்.

---

## **5. Profile Data Requirements / சுயவிவரத்தில் சேகரிக்க வேண்டிய விவரங்கள்**

Profile Page (Registration + Edit) பின்வரும் விவரங்களை கட்டாயம் சேகரிக்க வேண்டும்:

### **5.1 Mandatory Fields (கட்டாய புலங்கள்)**

- பயனர் பெயர்
- மொபைல் எண் (OTP)
- கிராமம்
- மண்டலம்
- பகுதி
- முதன்மை பயிர்
- நில அளவு
- நீர் ஆதாரம்

### **5.2 Optional but Recommended Fields (விருப்பமான ஆனால் முக்கிய புலங்கள்)**

- சாகுபடி முறை (Manual / Machine)
- கூடுதல் பயிர் ஆர்வம்
- கண்காணிக்க விரும்பும் பயிர்கள் (Select box)
- விவசாய கருவிகள் கிடைப்பது
- பாசன முறை (drip / canal / borewell etc.)

### **5.3 Profile Editing Rules (திருத்த விதிகள்)**

- Login செய்த பயனர் தன் profile‑ஐ திருத்தலாம்.
- Profile update செய்தவுடன் auto‑filter logic **உடனடியாக refresh** ஆக வேண்டும்.
- Admin பயனர் மற்ற profile‑களை பார்க்கலாம் (future enhancement).

---

## **6. User Experience Flow / பயனர் அனுபவ ஓட்டம்**

### **6.1 Logged‑in User Flow**

1. Login
2. Dashboard → auto‑filtered data
3. Services → personalized view
4. Advisory → crop‑specific guidance
5. Weather → region‑specific forecast
6. Market → crop‑specific price
7. Soil → location‑specific soil info
8. Profile → edit/update
9. Logout → session end

### **6.2 Guest User Flow**

1. Home
2. Dashboard → general data
3. Services → general list
4. Advisory → general guidance
5. Weather → general forecast
6. Market → general price
7. Profile → not accessible
8. Admin → not accessible

---

## **7. Acceptance Criteria / ஏற்றுக்கொள்ளும் அளவுகோல்கள்**

- Admin Page → Admin பயனருக்கு மட்டும்.
- Profile Page → Login செய்த பயனருக்கு மட்டும்.
- Direct URL access → restricted pages must redirect.
- Auto‑filter → profile data அடிப்படையில் அனைத்து பக்கங்களிலும் செயல்பட வேண்டும்.
- Profile Page → அனைத்து தேவையான விவரங்களையும் சேகரிக்க வேண்டும்.
- App close → session end.
- Guest user → அனைத்து பொதுப் பக்கங்களையும் பார்க்க முடியும்.
- Personalized data → must be accurate, region‑specific, crop‑specific, and context‑relevant.

---

## **8. Final Summary / இறுதி சுருக்கம்**

இந்த மேம்பட்ட PRD, Tamil‑first agriculture app‑இல் **அணுகல் கட்டுப்பாடு**, **சுயவிவர மேலாண்மை**, **தானியங்கி தகவல் வடிகட்டல்**, மற்றும் **பாதுகாப்பு** ஆகியவற்றை  
**அறிவியல்‑அடிப்படையிலான, புல‑சார்ந்த, தொழில்துறை தரநிலைக்கு** ஏற்ப வரையறுக்கிறது.

இதன் மூலம்:

- பயனருக்கு **துல்லியமான, தனிப்பட்ட, புல‑சார்ந்த தகவல்** கிடைக்கும்
- பயன்பாட்டின் **ஏற்றுக்கொள்ளல், செயல்திறன், நம்பகத்தன்மை** உயர்கிறது
- UI/UX ஒரு **செயல்பாட்டு சொத்து** (operational asset) ஆக மாறுகிறது
