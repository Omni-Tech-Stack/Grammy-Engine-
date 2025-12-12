# 🏗️ Grammy Engine - System Architecture

## 📐 High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│   │   Web App    │  │  Mobile App  │  │   API Docs   │                  │
│   │  (Next.js)   │  │ (React Native│  │   (Swagger)  │                  │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└──────────┼──────────────────┼──────────────────┼──────────────────────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐            │
│  │   Auth    │  │  Prompt   │  │  SongGen  │  │  MixMaster │            │
│  │  Router   │  │  Router   │  │  Router   │  │   Router   │            │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘            │
│        │              │              │              │                     │
│  ┌─────┴───────────────┴──────────────┴──────────────┴──────┐            │
│  │                  Middleware Layer                          │            │
│  │  [CORS] [Rate Limit] [JWT Auth] [Request Logging]        │            │
│  └────────────────────────────────────────────────────────────┘            │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌───────────────────┐
│   SUPABASE    │      │  CELERY WORKERS │      │   REDIS BROKER    │
│  (Database)   │      │                 │      │                   │
│               │      │  ┌────────────┐ │      │  ┌──────────────┐ │
│ ┌───────────┐ │      │  │Generation  │ │      │  │ Task Queue   │ │
│ │   Users   │ │◄─────┼──│  Worker    │◄┼──────┼──│              │ │
│ │  Tracks   │ │      │  │ (GPU/CPU)  │ │      │  │ generation:  │ │
│ │  Prompts  │ │      │  └────────────┘ │      │  │ mastering:   │ │
│ │  Scores   │ │      │                 │      │  │ scoring:     │ │
│ └───────────┘ │      │  ┌────────────┐ │      │  └──────────────┘ │
│               │      │  │ Mastering  │ │      │                   │
│ ┌───────────┐ │      │  │  Worker    │ │      │  ┌──────────────┐ │
│ │  Storage  │ │◄─────┼──│   (CPU)    │ │      │  │Result Backend│ │
│ │  (Audio)  │ │      │  └────────────┘ │      │  │   (Cache)    │ │
│ └───────────┘ │      │                 │      │  └──────────────┘ │
└───────────────┘      │  ┌────────────┐ │      └───────────────────┘
                       │  │  Scoring   │ │
                       │  │  Worker    │ │
                       │  │   (CPU)    │ │
                       │  └────────────┘ │
                       └─────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────────┐    ┌────────────────┐
│   OPENAI     │      │   MUSICGEN       │    │   MATCHERING   │
│   (GPT-4)    │      │   (Meta AI)      │    │   (Mastering)  │
│              │      │                  │    │                │
│ • Prompt     │      │ • Audio          │    │ • Audio        │
│   Enhancement│      │   Generation     │    │   Mastering    │
│ • Analysis   │      │ • Style Transfer │    │ • EQ/Compress  │
└──────────────┘      └──────────────────┘    └────────────────┘
```

---

## 🧩 Component Details

### **1. Frontend Layer (Next.js)**

**Purpose:** User interface and client-side logic

**Key Components:**
- **Pages:** Landing, Dashboard, Library, Auth
- **Components:** PromptInput, AudioVisualizer, MeterGauge, TrackCard
- **Hooks:** useGenerate, useAuth, usePlayback, useMeter
- **State Management:** Zustand stores for global state
- **API Client:** Axios with JWT interceptors

**Technology Stack:**
```typescript
- Framework: Next.js 14 (React 18)
- Language: TypeScript 5
- Styling: Tailwind CSS 3.4
- State: Zustand 4.5
- Audio: WaveSurfer.js 7.6
- Charts: Recharts 2.10
```

**Data Flow:**
```
User Input → Component → Hook → API Client → Backend → Response → State Update → UI Render
```

---

### **2. API Gateway (FastAPI)**

**Purpose:** Request routing, validation, authentication

**Routers:**
```python
/api/auth          - Authentication (login, register, refresh)
/api/prompt        - Prompt enhancement and templates
/api/songgen       - Song generation requests
/api/vocalgen      - Vocal generation and cloning
/api/mixmaster     - Mastering and mixing
/api/grammy-meter  - Hit prediction scoring
/api/upload        - File upload to storage
```

**Middleware Stack:**
1. **CORS:** Allow frontend origins
2. **Rate Limiting:** Prevent abuse (100 req/min per IP)
3. **JWT Authentication:** Verify user tokens
4. **Request Logging:** Track all requests
5. **Error Handling:** Standardized error responses

**Authentication Flow:**
```
1. User registers → Password hashed (bcrypt)
2. User logs in → JWT token issued (24h expiry)
3. Refresh token stored (30d expiry)
4. Protected routes verify JWT
5. Expired tokens → Auto-refresh or redirect to login
```

---

### **3. Celery Worker System**

**Purpose:** Asynchronous task processing for long-running jobs

**Queue Architecture:**
```
┌─────────────────────────────────────────────┐
│              REDIS BROKER                   │
├─────────────────────────────────────────────┤
│  Queue: generation (Priority: High)         │
│    - generate_song_task                     │
│    - generate_vocals_task                   │
├─────────────────────────────────────────────┤
│  Queue: mastering (Priority: Medium)        │
│    - master_track_task                      │
│    - apply_effects_task                     │
├─────────────────────────────────────────────┤
│  Queue: scoring (Priority: Low)             │
│    - analyze_track_task                     │
│    - calculate_grammy_score_task            │
└─────────────────────────────────────────────┘
```

**Worker Types:**
- **Generation Worker:** 2 concurrent tasks (GPU-bound)
- **Mastering Worker:** 4 concurrent tasks (CPU-bound)
- **Scoring Worker:** 4 concurrent tasks (CPU-bound)

**Task Lifecycle:**
```
1. API receives request
2. Task queued to Redis
3. Worker picks up task
4. Progress updates sent via callbacks
5. Result stored in Supabase
6. Frontend polls for completion
7. User notified via WebSocket (future)
```

---

### **4. Service Layer**

**Microservices:**

#### **OpenAI Service**
```python
- enhance_prompt(user_prompt) → enhanced_prompt
- analyze_sentiment(prompt) → sentiment_score
- suggest_improvements(track_metadata) → suggestions
```

#### **MusicGen Service**
```python
- generate_audio(prompt, duration, quality) → audio_file
- apply_style_transfer(audio, target_style) → styled_audio
```

#### **VocalSVC Service**
```python
- clone_voice(reference_audio) → voice_model
- generate_vocals(lyrics, voice_model) → vocal_audio
- morph_voice(audio, target_voice) → morphed_audio
```

#### **Matchering Service**
```python
- master_track(audio, reference) → mastered_audio
- apply_preset(audio, preset_name) → processed_audio
- analyze_loudness(audio) → lufs_value
```

#### **Hit Score Service**
```python
- calculate_score(audio) → grammy_score (0-100)
- get_category_scores(audio) → breakdown
- generate_insights(scores) → recommendations
```

#### **Supabase Client**
```python
- upload_file(file, bucket) → public_url
- insert_record(table, data) → record_id
- query_tracks(user_id, filters) → tracks[]
```

---

### **5. Data Models**

**Database Schema:**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    tracks_remaining INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    original_prompt TEXT NOT NULL,
    enhanced_prompt TEXT,
    genre VARCHAR(100),
    mood VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tracks table
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    prompt_id UUID REFERENCES prompts(id),
    title VARCHAR(255),
    audio_url TEXT,
    waveform_url TEXT,
    duration FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    progress INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Grammy Scores table
CREATE TABLE grammy_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    track_id UUID REFERENCES tracks(id),
    overall_score FLOAT,
    production_quality FLOAT,
    commercial_appeal FLOAT,
    innovation FLOAT,
    emotional_impact FLOAT,
    radio_readiness FLOAT,
    insights JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 Request Flow Examples

### **Example 1: Song Generation**

```
1. User enters prompt: "Chill lo-fi hip hop, 90 BPM"
   └─> Frontend: PromptInput.tsx

2. Frontend calls API: POST /api/songgen
   └─> Payload: { prompt: "...", duration: 60, quality: "high" }

3. API validates request, checks quota
   └─> auth.py: verify_token()
   └─> songgen.py: check_user_quota()

4. Task queued to Celery
   └─> celery_app.send_task("generate_song_task")

5. Worker picks up task
   └─> song_tasks.py: generate_song_task()
   └─> Calls: openai_service.enhance_prompt()
   └─> Calls: musicgen_service.generate_audio()

6. Progress updates sent to DB
   └─> 25% → 50% → 75% → 100%

7. Audio file uploaded to Supabase Storage
   └─> supabase_client.upload_file()

8. Track record created in DB
   └─> Track status: "completed"
   └─> Audio URL stored

9. Frontend polls for completion
   └─> GET /api/tracks/{track_id}
   └─> Returns: { status: "completed", audio_url: "..." }

10. User plays audio
    └─> AudioVisualizer.tsx renders waveform
```

---

### **Example 2: Grammy Meter Analysis**

```
1. User uploads track or selects from library
   └─> Frontend: Dashboard.tsx

2. Frontend calls API: POST /api/grammy-meter/analyze
   └─> Payload: { track_id: "uuid" }

3. Task queued to scoring queue
   └─> celery_app.send_task("analyze_track_task")

4. Worker downloads audio from Supabase
   └─> meter_tasks.py: analyze_track_task()

5. Audio features extracted
   └─> librosa.load() → audio array
   └─> Extract: tempo, spectral features, dynamics

6. ONNX model predicts scores
   └─> hit_score_service.calculate_score()
   └─> Returns: { overall: 82, categories: {...} }

7. Insights generated by GPT-4
   └─> openai_service.generate_insights()

8. Score record saved to DB
   └─> grammy_scores table

9. Frontend displays results
   └─> MeterGauge.tsx shows circular gauge
   └─> Category breakdown + recommendations
```

---

## 🚀 Deployment Architecture

### **Production Infrastructure**

```
┌────────────────────────────────────────────────────────────┐
│                      CLOUDFLARE CDN                        │
│                   (Static Assets, DDoS)                    │
└────────────────────────────┬───────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│   VERCEL     │    │    AWS ECS      │    │   SUPABASE   │
│  (Frontend)  │    │   (Backend)     │    │  (Database)  │
│              │    │                 │    │              │
│ • Next.js    │◄───┤ • FastAPI       │◄───┤ • PostgreSQL │
│ • CDN Edge   │    │ • Celery Workers│    │ • Storage    │
│ • Auto Scale │    │ • Auto Scale    │    │ • Auth       │
└──────────────┘    │ • Load Balancer │    └──────────────┘
                    └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            ┌──────────────┐  ┌──────────────┐
            │ REDIS CLOUD  │  │  SENTRY.io   │
            │ (Broker)     │  │ (Monitoring) │
            └──────────────┘  └──────────────┘
```

### **Scaling Strategy**

**Frontend (Vercel):**
- Auto-scales globally via CDN
- Serverless functions for API routes
- Edge caching for static assets

**Backend (AWS ECS):**
- Horizontal scaling based on CPU/memory
- Min: 2 instances, Max: 20 instances
- Load balancer distributes traffic

**Workers (AWS ECS):**
- Separate task definitions per queue
- GPU instances for generation (g4dn.xlarge)
- CPU instances for mastering (c6i.2xlarge)

**Database (Supabase):**
- Managed PostgreSQL with auto-backups
- Read replicas for scaling
- Connection pooling (PgBouncer)

---

## 📊 Performance Metrics

**Target SLAs:**
- **API Response Time:** < 200ms (p95)
- **Song Generation:** < 60s (p95)
- **Mastering:** < 30s (p95)
- **Grammy Meter:** < 15s (p95)
- **Uptime:** 99.9%

**Optimization Techniques:**
1. **Caching:** Redis for frequent queries
2. **CDN:** Static assets served from edge
3. **Database Indexes:** On user_id, created_at
4. **Connection Pooling:** Max 100 concurrent
5. **Task Batching:** Combine similar tasks

---

## 🔐 Security Architecture

**Defense in Depth:**

1. **Network Layer:**
   - Cloudflare WAF (DDoS protection)
   - Rate limiting (100 req/min per IP)
   - IP blacklisting for abuse

2. **Application Layer:**
   - JWT authentication (RS256)
   - Input validation (Pydantic)
   - SQL injection prevention (ORM)
   - XSS protection (React escaping)

3. **Data Layer:**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Database row-level security
   - Sensitive data masking

4. **Secrets Management:**
   - AWS Secrets Manager
   - Environment variables
   - Key rotation (90 days)

---

## 📈 Monitoring & Observability

**Logging Stack:**
```
Application Logs → CloudWatch → S3 Archive
                → Sentry (Errors)
                → PostHog (Analytics)
```

**Metrics Tracked:**
- Request rate, latency, errors (RED)
- CPU, memory, disk (USE)
- Task queue depth
- User engagement (DAU, MAU)
- Revenue metrics (MRR, churn)

**Alerts:**
- Error rate > 1% → PagerDuty
- API latency > 500ms → Slack
- Queue depth > 1000 → Email
- Disk usage > 80% → SMS

---

## 🔄 CI/CD Pipeline

```
GitHub Push
    │
    ├─> GitHub Actions
    │   ├─> Lint (flake8, ESLint)
    │   ├─> Type Check (mypy, TypeScript)
    │   ├─> Unit Tests (pytest, Jest)
    │   ├─> Integration Tests
    │   └─> Build Docker Images
    │
    ├─> Push to ECR/Docker Hub
    │
    └─> Deploy
        ├─> Staging (Auto)
        ├─> Manual Approval
        └─> Production (Blue/Green)
```

---

## 🎯 Future Architecture Enhancements

**Roadmap:**

**Q2 2025:**
- WebSocket real-time updates
- GraphQL API alongside REST
- Multi-region deployment (US, EU, Asia)

**Q3 2025:**
- Kubernetes migration (from ECS)
- Service mesh (Istio)
- Event-driven architecture (Kafka)

**Q4 2025:**
- Microservices split (auth, generation, mastering)
- ML model versioning (MLflow)
- Edge computing for generation

---

**Last Updated:** 2025-01-20  
**Version:** 1.0.0  
**Author:** Omni-Tech-Stack
