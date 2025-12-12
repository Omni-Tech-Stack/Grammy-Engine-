# 📡 Grammy Engine API Documentation

Complete REST API reference for Grammy Engine platform.

**Base URL:** `https://api.grammyengine.com/api`  
**Version:** 1.0.0  
**Protocol:** HTTPS only  
**Authentication:** JWT Bearer Token

---

## 🔐 Authentication

### **Register New User**

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "artist@example.com",
  "password": "SecurePass123!",
  "name": "John Artist"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "artist@example.com",
    "name": "John Artist",
    "tier": "free",
    "tracks_remaining": 3,
    "created_at": "2025-01-20T10:30:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**
- `400`: Email already registered
- `422`: Invalid email format or weak password

---

### **Login**

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
username=artist@example.com&password=SecurePass123!
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**
- `401`: Invalid credentials
- `422`: Missing username or password

---

### **Refresh Token**

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### **Get Current User**

```http
GET /auth/me
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "artist@example.com",
  "name": "John Artist",
  "tier": "pro",
  "tracks_remaining": 999,
  "total_tracks": 42,
  "created_at": "2025-01-20T10:30:00Z"
}
```

---

## 🎵 Prompt Engine

### **Enhance Prompt**

Transform basic prompt into detailed music production instruction.

```http
POST /prompt/enhance
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "prompt": "chill lofi beat",
  "style": "detailed",
  "include_technical": true
}
```

**Response (200 OK):**
```json
{
  "original_prompt": "chill lofi beat",
  "enhanced_prompt": "Laid-back lo-fi hip hop instrumental with warm vinyl crackle texture, featuring mellow Rhodes piano melody over dusty drum loop at 80 BPM, subtle jazz guitar plucks, deep sub bass, atmospheric tape hiss, rainy day ambience, perfect for studying or relaxation",
  "detected_genre": "Lo-Fi Hip Hop",
  "detected_mood": "Relaxed, Nostalgic",
  "suggested_bpm": 80,
  "suggested_key": "C minor",
  "estimated_duration": 120,
  "production_notes": {
    "instruments": ["Rhodes Piano", "Drum Loop", "Jazz Guitar", "Sub Bass"],
    "effects": ["Vinyl Crackle", "Tape Hiss", "Reverb"],
    "mixing_tips": "Use sidechain compression on bass, add lo-pass filter to drums"
  }
}
```

**Query Parameters:**
- `style` (optional): `minimal`, `balanced`, `detailed` (default: `balanced`)
- `include_technical` (optional): Include production notes (default: `false`)

---

### **Get Prompt Templates**

