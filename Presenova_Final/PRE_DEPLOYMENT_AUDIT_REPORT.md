# Presenova: Pre-Deployment Audit & Codebase Vulnerability Report
**System**: Flask/SocketIO Backend · React/TypeScript/Vite Frontend · Electron Desktop · Flutter Mobile  
**Target Environment**: Vercel (Frontend SPA) + Render/Cloud (Flask WebSocket API)  
**Audit Scope**: Pre-Deployment Readiness, Concurrency, Error Handling, Memory Leaks, Auth & Security  
**Audit Date**: September 2026 · Release 1.1.0  

---

## 1. Executive Summary & Readiness Assessment

This pre-deployment audit evaluates the production readiness of the **Presenova AI Presentation Platform** prior to establishing CI/CD automation and deploying the web frontend to **Vercel**. 

The audit identified **24 distinct technical issues** across the backend API, real-time WebSocket teleprompter stream, machine learning/computer vision perception pipelines, and the React/TypeScript frontend. 

### Summary by Severity

| Severity Level | Issue Count | Primary Risk Areas |
| :--- | :---: | :--- |
| **🚨 Critical** | **3** | Multithreaded MediaPipe race conditions, hardcoded backend URLs, broken Vercel WebSocket resolution |
| **⚠️ High** | **12** | JWT error interception gaps, missing token refresh route, temp file disk leaks, unhandled media permissions, unqueried FAISS vector index, missing file validation |
| **🟡 Medium** | **5** | Vercel dynamic preview CORS blocking, per-frame CLAHE memory re-allocation, relative download links, response schema inconsistencies |
| **🟢 Low** | **4** | Leftover developer comments, hardcoded Windows site-packages path, deprecated comparison dead code |
| **Total Issues** | **24** | **Remediation required before production deployment** |

---

## 2. Complete Issues Catalog & Technical Details

---

### 🚨 Critical Issues (Must Fix Before Any Production Deployment)

