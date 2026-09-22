# Presenova System: Current Issues, Runtime Diagnostics & Audit Roadmap
**Platform**: Presenova AI Presentation Platform (Flask/SocketIO Backend + Vite/React Frontend)  
**Date**: September 2026  
**Status**: Batch 1 Verified (14/14 Fixes Passed) · 10 Audit Items Pending · 4 Runtime Warnings Identified  

---

## 1. Khulasa-e-Haal (Current Executive Summary)

Is waqt Presenova project me **3 categories** ke masail (issues) aur observations samnay aayi hain:

1. **Hal Shuda Masail (Resolved in Batch 1 - 14 Issues)**:
   - Backend connectivity, token security, permanent file uploads, MediaPipe thread locks, aur frontend camera/mic permissions ke 14 bare issues resolve aur verify ho chuke hain.
2. **Runtime Warnings & Environmental Issues (Active in Console/Logs)**:
   - Test chalane ke doraan 4 ahem warnings aayi hain (spaCy missing model, Gemini deprecated package, HuggingFace unauthenticated hub warning, Firebase live vs offline state).
3. **Baqi Audit Masail (Pending Batch 2 & Batch 3 - 10 Issues)**:
   - FAISS vector search bypass, Vercel CORS dynamic preview regex, CLAHE per-frame memory allocation, error response unification, aur dead code.

---

## 2. Active Runtime Warnings & Environmental Masail (Console Diagnostics)

Jab humne terminal me tests chalaye to ye 4 runtime warnings/masail samnay aaye:

### ⚠️ Masla 1: spaCy Model `en_core_web_sm` Not Installed
- **Kahan aaraha hy**: `services/viva_rag_engine.py` aur `services/rewrite/spacy_rewriter.py`
- **Error message**:
  ```text
  [E050] Can't find model 'en_core_web_sm'. It doesn't seem to be a Python package or a valid path to a data directory.
  ```
- **Kiyun aaraha hy**: System me `spacy` library to mojood hy magar uska English language pack (`en_core_web_sm`) download nahi hua.
- **Asar (Impact)**: Code crash nahi hota kiyunke fallback rule-based regex chal jata hy, magar spaCy ke advanced linguistic features (POS tagging, dependency parsing) degrade ho jate hain.
- **Hal (Fix)**:
  ```powershell
  python -m spacy download en_core_web_sm
  ```

---

### ⚠️ Masla 2: Deprecated Google Generative AI Package
- **Kahan aaraha hy**: `ai_evaluator.py`, `services/gemini_service.py`, `services/ai/gemini_provider.py`
- **Warning message**:
  ```text
  FutureWarning: All support for the `google.generativeai` package has ended. 
  It will no longer be receiving updates or bug fixes. Please switch to the `google.genai` package.
  ```
- **Kiyun aaraha hy**: Google ne purani SDK `google-generativeai` ko sunset/deprecate kar diya hy aur new package `google-genai` introduce kiya hy.
- **Asar (Impact)**: Abhi code bilkul theek chal raha hy (fallback REST + offline evaluators kaam kar rahe hain), magar future me Google is API endpoint ko band kar sakta hy.
- **Hal (Fix)**: Requirements me `google-genai` update karna aur provider ko migrate karna.

---

### ⚠️ Masla 3: HuggingFace Hub Unauthenticated Warning
- **Kahan aaraha hy**: `sentence_transformers` (RAG Engine & Embeddings)
- **Warning message**:
  ```text
  Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits.
  ```
- **Kiyun aaraha hy**: Offline embeddings (`all-MiniLM-L6-v2`) download/check karte waqt bina HuggingFace token ke request ja rahi hy.
- **Asar (Impact)**: Sirf warning hy, model successfully load ho jata hy aur tests pass ho jate hain. Magar high traffic me Hugging Face IP rate-limit kar sakta hy.
- **Hal (Fix)**: `.env` me optional `HF_TOKEN` configure karna ya local cached directory path enforce karna.

---

### ⚠️ Masla 4: Firebase Firestore Connection vs In-Memory Fallback
- **Kahan aaraha hy**: `models.py`
- **Behavior**: Agar internet slow ho ya Firebase credentials offline hon, backend automatically `_MEMORY_STORE` me shift ho jata hy.
- **Asar (Impact)**: In-memory mode me server restart hone par guest/demo sessions wipe ho jate hain. Production deployment par permanent Firestore ensure karna zaroori hy.

---

## 3. Baqi Audit Masail Jo Codebase Me Abhi Baki Hain (Pending 10 Issues)

Pre-Deployment Audit me kul 24 issues identify huay thay. Batch 1 me **14 fix** ho chuke hain. Ye **10 issues** abhi pending hain:

