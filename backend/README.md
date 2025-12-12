# Grammy Engine Backend

Grammy Prompt Engine™ - AI-Powered Music Generation & Hit Prediction Platform

## Overview

The Grammy Engine backend is a comprehensive FastAPI application that powers an autonomous AI record label, handling everything from prompt enhancement to music generation, vocal synthesis, mixing/mastering, and hit prediction.

## Architecture

- **FastAPI** - Modern async web framework
- **Celery** - Distributed task queue for audio processing
- **Redis** - Message broker and cache
- **Supabase** - PostgreSQL database and file storage
- **PyTorch** - AI model inference
- **MusicGen** - Music generation
- **Librosa** - Audio analysis

## Project Structure

```
backend/
├── api/                    # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── prompt_engine.py   # Prompt enhancement
│   ├── songgen.py         # Music generation
│   ├── vocalgen.py        # Vocal synthesis
│   ├── mixmaster.py       # Mixing & mastering
│   ├── grammy_meter.py    # Hit prediction
│   └── upload.py          # File uploads
├── workers/               # Celery async tasks
│   ├── celery_app.py     # Celery configuration
│   ├── song_tasks.py     # Music generation tasks
│   ├── mix_tasks.py      # Mixing/mastering tasks
│   └── meter_tasks.py    # Analysis tasks
├── services/              # Core business logic
│   ├── openai_service.py       # GPT prompt enhancement
│   ├── musicgen_service.py     # MusicGen integration
│   ├── vocalsvc_service.py     # Vocal generation
│   ├── matchering_service.py   # Audio mastering
│   ├── hit_score_service.py    # Grammy Meter scoring
│   └── supabase_client.py      # Database client
├── models/                # Pydantic models
│   ├── user.py
│   ├── prompt.py
│   ├── track.py
│   └── score.py
├── main.py               # FastAPI application
└── requirements.txt      # Dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file:

```bash
# API Keys
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secret_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Redis
REDIS_URL=redis://localhost:6379/0

# Optional
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

### 3. Run Services

Start Redis:
```bash
redis-server
```

Start Celery worker:
```bash
celery -A workers.celery_app worker --loglevel=info
```

Start FastAPI server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Prompt Engine
- `POST /api/prompt/enhance` - Enhance user prompt
- `POST /api/prompt/analyze` - Analyze prompt
- `GET /api/prompt/templates` - Get prompt templates

### Song Generation
- `POST /api/songgen/generate` - Generate instrumental track
- `GET /api/songgen/status/{task_id}` - Check generation status
- `GET /api/songgen/models` - List available models

### Vocal Generation
- `POST /api/vocalgen/generate` - Generate AI vocals
- `GET /api/vocalgen/voices` - List voice styles
- `POST /api/vocalgen/clone` - Clone voice from sample

### Mix & Master
- `POST /api/mixmaster/process` - Master a track
- `POST /api/mixmaster/reference-match` - Match reference track
- `GET /api/mixmaster/presets` - Get mastering presets
- `POST /api/mixmaster/analyze/{track_id}` - Analyze mix

### Grammy Meter
- `POST /api/meter/analyze` - Calculate Grammy Score
- `GET /api/meter/history/{track_id}` - Score history
- `GET /api/meter/leaderboard` - Top tracks
- `GET /api/meter/benchmarks` - Scoring benchmarks

### Upload
- `POST /api/upload/audio` - Upload audio file
- `DELETE /api/upload/{file_id}` - Delete file
- `GET /api/upload/usage` - Storage usage

## Core Features

### 1. AI Prompt Enhancement
Transforms simple user prompts into detailed production prompts using GPT-4.

### 2. Music Generation
Uses Meta's MusicGen to generate instrumental tracks from text prompts.

### 3. Stem Separation
Separates generated music into individual stems (drums, bass, melody).

### 4. Vocal Synthesis
Generates AI vocals with multiple voice styles and effects.

### 5. Professional Mastering
Applies EQ, compression, loudness normalization, and limiting.

### 6. Grammy Meter™
AI-powered hit prediction analyzing:
- Production Quality
- Commercial Appeal
- Innovation
- Emotional Impact
- Radio Readiness

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
black .
flake8
mypy .
```

### Docker Build
```bash
docker build -t grammy-backend .
docker run -p 8000:8000 grammy-backend
```

## Production Deployment

### AWS ECS
1. Build and push Docker image to ECR
2. Create ECS task definition
3. Deploy to ECS cluster
4. Configure load balancer

### Environment Requirements
- Python 3.11+
- 4GB+ RAM for AI models
- GPU recommended for faster generation
- Redis for task queue
- PostgreSQL database (Supabase)

## License

Proprietary - Grammy Engine™ 2025
