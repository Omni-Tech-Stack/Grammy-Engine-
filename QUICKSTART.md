# Grammy Engine - Quick Start Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- 8GB+ RAM (16GB recommended)
- OpenAI API key
- Supabase account (free tier works)
- (Optional) GPU for faster generation

## Step-by-Step Deployment

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/Omni-Tech-Stack/Grammy-Engine.git
cd Grammy-Engine

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Required Environment Variables

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-32-char-secret-key
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Grammy Prompt Engine",
#   "version": "1.0.0",
#   "checks": {
#     "database": "connected",
#     "redis": "connected"
#   }
# }
```

### 5. Test Music Generation

```bash
# 1. Create account
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"testuser"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Save the token from response

# 3. Generate music
curl -X POST http://localhost:8000/api/songgen/generate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "upbeat electronic dance music with drums, 120 BPM",
    "duration": 30,
    "model": "musicgen-medium",
    "temperature": 1.0
  }'

# Returns task_id

# 4. Check status
curl http://localhost:8000/api/songgen/status/TASK_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Wait ~60 seconds for completion
```

### 6. Access Services

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Frontend:** http://localhost:3000 (if running)
- **Celery Monitor:** http://localhost:5555

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│           GRAMMY ENGINE SYSTEM              │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend (Next.js)                         │
│    ↓                                        │
│  API Gateway (FastAPI)                      │
│    ↓                                        │
│  ┌──────────────┐  ┌──────────────┐       │
│  │   Celery     │  │   Services   │       │
│  │   Workers    │  │   Layer      │       │
│  ├──────────────┤  ├──────────────┤       │
│  │ • Generation │  │ • MusicGen   │       │
│  │ • Mastering  │  │ • OpenAI     │       │
│  │ • Scoring    │  │ • Supabase   │       │
│  └──────────────┘  │ • Web3       │       │
│         ↓          └──────────────┘       │
│  ┌──────────────────────────────┐         │
│  │  Storage & Database          │         │
│  │  • PostgreSQL                │         │
│  │  • Redis                     │         │
│  │  • Supabase                  │         │
│  └──────────────────────────────┘         │
└─────────────────────────────────────────────┘
```

## Service Breakdown

### OFF-CHAIN Operations (Core Features)
- ✓ Music generation (MusicGen AI)
- ✓ Prompt enhancement (GPT-4)
- ✓ Vocal synthesis (So-VITS-SVC)
- ✓ Audio mastering (Matchering)
- ✓ Quality scoring (Grammy Meter)
- ✓ File storage (Supabase)
- ✓ User management

### ON-CHAIN Operations (Optional Features)
- ⚡ NFT minting (requires Web3 config)
- ⚡ Marketplace integration
- ⚡ Ownership tracking
- ⚡ Royalty distribution

**Note:** On-chain features are OPTIONAL and don't affect core music generation.

## Performance Expectations

### Music Generation Times

| Duration | Model  | CPU Only | With GPU |
|----------|--------|----------|----------|
| 30s      | Small  | ~45s     | ~15s     |
| 60s      | Medium | ~90s     | ~30s     |
| 180s     | Large  | ~5min    | ~90s     |

### Resource Usage

**Minimum:**
- RAM: 8GB
- CPU: 4 cores
- Disk: 20GB

**Recommended:**
- RAM: 16GB
- CPU: 8 cores
- GPU: NVIDIA GPU with 8GB+ VRAM
- Disk: 50GB SSD

## Troubleshooting

### Model Download Issues

If MusicGen model download fails:

```bash
# Pre-download models
docker-compose exec backend python -c "
from transformers import AutoProcessor, MusicgenForConditionalGeneration
print('Downloading model...')
MusicgenForConditionalGeneration.from_pretrained('facebook/musicgen-small')
print('Done!')
"
```

### Memory Issues

If running out of memory:

```env
# In .env file
LIGHTWEIGHT_MODE=true
MODEL_SIZE=small
MODEL_PRECISION=int8
```

This reduces memory usage by 75%.

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 5
docker-compose up -d
```

### Celery Worker Not Processing

```bash
# Check worker logs
docker-compose logs -f worker

# Restart workers
docker-compose restart worker
```

## Scaling for Production

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  worker:
    deploy:
      replicas: 3  # Run 3 worker instances
```

### Load Balancing

Use Nginx or AWS ALB in front of multiple backend instances.

### Database Optimization

- Enable connection pooling (PgBouncer)
- Add read replicas for heavy read loads
- Index frequently queried columns

## Monitoring

### Health Checks

```bash
# Overall health
curl http://localhost:8000/health

# Celery status
curl http://localhost:5555/api/workers
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS in production
- [ ] Set up firewall rules
- [ ] Keep API keys in environment variables
- [ ] Enable rate limiting
- [ ] Regular security updates

## Next Steps

1. ✓ Deploy system
2. ✓ Test music generation
3. ✓ Verify all services running
4. Generate sample tracks
5. Tune performance settings
6. Add monitoring/alerts
7. Deploy frontend
8. Configure custom domain
9. (Optional) Enable blockchain features

## Support

- Documentation: See `/ARCHITECTURE.md`, `/API_DOCS.md`
- Issues: GitHub Issues
- Community: Discord (link in README)

---

**Quick Reference:**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Clean everything
docker-compose down -v
```

Ready to generate Grammy-worthy music! 🎵