| Issue ID | File / Component | Severity | Masla Kiya Hy? |
| :--- | :--- | :---: | :--- |
| **ISSUE-08** | `services/viva_rag_engine.py` | ⚠️ High | FAISS vector index build to hota hy magar `index.search()` call nahi hota; questions linear sequential loop se bante hain. |
| **ISSUE-16** | `main.py` (CORS Setup) | 🟡 Medium | Vercel PR preview domains (`*.vercel.app`) dynamic hotay hain; backend sirf static comma-separated URLs accept karta hy. |
| **ISSUE-17** | `phase_live.py` | 🟡 Medium | `cv2.createCLAHE()` har incoming video frame (~5-10 times/sec) pe naya banaya jata hy jis se memory/CPU waste hoti hy. |
| **ISSUE-18** | `frontend/src/pages/PresentationRewriter.tsx` | 🟡 Medium | Improved PPTX ka download link relative `/api/...` hy, Vercel frontend pe click krne se 404 dega. |
| **ISSUE-19** | `routes/*`, `phase_two.py`, `phase_four.py` | 🟡 Medium | Har endpoint alag error format bhej raha hy (`success: false`, `error: ...`, `status: error`). Unified contract chahiye. |
| **ISSUE-20** | `models.py` | 🟡 Medium | `PresentationSession.update_metrics()` me `metrics[key].append()` thread-lock ke bahir call ho raha hy. |
| **ISSUE-21** | `phase_four.py` | 🟢 Low | Informal Urdu/developer comment mojood hy (`print(... bytes) # ← ye add karo`). |
| **ISSUE-22** | `services/coach_intent_engine.py`, `viva_rag_engine.py` | 🟢 Low | Developer machine ka hardcoded path hy (`~\AppData\Roaming\Python\Python314\site-packages`). |
| **ISSUE-23** | `frontend/src/pages/LiveCoach.tsx` | 🟢 Low | 100+ lines dead commented-out code mojood hy (`/* COMPARISON_DISABLED */`). |
| **ISSUE-24** | `phase_two.py` | 🟢 Low | Deprecated route `/compare-documents` backend me bachi hui hy jabke frontend wizard remove ho chuka hy. |

---

## 4. Kamyabi Se Hal Shuda Masail (Batch 1 - 14 Issues Completed & Tested)

Ye tamam masail code level par mukammal theek kiye ja chuke hain aur inka test verification pass ho chuka hy:

1. **ISSUE-14**: `phase_two.py` aur `phase_four.py` me uploads ab permanent directory (`instance/uploads/<uuid>/`) me save hotay hain, temporary file delete nahi hoti.
2. **ISSUE-13**: `phase_two.py` me magic byte file signature verification (`validate_file_content`) activate kar di gayi hy.
3. **ISSUE-01**: `phase_live.py` me per-session MediaPipe detector aur concurrency `Lock` implement kiya gaya taake multi-user crash na ho.
4. **ISSUE-02**: `frontend/src/services/api.ts` me hardcoded `http://localhost:5000/` ko dynamically environment URL se replace kiya gaya.
5. **ISSUE-03**: `frontend/src/hooks/useLiveSession.ts` me Vercel relative path hone par `window.location.origin` / `VITE_SOCKET_URL` fallback implement kiya gaya.
6. **ISSUE-04**: `auth.py` aur `main.py` me `jwt.expired_token_loader`, `jwt.invalid_token_loader`, aur `jwt.unauthorized_loader` register kiye gaye.
7. **ISSUE-05**: `auth.py` me `/api/auth/refresh` endpoint banaya gaya jo 24 hours ke baad token expire hone se bachata hy.
8. **ISSUE-06**: `phase_live.py` me live audio chunks ki temporary `.webm` file `finally:` block me guaranteed delete hoti hy taake server disk bhar na jaye.
9. **ISSUE-07**: `phase_live.py` aur `phase_four.py` me Groq Whisper client ke liye `timeout=4.0s` aur `RateLimitError / APITimeoutError` fallback handling dali gayi.
10. **ISSUE-09**: `frontend/src/hooks/useLiveSession.ts` me microphone permission reject hone par `.catch()` aur user error alert lagaya gaya.
11. **ISSUE-10**: `frontend/src/hooks/useLiveSession.ts` me session stop hone par mic ke tamam audio tracks (`track.stop()`) properly release kar diye gaye.
12. **ISSUE-11**: `frontend/src/components/VideoCapture.tsx` me webcam permission block hone par `onError` callback parent UI ko pass kiya gaya.
13. **ISSUE-12**: `routes/question_generator.py` me anonymous request rate limiting (`@rate_limit`) aur questions count ko 3 se 30 ke darmiyan clamp kiya gaya.
14. **ISSUE-15**: `frontend/.env.example` me backend URLs aur Firebase web client ke tamam 8 environment variables document kiye gaye.

---

## 5. Next Steps (Agla Kaam Kiya Karna Hy?)

- **Step 1**: Batch 2 ke Medium Issues (ISSUE-08, ISSUE-16, ISSUE-17, ISSUE-18, ISSUE-19, ISSUE-20) ko resolve karna.
- **Step 2**: Batch 3 ke Housekeeping Issues (ISSUE-21, ISSUE-22, ISSUE-23, ISSUE-24) ko clean karna.
- **Step 3**: Terminal me `python -m spacy download en_core_web_sm` run karna taake spaCy model warning khatam ho jaye.
