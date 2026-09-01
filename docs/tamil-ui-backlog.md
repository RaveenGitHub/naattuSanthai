# தமிழ் பயனர் இடைமுகம் மற்றும் செயல்படுத்தல் பின்னணி

## 1. நோக்கம்

இந்த பயன்பாடு தமிழ்நாடு விவசாயிகளின் நிஜ வாழ்க்கை தேவைகளுக்கு ஏற்ப வடிவமைக்கப்பட்டுள்ளது. பயனர் இடைமுகம் எளிமையான தமிழ் மொழியில், பெரிய எழுத்துரு, தெளிவான வழிசெலுத்தல் மற்றும் புல சூழலுக்கு ஏற்ற காட்சி முறையில் இருக்க வேண்டும்.

இது பின்வரும் மதிப்புகளை கையாள வேண்டும்:

- விவசாயிக்கு புரிந்துகொள்ளக்கூடிய தமிழ்
- சிறிய ஸ்மார்ட்போன் திரைக்கு ஏற்ற மேம்பாடு
- குறைந்த இணைய இணைப்பு சூழலில் செயல்படும் தன்மை
- உடனடி முடிவு எடுக்கும் UI
- புலம், சந்தை, வானிலை, மண், நீர் மற்றும் அரசுத் திட்டங்கள் அனைத்தும் ஒரே இடத்தில்

## 2. இலக்கு பயனர்கள்

- சிறு மற்றும் நடுத்தர விவசாயிகள்
- புல அலுவலர்கள்
- வேளாண்மை ஆலோசகர்கள்
- கிராம முன்னோடிகள் / volunteerders
- கூட்டுறவு மேலாளர்கள்
- அரசு திட்ட ஆதரவு குழுக்கள்

## 3. UX கட்டமைப்பு

### முக்கிய செயல்பாடுகள்

1. முகப்பு / அறிமுகம்
2. டாஷ்போர்டு
3. சேவைகள் பட்டியல்
4. பயிர் ஆலோசனை
5. வானிலை மற்றும் சந்தை
6. மண் பரிசோதனை
7. நோய்/பூச்சி கண்டறிதல்
8. அரசு திட்டங்கள்
9. பயனர் சுயவிவரம்
10. நிர்வாக / மேம்பாட்டு மேனேஜ்மென்ட்

## 4. UI தளங்கள் மற்றும் நிலை

| வரிசை | திரை / பகுதி                          | நிலை             | முக்கிய நோக்கம்                               | குறிப்பு                                    |
| ----- | ------------------------------------- | ---------------- | --------------------------------------------- | ------------------------------------------- |
| 1     | முகப்பு பக்கம்                        | முடிந்தது        | பிராண்ட், கோலங்கள், முக்கிய முடிவுகள்         | தமிழ்-முதல் அறிவிப்பு மற்றும் பயனர் ஈர்ப்பு |
| 2     | விவசாயி டாஷ்போர்டு                    | முடிந்தது        | புல நிலை, ஆரோக்கியம், முன்னுரிமை நடவடிக்கைகள் | புல-திட்டமிடல் மையம்                        |
| 3     | சேவைகள் பக்கம்                        | முடிந்தது        | அனைத்து வேளாண்மை சேவைகளை பார்வை               | பயனர் விருப்பங்கள் மற்றும் வழிசெலுத்தல்     |
| 4     | பயிர் ஆலோசனை                          | முடிந்தது        | பருவம், நீர், உரம், பூச்சி மேலாண்மை           | சாகுபடி முடிவுகள்                           |
| 5     | வானிலை + சந்தை                        | முடிந்தது        | வானிலை, எச்சரிக்கை, மண்டி விலை                | வர்த்தகம் + சாகுபடி ஒருங்கிணைப்பு           |
| 6     | மண் பரிசோதனை                          | திட்டமிடப்பட்டது | pH, ஈரப்பதம், ஊட்டச்சத்து, பரிந்துரை          | தரவு-நடுவண் பகுப்பாய்வு                     |
| 7     | நோய் கண்டறிதல்                        | திட்டமிடப்பட்டது | புகைப்படம் பதிவேற்றம், AI பகுப்பாய்வு         | காட்சி முடிவு + பரிந்துரை                   |
| 8     | அரசு திட்டங்கள்                       | திட்டமிடப்பட்டது | மானியம், காப்பீடு, கடன், விண்ணப்பம்           | பயனர் உதவி + சான்றுகள்                      |
| 9     | பயனர் லாகின் / பதிவு                  | திட்டமிடப்பட்டது | கிராமப்புற பயனர் சுயவிவரம்                    | எளிமையான OTP / சாதன பதிவு                   |
| 10    | சுயவிவரம் / முன்னேற்றம்               | திட்டமிடப்பட்டது | பயனர் செயல்பாடு, வரலாறு, அமைப்பு              | தனிப்பட்ட பயனர் மேலாண்மை                    |
| 11    | நிர்வாக டாஷ்போர்டு                    | திட்டமிடப்பட்டது | ஊழியர்கள், களப்பணி, மதிப்பீடு                 | மேம்பாட்டு மேலாண்மை                         |
| 12    | நிலைத்தன்மை / கார்பன் / டிரேசபிலிட்டி | திட்டமிடப்பட்டது | ESG, ஆதாரம், நிலைத்தன்மை                      | வணிக மற்றும் கூட்டுறவு மையம்                |

