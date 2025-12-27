# 🚂 Railway Deployment Guide - Grammy Engine

This guide provides step-by-step instructions for deploying Grammy Engine to Railway.app, a modern platform-as-a-service that simplifies deployment.

## 📋 Prerequisites

- GitHub account with access to Grammy Engine repository
- Railway account (sign up at [railway.app](https://railway.app))
- OpenAI API key
- Supabase account and credentials
- (Optional) AWS account for S3 storage

## 🚀 Quick Start (One-Click Deploy)

### Option 1: Deploy from GitHub (Recommended)

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Sign up using your GitHub account
   - Link your GitHub repository

2. **Create New Project**
   - Click "New Project" in Railway dashboard
   - Select "Deploy from GitHub repo"
   - Choose `Grammy-Engine-` repository
   - Railway will auto-detect the configuration

3. **Configure Services**
   Railway will create separate services for:
   - Frontend (Next.js)
   - Backend (FastAPI)
   - PostgreSQL (auto-provisioned)
   - Redis (auto-provisioned)

## 🔧 Detailed Setup

### Step 1: Create Backend Service

1. **Add Backend Service**
   - In your Railway project, click "+ New"
   - Select "GitHub Repo"
   - Choose `Grammy-Engine-` repository
   - Set root directory: `/backend`

2. **Configure Environment Variables**
   Add the following variables in Railway dashboard:

   ```bash
   # OpenAI
   OPENAI_API_KEY=sk-...
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=eyJhbGc...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
   
   # Security
   SECRET_KEY=your-secret-key-here-change-this
   
   # Database (auto-provided by Railway PostgreSQL)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   
   # Redis (auto-provided by Railway Redis)
   REDIS_URL=${{Redis.REDIS_URL}}
   CELERY_BROKER_URL=${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
   
   # Production Settings
   ENVIRONMENT=production
   DEBUG=false
   ```

3. **Configure Build & Deploy**
   - Railway auto-detects `backend/railway.json`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Generate Domain**
   - Go to "Settings" tab
   - Click "Generate Domain" under "Public Networking"
   - Copy the generated URL (e.g., `https://backend-production-xxxx.up.railway.app`)

### Step 2: Add PostgreSQL Database

1. **Add Database**
   - Click "+ New" in your project
   - Select "Database" → "PostgreSQL"
   - Railway automatically provisions the database

2. **Connect to Backend**
   - Database URL is automatically available as `${{Postgres.DATABASE_URL}}`
   - Backend service will reference this in `DATABASE_URL` variable

3. **Run Migrations** (Optional)
   - In backend service settings, add a build step:
   ```bash
   pip install -r requirements.txt && python migrate.py
   ```

### Step 3: Add Redis Cache

1. **Add Redis**
   - Click "+ New" in your project
   - Select "Database" → "Redis"
   - Railway automatically provisions Redis

2. **Connect to Backend**
   - Redis URL is automatically available as `${{Redis.REDIS_URL}}`
   - Used for Celery task queue

### Step 4: Create Frontend Service

1. **Add Frontend Service**
   - Click "+ New"
   - Select "GitHub Repo"
   - Choose `Grammy-Engine-` repository
   - Set root directory: `/frontend`

2. **Configure Environment Variables**
   ```bash
   # Backend API URL (use the generated backend domain)
   NEXT_PUBLIC_API_URL=https://backend-production-xxxx.up.railway.app
   ```

3. **Configure Build & Deploy**
   - Railway auto-detects `frontend/railway.json`
   - Build command: `npm install && npm run build`
   - Start command: `npm start`

4. **Generate Domain**
   - Go to "Settings" tab
   - Click "Generate Domain"
   - This is your public frontend URL

### Step 5: Configure Celery Workers (Optional)

For background tasks (music generation, processing):

1. **Create Worker Service**
   - Click "+ New"
   - Select "GitHub Repo"
   - Choose `Grammy-Engine-` repository
   - Set root directory: `/backend`

2. **Override Start Command**
   - In "Settings" → "Deploy"
   - Set start command:
   ```bash
   celery -A workers.celery_app worker --loglevel=info
   ```

3. **Add Environment Variables**
   - Same as backend service
   - Include `REDIS_URL`, `DATABASE_URL`, etc.

## 🔒 Security Configuration

### Custom Domain Setup

1. **Add Custom Domain**
   - Go to service "Settings"
   - Click "Add Custom Domain"
   - Enter your domain (e.g., `api.grammyengine.com`)
   - Update DNS records as instructed

2. **SSL Certificates**
   - Railway automatically provisions SSL certificates
   - HTTPS is enabled by default

### Environment Variables Best Practices

- **Never commit** `.env` files to git
- Use Railway's environment variable dashboard
- Reference sensitive values using `${{SERVICE.VARIABLE}}` syntax
- Rotate keys regularly

## 📊 Monitoring & Logs

### View Logs

1. **Real-time Logs**
   - Click on any service
   - Select "Deployments" tab
   - View live logs for debugging

2. **Log Filters**
   - Use Railway's log search
   - Filter by severity (info, warning, error)

### Health Checks

Railway automatically monitors health check endpoints:

- **Backend**: `GET /health`
- **Frontend**: `GET /api/health`

Health checks run every 30 seconds with 100s timeout.

### Metrics Dashboard

- View CPU, memory, network usage
- Monitor request rates
- Track response times

## 🔄 Continuous Deployment

### Auto-Deploy from GitHub

1. **Configure GitHub Integration**
   - Railway automatically watches your repo
   - Deploys on every push to main branch

2. **Branch Deployments**
   - Create separate Railway projects for staging
   - Deploy from different branches

3. **Rollback**
   - Go to "Deployments" tab
   - Click on previous deployment
   - Select "Redeploy"

## 💰 Cost Estimation

### Railway Pricing Tiers

**Developer Plan ($5/month)**
- $5 of usage included
- Good for testing/development
- Estimated cost: $5-20/month

**Team Plan ($20/month)**
- $20 of usage included
- Better for production
- Estimated cost: $20-100/month

**Usage-Based Costs**
- PostgreSQL: ~$5/month (1GB storage)
- Redis: ~$3/month (100MB)
- Backend: ~$10-30/month (depending on traffic)
- Frontend: ~$5-15/month
- Celery Workers: ~$10-40/month (CPU-intensive)

**Total Estimated Monthly Cost**: $30-120/month

### Cost Optimization Tips

1. **Use Shared Resources**
   - Single PostgreSQL instance for all services
   - Single Redis instance for cache + Celery

2. **Scale Workers Separately**
   - Only run Celery workers when needed
   - Use Railway's auto-scaling

3. **Monitor Usage**
   - Check Railway dashboard weekly
   - Set up billing alerts

## 🐛 Troubleshooting

### Common Issues

#### Build Failures

**Problem**: Python dependencies fail to install
**Solution**:
```bash
# Check nixpacks.toml includes all system dependencies
nixPkgs = ["python39", "postgresql", "ffmpeg", "libsndfile"]
```

**Problem**: Node.js build fails
**Solution**:
```bash
# Ensure package.json includes all dependencies
# Run locally: npm install && npm run build
```

#### Runtime Errors

**Problem**: Database connection fails
**Solution**:
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure backend service references `${{Postgres.DATABASE_URL}}`

**Problem**: CORS errors
**Solution**:
- Verify frontend domain is in backend CORS origins
- Check `NEXT_PUBLIC_API_URL` points to correct backend URL
- Ensure HTTPS is used for production

**Problem**: Health check fails
**Solution**:
- Verify `/health` endpoint responds within 100s
- Check health check path in `railway.json`
- Review logs for initialization errors

#### Performance Issues

**Problem**: Slow response times
**Solution**:
- Scale up backend instances (Settings → Scale)
- Enable Railway's auto-scaling
- Optimize database queries

**Problem**: Out of memory
**Solution**:
- Increase memory allocation (Team plan required)
- Optimize audio processing to use streaming
- Split workers into separate services

### Getting Help

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Grammy Engine Issues**: [GitHub Issues](https://github.com/Omni-Tech-Stack/Grammy-Engine-/issues)

## 📝 Deployment Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Health checks passing
- [ ] PostgreSQL database running
- [ ] Redis cache running
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active
- [ ] Logs monitored for errors
- [ ] Performance tested under load
- [ ] Billing alerts configured
- [ ] Backup strategy in place

## 🔄 Maintenance

### Database Backups

**Automatic Backups** (Railway Pro):
- Daily automated backups
- 7-day retention
- Point-in-time recovery

**Manual Backups**:
```bash
# Using Railway CLI
railway run -- pg_dump $DATABASE_URL > backup.sql
```

### Database Migrations

Run migrations using `backend/migrate.py`:

```bash
# In Railway service, add to build command
pip install -r requirements.txt && python migrate.py
```

### Monitoring

Set up alerts for:
- Service downtime
- High error rates
- Memory/CPU usage
- Database performance

## 🚀 Next Steps

After deployment:

1. **Test All Features**
   - Song generation
   - Vocal synthesis
   - Grammy Meter scoring
   - File uploads

2. **Configure CDN** (Optional)
   - Use Cloudflare for static assets
   - Cache API responses

3. **Set Up Monitoring**
   - Integrate Sentry for error tracking
   - Set up uptime monitoring

4. **Optimize Performance**
   - Enable caching strategies
   - Optimize database indexes
   - Use connection pooling

---

**Need Help?** Open an issue on [GitHub](https://github.com/Omni-Tech-Stack/Grammy-Engine-/issues) or contact the Grammy Engine team.