#### [ISSUE-01] Global MediaPipe Instance Concurrency Race Condition
- **File**: [`phase_live.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_live.py#L206) (Lines 206, 335–355)
- **Severity**: Critical
- **Component**: Vision Perception / WebSocket Server
- **Root Cause**: `face_mesh_detector` is declared as a global module-level variable initialized once via `init_face_mesh()`. MediaPipe's underlying C++ graph runner is **not thread-safe**. When multiple concurrent users stream webcam frames to `/ws/live-session`, worker threads execute `face_mesh_detector.process(rgb)` simultaneously on the same instance.
- **Production Impact**: Landmark state collisions between different users, corrupted gaze calculations, and native C++ segmentation faults that crash the entire Flask/Gunicorn worker process.
- **Recommended Fix**: Wrap `FaceLandmarker` / `FaceMesh` inside Python's `threading.local()` or instantiate detectors per user session in `_MEMORY_STORE["presentation_sessions"][session_id]["detector"]` with thread-safe lock wrappers.

---

#### [ISSUE-02] Hardcoded `http://localhost:5000/` in Frontend API Service
- **File**: [`frontend/src/services/api.ts`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/services/api.ts#L394-L404) (Lines 394–404)
- **Severity**: Critical
- **Component**: Frontend Networking
- **Root Cause**: The `healthCheck()` utility makes an explicit network call to `'http://localhost:5000/'`:
  ```typescript
  export const healthCheck = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:5000/', { method: 'GET' });
      return response.ok;
    } ...
  };
  ```
- **Production Impact**: On Vercel, client browsers attempt to ping their own local machine on port 5000 rather than the cloud API, causing health checks to fail and falsely reporting backend downtime.
- **Recommended Fix**: Derive the URL from `API_BASE_URL`:
  ```typescript
  const rootUrl = API_BASE_URL.replace(/\/api\/?$/, '') || window.location.origin;
  const response = await fetch(`${rootUrl}/`, { method: 'GET' });
  ```

---

#### [ISSUE-03] Socket.IO Host URL Fallback Fails on Relative Vercel Base Paths
- **File**: [`frontend/src/hooks/useLiveSession.ts`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/hooks/useLiveSession.ts#L45-L46) (Lines 45–46)
- **Severity**: Critical
- **Component**: Real-Time Live Coaching Teleprompter
- **Root Cause**: The socket host resolution logic:
  ```typescript
  const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5000/api';
  const socketHost = apiBase.replace(/\/api\/?$/, '') || 'http://localhost:5000';
  ```
  When deploying to Vercel with a standard reverse-proxy setup, `VITE_API_BASE_URL` is set to `/api` (relative). `"/api".replace(/\/api\/?$/, '')` returns `""` (empty string), which evaluates to `'http://localhost:5000'`.
- **Production Impact**: On production Vercel environments, the live teleprompter fails to connect to the cloud WebSocket server and instead tries to connect to the presenter's local machine.
- **Recommended Fix**: Use `window.location.origin` when the stripped string is empty, or introduce a dedicated `VITE_SOCKET_URL` environment variable:
  ```typescript
  const socketHost = (import.meta as any).env?.VITE_SOCKET_URL || 
    (apiBase.startsWith('http') ? apiBase.replace(/\/api\/?$/, '') : window.location.origin);
  ```

---

### ⚠️ High-Severity Issues

#### [ISSUE-04] JWT Error Handlers Not Registered on `JWTManager` Instance
- **File**: [`auth.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/auth.py#L421-L459) & [`main.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/main.py#L163)
- **Severity**: High
- **Component**: Authentication & Security
- **Root Cause**: `register_jwt_error_handlers(app)` in `auth.py` binds generic Flask handlers (`@app.errorhandler(401)`, `@app.errorhandler(422)`). However, `flask_jwt_extended` intercepts token failures internally and returns default unformatted payloads (`{"msg": "Token has expired"}`) unless configured using `@jwt.expired_token_loader`, `@jwt.invalid_token_loader`, and `@jwt.unauthorized_loader`.
- **Production Impact**: Expired tokens produce non-standard JSON payloads that bypass frontend interceptor parsing in `fetchWithAuth`.
- **Recommended Fix**: Pass `jwt = JWTManager(app)` to `register_jwt_error_handlers(jwt)` and register:
  ```python
  @jwt.expired_token_loader
  def expired_token_callback(jwt_header, jwt_payload):
      return jsonify({"error": "Token expired", "message": "Session expired. Please log in again."}), 401
  ```

---

#### [ISSUE-05] Missing Token Refresh Endpoint (`/api/auth/refresh`)
- **File**: [`auth.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/auth.py)
- **Severity**: High
- **Component**: Authentication Lifecycle
- **Root Cause**: The JWT expiration is configured for 24 hours (`app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)`). However, there is no token refresh endpoint or silent token renewal logic implemented.
- **Production Impact**: Users actively practicing long presentations will be abruptly logged out after 24 hours and lose in-flight rehearsals, with no background refresh mechanism available.
- **Recommended Fix**: Implement `@auth_bp.route('/refresh', methods=['POST'])` with `@jwt_required(refresh=True)` or issue fresh tokens upon active session verification.

---

#### [ISSUE-06] OS Temp File Leak in Live Audio Chunk Processing
- **File**: [`phase_live.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_live.py#L744-L765) (Lines 744–765)
- **Severity**: High
- **Component**: Speech STT / System Resources
- **Root Cause**: In `analyze_audio_chunk()`, a temporary `.webm` file is written to disk on every 3-second audio slice. The cleanup call `os.remove(temp_audio_path)` is placed at the bottom of the `try` block. If `groq_client.audio.transcriptions.create()` throws any exception (rate limit, timeout, socket drop), the execution jumps straight to `except Exception:`, skipping `os.remove()`.
- **Production Impact**: During a live presentation, up to 20 files per minute are leaked in the OS temporary directory on network errors, rapidly exhausting server disk inodes.
- **Recommended Fix**: Enforce cleanup in a `finally` block:
  ```python
  temp_audio_path = None
  try:
      with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
          temp_audio.write(audio_bytes)
          temp_audio_path = temp_audio.name
      # transcribe...
  finally:
      if temp_audio_path and os.path.exists(temp_audio_path):
          try:
              os.remove(temp_audio_path)
          except OSError:
              pass
  ```

---

#### [ISSUE-07] Groq Whisper API Missing Timeout and Rate-Limit Retries
- **File**: [`phase_live.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_live.py#L29) & [`phase_four.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_four.py#L24)
- **Severity**: High
- **Component**: Speech-to-Text Pipeline
- **Root Cause**: `groq_client = Groq(api_key=GROQ_API_KEY)` is initialized without custom timeouts (`timeout=5.0`) or rate-limit retry handlers.
- **Production Impact**: If Groq experiences API latency or transient outages, the WebSocket thread blocks for default socket timeouts (up to 60s), hanging real-time audio telemetry.
- **Recommended Fix**: Instantiate Groq with an explicit request timeout and catch `groq.RateLimitError` and `groq.APITimeoutError`:
  ```python
  from groq import Groq, RateLimitError, APITimeoutError
  groq_client = Groq(api_key=GROQ_API_KEY, timeout=4.0)
  ```

---

#### [ISSUE-08] In-Memory FAISS Vector Index Built but Never Searched in Viva Generator
- **File**: [`services/viva_rag_engine.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/services/viva_rag_engine.py#L201-L220) (Lines 201–220)
- **Severity**: High
- **Component**: Classical ML / Retrieval-Augmented Generation
- **Root Cause**: In `generate_viva_questions_rag()`:
  ```python
  chunks = chunk_text(extracted_text, target_word_count=180)
  index, embeddings = build_faiss_index(chunks)
  
  questions = []
  for i, chunk in enumerate(chunks):  # <-- Sequential iteration!
      terms = extract_key_terms(chunk["text"])
      ...
  ```
  `build_faiss_index` encodes passages and creates an `IndexFlatIP`, but `index.search()` is never invoked. The function simply loops through `chunks` in linear document order.
- **Production Impact**: CPU cycles and RAM are wasted computing SentenceTransformers embeddings and building FAISS indices that are discarded without retrieval benefit.
- **Recommended Fix**: Query the FAISS index with topical question seeds or key entity embeddings to retrieve the most critical defense-worthy passages before synthesizing questions.

---

#### [ISSUE-09] Unhandled Promise Rejection in Live Microphone Capture
- **File**: [`frontend/src/hooks/useLiveSession.ts`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/hooks/useLiveSession.ts#L193-L225) (Lines 193–225)
- **Severity**: High
- **Component**: Frontend Media Recording
- **Root Cause**: The audio capture setup call:
  ```typescript
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => { ... });
  ```
  completely omits a `.catch()` error handler.
- **Production Impact**: When a user rejects microphone permission or has no input device, the promise rejects unhandled. The session remains stuck in `status === 'STREAMING'`, video frames continue transmitting, but no audio telemetry is processed, and the user receives no UI feedback explaining why voice feedback is silent.
- **Recommended Fix**: Attach a `.catch()` block that updates error state and halts the session gracefully:
  ```typescript
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => { ... })
    .catch((err) => {
      setError(`Microphone access error: ${err.message || 'Permission denied'}`);
      stopSession();
    });
  ```

---

#### [ISSUE-10] Live Audio Stream Tracks Never Released on Session Stop
- **File**: [`frontend/src/hooks/useLiveSession.ts`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/hooks/useLiveSession.ts#L153-L166) (Lines 153–166)
- **Severity**: High
- **Component**: Resource Management & Privacy
- **Root Cause**: In `stopMediaStreaming()`, `mediaRecorderRef.current.stop()` is called, but the underlying `MediaStream` tracks (`localAudioStream.getTracks()`) are never stopped.
- **Production Impact**: The browser's red microphone recording indicator remains illuminated indefinitely after the user clicks "Finish Session". The hardware microphone remains locked until the tab is closed.
- **Recommended Fix**: Store `localAudioStream` in a ref (`audioStreamRef.current`) and stop all tracks during `stopMediaStreaming()`:
  ```typescript
  if (audioStreamRef.current) {
    audioStreamRef.current.getTracks().forEach((track) => track.stop());
    audioStreamRef.current = null;
  }
  ```

---

#### [ISSUE-11] Video Capture Permission Denial Silent to Parent UI
- **File**: [`frontend/src/components/VideoCapture.tsx`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/components/VideoCapture.tsx#L34-L37) (Lines 34–37)
- **Severity**: High
- **Component**: Frontend UX & Composure Tracking
- **Root Cause**: When `navigator.mediaDevices.getUserMedia({ video: ... })` rejects:
  ```typescript
  .catch((err) => {
    console.error('Error accessing webcam:', err);
    setCameraActive(false);
  });
  ```
  The error is written to the developer console, but no callback (`onError`) is passed to notify `LiveCoach.tsx`.
- **Production Impact**: The presenter sees a dark box labeled "Camera is off" with zero indication that camera permissions were blocked or that another app (Zoom/Teams) is locking the webcam.
- **Recommended Fix**: Add `onError?: (errorMsg: string) => void` to `VideoCaptureProps` and invoke it on catch.

---

#### [ISSUE-12] Unauthenticated & Unbounded Question Generator Endpoint
- **File**: [`routes/question_generator.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/routes/question_generator.py#L66-L75) (Lines 66–75)
- **Severity**: High
- **Component**: API Security & Rate Limiting
- **Root Cause**: `/api/questions/generate` has no `@jwt_required` decorator, no `@rate_limit`, and parses `num_questions = int(request.form.get('num_questions', 10))` without bounds clamping.
- **Production Impact**: Any anonymous client can send a loop of requests with `num_questions=100000`, overwhelming the server's CPU with SentenceTransformers embeddings and text splitting.
- **Recommended Fix**: Add `@rate_limit(limit_authenticated=15, limit_guest=3)` and clamp input:
  ```python
  num_questions = max(3, min(30, int(request.form.get('num_questions', 10))))
  ```

---

#### [ISSUE-13] Missing Magic Byte File Signature Verification on Document Uploads
- **File**: [`phase_two.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_two.py#L150-L160) (Lines 150–160)
- **Severity**: High
- **Component**: Upload Security
- **Root Cause**: `phase_two.py` validates file types solely using file extension (`os.path.splitext(file.filename)[1].lower()`). Unlike `presentation_rewriter.py` which calls `validate_file_content(path, name)` to inspect magic bytes (e.g. `PK\x03\x04` for PPTX/DOCX, `%PDF` for PDF), `phase_two.py` directly passes unverified files to parsers.
- **Production Impact**: Renamed executables, corrupted archives, or polyglot binaries will cause parser crashes, unhandled 500 errors, or memory buffer overflows.
- **Recommended Fix**: Import and invoke `validate_file_content(temp_file_path, file.filename)` before parsing.

---

#### [ISSUE-14] Database Upload Records Point to Deleted Temporary Files
- **File**: [`phase_two.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_two.py#L274) & [`phase_four.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_four.py#L380)
- **Severity**: High
- **Component**: Database Integrity
- **Root Cause**: When a document or audio file is analyzed:
  ```python
  upload_record = Upload.create(
      filename=file.filename,
      file_path=temp_file_path,  # <-- Temporary OS path stored!
      user_id=user_id
  )
  ```
  In the `finally` block of both routes, `os.remove(temp_file_path)` executes.
- **Production Impact**: The database stores file paths that no longer exist on disk. Any subsequent feature attempting to retrieve or re-read the original file crashes with `FileNotFoundError`.
- **Recommended Fix**: Either persist files to a permanent storage directory (e.g. `instance/uploads/`) before recording the path, or set `file_path=None` / store file metadata only.

---

#### [ISSUE-15] Incomplete Frontend Environment Variable Template (`.env.example`)
- **File**: [`frontend/.env.example`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/.env.example)
- **Severity**: High
- **Component**: DevOps & CI/CD
- **Root Cause**: `frontend/.env.example` contains only:
  ```env
  VITE_API_BASE_URL=/api
  ```
  It completely omits:
  - `VITE_FIREBASE_API_KEY`
  - `VITE_FIREBASE_AUTH_DOMAIN`
  - `VITE_FIREBASE_PROJECT_ID`
  - `VITE_FIREBASE_STORAGE_BUCKET`
  - `VITE_FIREBASE_MESSAGING_SENDER_ID`
  - `VITE_FIREBASE_APP_ID`
  - `VITE_SOCKET_URL`
- **Production Impact**: Setting up a new staging environment or configuring GitHub Actions / Vercel secrets using `.env.example` as a template results in broken Firebase authentication and silent build failures.
- **Recommended Fix**: Populate `frontend/.env.example` with full placeholder variables mirroring `frontend/.env`.

---

### 🟡 Medium-Severity Issues

#### [ISSUE-16] Fragile CORS Configuration for Vercel Dynamic Preview Deployments
- **File**: [`main.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/main.py#L122-L136) (Lines 122–136)
- **Severity**: Medium
- **Component**: Backend CORS Configuration
- **Root Cause**: `CORS(app)` parses a comma-separated list of exact origin strings from `CORS_ORIGINS`. Vercel creates dynamic URLs for preview/PR deployments (`https://presenova-git-feature-team.vercel.app`), which cannot be hardcoded in advance.
- **Production Impact**: PR preview deployments on Vercel are blocked by CORS preflight failures (403/blocked) when communicating with the staging backend.
- **Recommended Fix**: Support regex patterns or check if the origin matches `r"https://.*\.vercel\.app$"` when `FLASK_ENV != 'production'`.

---

#### [ISSUE-17] CLAHE Re-instantiated on Every Single Video Frame
- **File**: [`phase_live.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_live.py#L522) (Line 522)
- **Severity**: Medium
- **Component**: OpenCV Performance & Memory
- **Root Cause**: Inside `_analyze_frame_with_haar()`:
  ```python
  clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
  enhanced_gray = clahe.apply(gray)
  ```
  `cv2.createCLAHE()` creates a new C++ filter object on every incoming frame (~3 to 10 times per second per user).
- **Production Impact**: Increases CPU overhead and garbage collection pauses under multiple active live sessions.
- **Recommended Fix**: Initialize `_CLAHE = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))` once at module level or reuse it.

---

#### [ISSUE-18] Inconsistent Download Link Protocol in Presentation Rewriter
- **File**: [`frontend/src/pages/PresentationRewriter.tsx`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/pages/PresentationRewriter.tsx#L539) (Line 539)
- **Severity**: Medium
- **Component**: Cross-Domain Asset Downloading
- **Root Cause**: In `PresentationRewriter.tsx`, the download anchor binds `href={result.download_url}` directly:
  ```tsx
  <a href={result.download_url} download>Download Improved PPTX</a>
  ```
  The backend returns a relative path: `/api/presentation-rewriter/download/<filename>`. When frontend is on Vercel (`https://presenova.vercel.app`) and backend is on Render (`https://fyp-presenova.onrender.com`), this link navigates to Vercel and returns 404. Conversely, [`PresentationGenerator.tsx`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/pages/PresentationGenerator.tsx#L680) correctly prefixes `${API_BASE_URL}`.
- **Recommended Fix**: Wrap `result.download_url` with `getDownloadUrl(result.download_url)` that prefixes the API base origin if not already absolute.

---

#### [ISSUE-19] Inconsistent Error Response Schemas Between Blueprints
- **File**: `routes/*`, `phase_two.py`, `phase_four.py`, `phase_live.py`
- **Severity**: Medium
- **Component**: API Contract Standardization
- **Root Cause**:
  - `routes/presentation_rewriter.py` & `routes/question_generator.py` return:
    `{"success": false, "message": "..."}`
  - `phase_two.py`, `phase_four.py`, and `auth.py` return:
    `{"error": "...", "message": "..."}`
  - `phase_live.py` returns:
    `{"status": "error", "message": "..."}`
- **Production Impact**: Frontend API error handlers must check `data.message || data.error || data.details` with multiple fallbacks, leading to unhandled edge cases where error banners display `[object Object]` or blank text.
- **Recommended Fix**: Standardize on a unified error response contract across all blueprints:
  ```json
  {
    "success": false,
    "error": "ShortErrorCode",
    "message": "Human readable message"
  }
  ```

---

#### [ISSUE-20] Unlocked `metrics.append()` in PresentationSession Update
- **File**: [`models.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/models.py#L487-L495) (Lines 487–495)
- **Severity**: Medium
- **Component**: Thread Safety / Shared State
- **Root Cause**: In `PresentationSession.update_metrics(self, key, value)`:
  ```python
  if self.metrics and key in self.metrics:
      if isinstance(self.metrics[key], list):
          self.metrics[key].append(value)  # <-- Outside thread lock!

  with _store_lock:
      if self.id in _MEMORY_STORE["presentation_sessions"]:
          _MEMORY_STORE["presentation_sessions"][self.id]["metrics"] = self.metrics
  ```
  `self.metrics[key].append(value)` executes before acquiring `_store_lock`.
- **Production Impact**: If video frame feedback and audio chunk metrics arrive simultaneously on separate threads for the same session, list appends can encounter race conditions or race against state serialization.
- **Recommended Fix**: Move the list mutation inside the `with _store_lock:` context block.

---

### 🟢 Low-Severity & Housekeeping Issues

#### [ISSUE-21] Leftover Developer Inline Comment in Production Route
- **File**: [`phase_four.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_four.py#L288) (Line 288)
- **Severity**: Low
- **Component**: Code Quality & Cleanliness
- **Description**: Contains:
  ```python
  print(f"📦 Saved audio file size: {os.path.getsize(temp_file_path)} bytes")  # ← ye add karo
  ```
- **Recommended Fix**: Remove the informal comment.

---

#### [ISSUE-22] Hardcoded Windows Python 3.14 Path in RAG Modules
- **File**: [`services/coach_intent_engine.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/services/coach_intent_engine.py#L14-L16) & [`services/viva_rag_engine.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/services/viva_rag_engine.py#L16-L18)
- **Severity**: Low
- **Component**: Environment Portability
- **Description**: Contains:
  ```python
  site_packages = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
  if os.path.exists(site_packages) and site_packages not in sys.path:
      sys.path.insert(0, site_packages)
  ```
  This is a developer-machine specific workaround that adds noise when running in Linux Docker containers or virtual environments.
- **Recommended Fix**: Remove the hardcoded Windows path and rely on standard Python virtualenv packaging.

---

#### [ISSUE-23] 100+ Lines of Commented Dead Code in LiveCoach Component
- **File**: [`frontend/src/pages/LiveCoach.tsx`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/frontend/src/pages/LiveCoach.tsx#L116-L172) (Lines 116–121, 143–172, 210–276)
- **Severity**: Low
- **Component**: Frontend Bundle Size & Maintainability
- **Description**: Large blocks of commented-out code (`/* COMPARISON_DISABLED ... */`) from the deprecated V1 vs V2 comparison report feature remain inside `LiveCoach.tsx`.
- **Recommended Fix**: Delete dead commented blocks to reduce bundle bloat.

---

#### [ISSUE-24] Dead Route Remaining in Document Analyzer Backend
- **File**: [`phase_two.py`](file:///c:/Users/Muhammad/Downloads/FYP%20Final_1.2/phase_two.py#L315-L388) (Lines 315–388)
- **Severity**: Low
- **Component**: API Surface Minimization
- **Description**: `@phase_two_bp.route('/compare-documents', methods=['POST'])` remains registered on the backend, but the frontend comparison wizard was deprecated and removed.
- **Recommended Fix**: Remove or deprecate the dead route to minimize untested attack surface.

---

## 3. Recommended Remediation Order

We recommend resolving these issues in **3 sequential batches**:

1. **Batch 1: Production Blockers (Critical & High)**
   - Fix [ISSUE-01], [ISSUE-02], [ISSUE-03]: Concurrency in MediaPipe, hardcoded localhost URLs, and Vercel WebSocket resolution.
   - Fix [ISSUE-06], [ISSUE-07]: Groq Whisper temp file leaks and timeout handling.
   - Fix [ISSUE-09], [ISSUE-10], [ISSUE-11]: Audio track leaks and unhandled camera/microphone errors in `useLiveSession.ts`.
   - Fix [ISSUE-04], [ISSUE-05]: JWT error handlers and refresh endpoint.
   - Fix [ISSUE-12], [ISSUE-13], [ISSUE-15]: Route input clamping, upload magic bytes check, and `.env.example` completion.

2. **Batch 2: Performance & Contract Consistency (Medium)**
   - Fix [ISSUE-16]: CORS Vercel dynamic regex.
   - Fix [ISSUE-17], [ISSUE-18], [ISSUE-20]: CLAHE re-allocation, download URL consistency, and thread-safe session metrics update.
   - Fix [ISSUE-08]: FAISS vector index query integration in `viva_rag_engine.py`.
   - Fix [ISSUE-19]: Unified error response schema.

3. **Batch 3: Housekeeping & Dead Code Removal (Low)**
   - Fix [ISSUE-21], [ISSUE-22], [ISSUE-23], [ISSUE-24]: Comments, dead paths, and deprecated comparison code cleanup.

---
*Report generated for user review. No code modifications have been applied.*