## 5. UIஇன் தமிழ் வடிவமைப்பு கொள்கைகள்

### 5.1 மொழி மற்றும் வாசிப்பு

- எளிய, நாள்-நாள் தமிழில் கட்டுரை
- பெரிய எழுத்துரு (14–18px minimum on mobile)
- குறுகிய தலைப்புகள்
- பொத்தான்கள் மற்றும் அறிகுறிகள் தெளிவாக இருக்கும்

### 5.2 நிறங்கள்

- பச்சை: பயிர், ஆரோக்கியம், நிலைத்தன்மை
- பழுப்பு: மண் மற்றும் விவசாயம்
- நீலம்: நீர், வானிலை, நம்பகத்தன்மை
- மஞ்சள்: எச்சரிக்கை, கவனம், அபாயம்
- சாம்பல் / வெள்ளை: பின்னணி மற்றும் நேர்த்தி

### 5.3 UI கூறுகள்

- நிலை பிளேடுகள்
- விரிவான கார்டுகள்
- AI/எச்சரிக்கை கூற்றுகள்
- சமீபத்திய நடவடிக்கை அட்டவணைகள்
- இழப்பு / தரவு / செயல்கள் தொடர்பான பட்டிகள்

## 6. பயனர் அனுபவம் (UX) விருப்பங்கள்

### Farmer journey

1. முகப்பு பக்கம்
2. சேவைகள் தேர்வு
3. மண் / வானிலை / சந்தை வழிகாட்டுதல்
4. பணிப்பட்டியல் / ஆலோசனைx
5. முடிவு சுருக்கம்
6. இயங்கும் நடவடிக்கை

### Volunteer / field staff journey

1. கிராம மண்டல டாஷ்போர்டு
2. புல கண்காணிப்பு
3. குறைபாடு பதிவு
4. பயிர் ஆலோசனை வெளியீடு
5. அறிக்கை அனுப்பு

## 7. செயல்படுத்தல் முன்னுரிமை

### Completed

- Home page
- Dashboard
- Services page
- Advisory page
- Weather and market page

### In progress

- Soil health page
- Disease detection page
- Farmer login and registration experience
- Government schemes page

### Planned

- Profile page
- Admin dashboard
- Sustainability tracker
- Traceability dashboard
- Voice assistant and offline support

## 8. Implementation backlog map

| பகுதி                    | முன்னுரிமை | நிலை        | குறிப்புகள்                        | அடுத்த நடவடிக்கை                     |
| ------------------------ | ---------- | ----------- | ---------------------------------- | ------------------------------------ |
| Landing experience       | High       | done        | Tamil-first home page              | final polish                         |
| Dashboard                | High       | done        | field metrics and crop health view | add real data wiring                 |
| Services catalog         | High       | done        | grouped agriculture services       | add deep links                       |
| Crop advisory            | High       | done        | seasonal guidance and irrigation   | connect to logic engine              |
| Weather and market       | High       | done        | risk + price decision layer        | live API integration                 |
| Soil health              | High       | in-progress | pH, moisture, fertility guidance   | create dedicated page                |
| Disease detection        | High       | in-progress | scan and AI review flow            | add image upload workflow            |
| Government schemes       | Medium     | planned     | benefits and subsidy info          | add local Tamil content              |
| Farmer profile           | Medium     | planned     | user history and farm record       | add editable fields                  |
| Admin console            | Medium     | planned     | operations oversight               | add role support                     |
| Sustainability dashboard | Medium     | planned     | carbon and regenerative metrics    | add analytics                        |
| Traceability flow        | Medium     | planned     | supply chain journey               | add lot-based data model             |
| Offline mode             | High       | planned     | local cache and safe actions       | implement service worker / app cache |
| Voice assistant          | Low        | planned     | Tamil audio guidance               | integrate TTS and speech support     |

## 9. தரவு மற்றும் தொழில்நுட்ப கோரிக்கைகள்

- FastAPI backend stays as the source of truth
- HTML/UI pages can be progressively upgraded to React Native or Flutter app screens
- backend response contract must support both English and Tamil labels
- all screens must support offline-safe fallback content
- all farmer-facing text must be reviewed by local agronomy and language reviewers

## 10. Exit criteria

UI work is considered ready for the next product milestone when all pages below are implemented with consistent language, layout, and field-use clarity:

- home
- dashboard
- services
- advisory
- weather-market
- soil-test
- disease-detection
- scheme-guidance
- profile
- admin

## 11. Final recommendation

Tamil-first UI flow should be treated as a core product decision, not just cosmetic localization. For Tamil Nadu farmers, the interface must be simple enough for first-time users, informative enough for field decisions, and robust enough for off-grid environments. This makes the UI not only user-friendly but also operationally valuable.