```http
GET /prompt/templates
```

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "lofi-hiphop",
      "name": "Lo-Fi Hip Hop",
      "prompt": "Chill lo-fi hip hop beat with jazzy piano, vinyl crackle, 80 BPM",
      "genre": "Hip Hop",
      "tags": ["chill", "study", "relaxing"],
      "duration": 120
    },
    {
      "id": "summer-pop",
      "name": "Summer Pop",
      "prompt": "Upbeat summer pop song with tropical vibes, catchy chorus, 120 BPM",
      "genre": "Pop",
      "tags": ["upbeat", "tropical", "catchy"],
      "duration": 180
    }
  ]
}
```

---

## 🎼 Song Generation

### **Generate Song**

Create instrumental track from prompt (async operation).

```http
POST /songgen/generate
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "prompt": "Upbeat summer pop song with tropical vibes, catchy chorus, 120 BPM",
  "duration": 180,
  "model": "musicgen-large",
  "quality": "high",
  "temperature": 0.8,
  "top_k": 250
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "a3f5e8d0-1234-5678-9abc-def012345678",
  "track_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "estimated_time": 45,
  "queue_position": 3
}
```

**Parameters:**
- `prompt` (required): Music description
- `duration` (optional): Length in seconds (15-300, default: 30)
- `model` (optional): `musicgen-small`, `musicgen-medium`, `musicgen-large` (default: `medium`)
- `quality` (optional): `draft`, `standard`, `high` (default: `standard`)
- `temperature` (optional): Creativity level 0.0-1.5 (default: 1.0)
- `top_k` (optional): Sampling diversity 0-250 (default: 250)

**Tier Limits:**
- Free: 3 tracks/month, max 30s, `musicgen-small` only
- Pro: Unlimited, max 180s, all models
- Label: Unlimited, max 300s, all models, priority queue

---

### **Check Generation Status**

```http
GET /songgen/status/{task_id}
Authorization: Bearer {access_token}
```

**Response (200 OK) - In Progress:**
```json
{
  "task_id": "a3f5e8d0-1234-5678-9abc-def012345678",
  "status": "processing",
  "progress": 65,
  "current_step": "Generating audio",
  "estimated_remaining": 20
}
```

**Response (200 OK) - Completed:**
```json
{
  "task_id": "a3f5e8d0-1234-5678-9abc-def012345678",
  "status": "completed",
  "progress": 100,
  "track": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Summer Vibes",
    "audio_url": "https://storage.supabase.co/audio/550e8400.mp3",
    "waveform_url": "https://storage.supabase.co/waveforms/550e8400.png",
    "duration": 180.5,
    "created_at": "2025-01-20T10:35:00Z"
  }
}
```

**Status Values:**
- `queued`: Waiting in queue
- `processing`: Currently generating
- `completed`: Finished successfully
- `failed`: Generation failed
- `cancelled`: User cancelled

---

### **Cancel Generation**

```http
DELETE /songgen/cancel/{task_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "message": "Generation cancelled",
  "refunded": true
}
```

---

## 🎤 Vocal Generation

### **Generate Vocals**

Add AI-generated vocals to instrumental (async operation).

```http
POST /vocalgen/generate
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "track_id": "550e8400-e29b-41d4-a716-446655440000",
  "lyrics": "Summer days, endless waves...",
  "voice_style": "pop-female-bright",
  "pitch_shift": 0,
  "auto_tune": true
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "b4g6f9e1-2345-6789-0bcd-efg123456789",
  "status": "queued",
  "estimated_time": 30
}
```

**Parameters:**
- `track_id` (required): Instrumental track UUID
- `lyrics` (optional): Text to sing (if empty, generates humming/vocalizations)
- `voice_style` (optional): Voice preset (see `/vocalgen/voices`)
- `pitch_shift` (optional): Semitones -12 to +12 (default: 0)
- `auto_tune` (optional): Apply pitch correction (default: false)

---

### **Available Voice Styles**

```http
GET /vocalgen/voices
```

**Response (200 OK):**
```json
{
  "voices": [
    {
      "id": "pop-female-bright",
      "name": "Pop Female (Bright)",
      "gender": "female",
      "range": "Soprano",
      "genres": ["Pop", "EDM", "Dance"],
      "sample_url": "https://storage.supabase.co/samples/pop-female-bright.mp3"
    },
    {
      "id": "rnb-male-smooth",
      "name": "R&B Male (Smooth)",
      "gender": "male",
      "range": "Tenor",
      "genres": ["R&B", "Soul", "Hip Hop"],
      "sample_url": "https://storage.supabase.co/samples/rnb-male-smooth.mp3"
    }
  ]
}
```

---

### **Clone Voice**

Upload reference audio to create custom voice model (Pro tier+).

```http
POST /vocalgen/clone
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
file: (audio file, .mp3/.wav, 30-60s clean vocals)
name: "My Custom Voice"
```

**Response (202 Accepted):**
```json
{
  "task_id": "c5h7g0f2-3456-7890-1cde-fgh234567890",
  "voice_id": "custom-voice-uuid",
  "status": "processing",
  "estimated_time": 120
}
```

---

## 🎚️ MixMaster (Mastering)

### **Master Track**

Apply professional mastering (async operation).

```http
POST /mixmaster/master
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "track_id": "550e8400-e29b-41d4-a716-446655440000",
  "preset": "spotify-loud",
  "target_lufs": -14.0,
  "reference_track_url": null
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "d6i8h1g3-4567-8901-2def-ghi345678901",
  "status": "queued",
  "estimated_time": 25
}
```

**Parameters:**
- `track_id` (required): Track UUID to master
- `preset` (optional): Mastering preset (see `/mixmaster/presets`)
- `target_lufs` (optional): Target loudness -23 to -8 LUFS (default: -14)
- `reference_track_url` (optional): URL of reference track for style matching

---

### **Mastering Presets**

```http
GET /mixmaster/presets
```

**Response (200 OK):**
```json
{
  "presets": [
    {
      "id": "spotify-loud",
      "name": "Spotify Loud",
      "description": "Modern streaming optimized (-14 LUFS)",
      "target_lufs": -14.0,
      "use_cases": ["Streaming", "Playlists"]
    },
    {
      "id": "vinyl-warm",
      "name": "Vinyl Warm",
      "description": "Vintage warmth with analog saturation",
      "target_lufs": -16.0,
      "use_cases": ["Vinyl", "Lo-Fi", "Retro"]
    },
    {
      "id": "radio-ready",
      "name": "Radio Ready",
      "description": "Competitive loudness for radio (-8 LUFS)",
      "target_lufs": -8.0,
      "use_cases": ["Radio", "TV", "Commercial"]
    }
  ]
}
```

---

## 🏆 Grammy Meter

### **Analyze Track**

Predict hit potential and get actionable feedback (async).

```http
POST /grammy-meter/analyze
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "track_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "e7j9i2h4-5678-9012-3efg-hij456789012",
  "status": "queued",
  "estimated_time": 15
}
```

---

### **Get Analysis Result**

```http
GET /grammy-meter/result/{task_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "track_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 82.5,
  "rating": "Grammy Worthy",
  "categories": {
    "production_quality": {
      "score": 88,
      "weight": 0.25,
      "breakdown": {
        "mix_balance": 90,
        "frequency_distribution": 85,
        "dynamic_range": 88
      }
    },
    "commercial_appeal": {
      "score": 78,
      "weight": 0.30,
      "breakdown": {
        "catchiness": 82,
        "structure": 75,
        "hook_strength": 80
      }
    },
    "innovation": {
      "score": 75,
      "weight": 0.15,
      "breakdown": {
        "uniqueness": 72,
        "genre_fusion": 78
      }
    },
    "emotional_impact": {
      "score": 85,
      "weight": 0.20,
      "breakdown": {
        "energy": 88,
        "mood_consistency": 82
      }
    },
    "radio_readiness": {
      "score": 80,
      "weight": 0.10,
      "breakdown": {
        "loudness": 85,
        "duration": 75
      }
    }
  },
  "insights": [
    "🎯 Strong commercial potential with catchy hooks",
    "🔊 Excellent production quality and mix balance",
    "⚡ High energy level suitable for playlists"
  ],
  "recommendations": [
    "📈 Consider shortening intro by 5 seconds for better engagement",
    "🎚️ Boost high-end frequencies for more clarity",
    "🎼 Add variation in final chorus to maintain interest"
  ],
  "comparable_tracks": [
    {
      "title": "Blinding Lights",
      "artist": "The Weeknd",
      "similarity": 0.78
    }
  ],
  "analyzed_at": "2025-01-20T10:40:00Z"
}
```

**Score Ratings:**
- `90-100`: Grammy Potential
- `75-89`: Grammy Worthy
- `60-74`: Hit Potential
- `40-59`: Needs Improvement
- `0-39`: Rework Recommended

---

### **Get Leaderboard**

```http
GET /grammy-meter/leaderboard
```

**Query Parameters:**
- `period` (optional): `today`, `week`, `month`, `all-time` (default: `week`)
- `genre` (optional): Filter by genre
- `limit` (optional): Number of results (default: 100)

**Response (200 OK):**
```json
{
  "period": "week",
  "updated_at": "2025-01-20T10:00:00Z",
  "tracks": [
    {
      "rank": 1,
      "track_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Summer Vibes",
      "artist": "John Artist",
      "score": 92.3,
      "genre": "Pop",
      "created_at": "2025-01-18T14:20:00Z"
    }
  ]
}
```

---

## 📤 File Upload

### **Upload Audio File**

Upload existing audio for mastering or analysis.

```http
POST /upload/audio
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
file: (audio file, .mp3/.wav/.flac, max 50MB)
title: "My Track"
```

**Response (201 Created):**
```json
{
  "track_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Track",
  "audio_url": "https://storage.supabase.co/audio/550e8400.mp3",
  "duration": 245.8,
  "format": "mp3",
  "bitrate": 320000,
  "sample_rate": 44100
}
```

**File Requirements:**
- **Formats:** .mp3, .wav, .flac, .m4a
- **Max Size:** 50MB (Free), 200MB (Pro), 1GB (Label)
- **Duration:** Max 10 minutes

---

## 📦 Track Management

### **List User Tracks**

```http
GET /tracks
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `status` (optional): `completed`, `processing`, `failed`
- `sort` (optional): `created_at`, `title`, `duration` (default: `created_at`)
- `order` (optional): `asc`, `desc` (default: `desc`)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "total": 42,
  "limit": 50,
  "offset": 0,
  "tracks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Summer Vibes",
      "audio_url": "https://storage.supabase.co/audio/550e8400.mp3",
      "waveform_url": "https://storage.supabase.co/waveforms/550e8400.png",
      "duration": 180.5,
      "status": "completed",
      "grammy_score": 82.5,
      "created_at": "2025-01-20T10:35:00Z"
    }
  ]
}
```

---

### **Get Track Details**

```http
GET /tracks/{track_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Summer Vibes",
  "audio_url": "https://storage.supabase.co/audio/550e8400.mp3",
  "waveform_url": "https://storage.supabase.co/waveforms/550e8400.png",
  "duration": 180.5,
  "status": "completed",
  "prompt": {
    "original": "Upbeat summer pop song",
    "enhanced": "Upbeat summer pop song with tropical vibes..."
  },
  "generation_settings": {
    "model": "musicgen-large",
    "temperature": 0.8,
    "duration": 180
  },
  "grammy_score": {
    "overall": 82.5,
    "production_quality": 88,
    "commercial_appeal": 78
  },
  "created_at": "2025-01-20T10:35:00Z",
  "updated_at": "2025-01-20T10:36:15Z"
}
```

---

### **Delete Track**

```http
DELETE /tracks/{track_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

---

## 💳 Subscription Management

### **Get Pricing Tiers**

```http
GET /subscriptions/tiers
```

**Response (200 OK):**
```json
{
  "tiers": [
    {
      "id": "free",
      "name": "Starter",
      "price": 0,
      "interval": "month",
      "features": {
        "tracks_per_month": 3,
        "max_duration": 30,
        "models": ["musicgen-small"],
        "mastering": false,
        "grammy_meter": false,
        "priority_queue": false
      }
    },
    {
      "id": "pro",
      "name": "Pro Creator",
      "price": 29,
      "interval": "month",
      "stripe_price_id": "price_1234567890",
      "features": {
        "tracks_per_month": 9999,
        "max_duration": 180,
        "models": ["musicgen-small", "musicgen-medium", "musicgen-large"],
        "mastering": true,
        "grammy_meter": true,
        "priority_queue": false,
        "voice_cloning": true
      }
    },
    {
      "id": "label",
      "name": "Label Plan",
      "price": 199,
      "interval": "month",
      "stripe_price_id": "price_0987654321",
      "features": {
        "tracks_per_month": 9999,
        "max_duration": 300,
        "models": ["musicgen-small", "musicgen-medium", "musicgen-large"],
        "mastering": true,
        "grammy_meter": true,
        "priority_queue": true,
        "voice_cloning": true,
        "api_access": true,
        "multi_user": 5
      }
    }
  ]
}
```

---

### **Create Checkout Session**

```http
POST /subscriptions/checkout
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "tier_id": "pro",
  "success_url": "https://grammyengine.com/success",
  "cancel_url": "https://grammyengine.com/pricing"
}
```

**Response (200 OK):**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

---

## 📊 Analytics

### **Get Usage Stats**

```http
GET /analytics/usage
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `period` (optional): `day`, `week`, `month`, `year` (default: `month`)

**Response (200 OK):**
```json
{
  "period": "month",
  "tracks_generated": 42,
  "tracks_mastered": 28,
  "tracks_analyzed": 35,
  "total_duration": 5430.5,
  "average_grammy_score": 76.8,
  "storage_used": "1.2 GB",
  "daily_breakdown": [
    {"date": "2025-01-01", "tracks": 2},
    {"date": "2025-01-02", "tracks": 3}
  ]
}
```

---

## ⚠️ Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly track limit reached. Upgrade to Pro for unlimited tracks.",
    "details": {
      "current_tier": "free",
      "tracks_used": 3,
      "tracks_limit": 3
    }
  }
}
```

### **Common Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or expired token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `QUOTA_EXCEEDED` | 429 | Usage limit reached |
| `VALIDATION_ERROR` | 422 | Invalid request parameters |
| `RATE_LIMIT` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |

---

## 🔒 Rate Limiting

**Limits (per user):**
- Free: 100 requests/hour
- Pro: 1,000 requests/hour
- Label: 10,000 requests/hour

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642686000
```

**Exceeded:**
```json
{
  "error": {
    "code": "RATE_LIMIT",
    "message": "Rate limit exceeded. Try again in 15 minutes.",
    "retry_after": 900
  }
}
```

---

## 🌐 Webhooks

Subscribe to events for real-time updates (Label tier+).

### **Available Events**
- `track.generated`: Song generation completed
- `track.mastered`: Mastering completed
- `track.analyzed`: Grammy Meter analysis completed
- `subscription.updated`: User changed subscription
- `quota.warning`: Approaching usage limit

### **Webhook Payload**
```json
{
  "event": "track.generated",
  "timestamp": "2025-01-20T10:35:00Z",
  "data": {
    "track_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-uuid",
    "status": "completed"
  },
  "signature": "sha256=abcdef1234567890..."
}
```

---

## 📚 SDKs & Libraries

**Official SDKs:**
- Python: `pip install grammy-engine`
- JavaScript: `npm install @grammy-engine/sdk`
- Ruby: `gem install grammy_engine`

**Example Usage (Python):**
```python
from grammy_engine import GrammyClient

client = GrammyClient(api_key="your_api_key")

# Generate track
track = client.generate_song(
    prompt="Chill lo-fi beat",
    duration=120
)

# Wait for completion
track.wait_until_complete()

# Get Grammy Score
score = client.analyze_track(track.id)
print(f"Score: {score.overall}")
```

---

## 🆘 Support

- **API Status:** [status.grammyengine.com](https://status.grammyengine.com)
- **Documentation:** [docs.grammyengine.com](https://docs.grammyengine.com)
- **Email:** api@grammyengine.com
- **Discord:** [Join our community](https://discord.gg/grammyengine)

---

**Last Updated:** 2025-01-20  
**Version:** 1.0.0
