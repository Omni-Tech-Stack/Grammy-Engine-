# 🚀 Grammy Engine - Deployment Guide

Complete guide for deploying Grammy Engine to production environments.

---

## 📋 Prerequisites

### **Required Accounts**
- ✅ AWS Account (for ECS, ECR, S3)
- ✅ Supabase Account (database, storage, auth)
- ✅ Vercel Account (frontend hosting)
- ✅ OpenAI API Access (GPT-4)
- ✅ Domain name (optional but recommended)

### **Required Tools**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Vercel CLI
npm install -g vercel

# Install Supabase CLI
npm install -g supabase
```

---

## 🏗️ Infrastructure Setup

### **1. Supabase Configuration**

#### **Create New Project**
```bash
# Login to Supabase
supabase login

# Create project (or use web UI)
# Visit: https://app.supabase.com/new
```

#### **Run Database Migrations**
```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    tracks_remaining INT DEFAULT 3,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_prompt TEXT NOT NULL,
    enhanced_prompt TEXT,
    genre VARCHAR(100),
    mood VARCHAR(100),
    duration INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create tracks table
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    prompt_id UUID REFERENCES prompts(id),
    title VARCHAR(255),
    audio_url TEXT,
    waveform_url TEXT,
    duration FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    progress INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create grammy_scores table
CREATE TABLE grammy_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    overall_score FLOAT NOT NULL,
    production_quality FLOAT,
    commercial_appeal FLOAT,
    innovation FLOAT,
    emotional_impact FLOAT,
    radio_readiness FLOAT,
    insights JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tracks_user_id ON tracks(user_id);
CREATE INDEX idx_tracks_created_at ON tracks(created_at DESC);
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_scores_track_id ON grammy_scores(track_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE grammy_scores ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only see their own data)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own tracks" ON tracks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tracks" ON tracks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own prompts" ON prompts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own prompts" ON prompts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

#### **Create Storage Buckets**
```bash
# Via Supabase Dashboard: Storage > New Bucket
# Bucket 1: "audio-files" (public)
# Bucket 2: "waveforms" (public)
# Bucket 3: "models" (private)
```

#### **Get API Keys**
```bash
# From Supabase Dashboard: Settings > API
# Copy these values:
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
```

---

### **2. AWS Setup**

#### **Configure AWS CLI**
```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

#### **Create ECR Repositories**
```bash
# Create repository for backend
aws ecr create-repository \
    --repository-name grammy-engine-backend \
    --region us-east-1

# Create repository for workers
aws ecr create-repository \
    --repository-name grammy-engine-workers \
    --region us-east-1

# Save repository URIs
export BACKEND_REPO_URI=$(aws ecr describe-repositories \
    --repository-names grammy-engine-backend \
    --query 'repositories[0].repositoryUri' \
    --output text)

export WORKERS_REPO_URI=$(aws ecr describe-repositories \
    --repository-names grammy-engine-workers \
    --query 'repositories[0].repositoryUri' \
    --output text)
```

#### **Create ECS Cluster**
```bash
# Create ECS cluster
aws ecs create-cluster \
    --cluster-name grammy-engine-cluster \
    --region us-east-1

# Create task execution role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://task-execution-role.json

# Attach policies
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

#### **Create Redis ElastiCache**
```bash
# Create subnet group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name grammy-redis-subnet \
    --cache-subnet-group-description "Grammy Engine Redis" \
    --subnet-ids subnet-xxxxx subnet-yyyyy

# Create Redis cluster
aws elasticache create-replication-group \
    --replication-group-id grammy-redis \
    --replication-group-description "Grammy Engine Redis" \
    --engine redis \
    --cache-node-type cache.t3.micro \
    --num-cache-clusters 2 \
    --automatic-failover-enabled

# Get Redis endpoint
aws elasticache describe-replication-groups \
    --replication-group-id grammy-redis \
    --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address'
```

---

### **3. Build & Push Docker Images**

#### **Backend Image**
```bash
# Navigate to backend directory
cd backend

# Build image
docker build -t grammy-engine-backend:latest .

# Tag for ECR
docker tag grammy-engine-backend:latest $BACKEND_REPO_URI:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $BACKEND_REPO_URI

# Push to ECR
docker push $BACKEND_REPO_URI:latest
```

#### **Workers Image**
```bash
# Build workers image (same Dockerfile as backend)
docker build -t grammy-engine-workers:latest .

# Tag for ECR
docker tag grammy-engine-workers:latest $WORKERS_REPO_URI:latest

# Push to ECR
docker push $WORKERS_REPO_URI:latest
```

---

### **4. ECS Task Definitions**

#### **Backend Task Definition**
Create `backend-task-def.json`:
```json
{
  "family": "grammy-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_BACKEND_REPO_URI:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "SUPABASE_URL", "value": "YOUR_SUPABASE_URL"},
        {"name": "REDIS_URL", "value": "redis://YOUR_REDIS_ENDPOINT:6379"}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:openai-api-key"
        },
        {
          "name": "SUPABASE_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:supabase-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/grammy-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition \
    --cli-input-json file://backend-task-def.json
```

#### **Workers Task Definition**
Create `workers-task-def.json`:
```json
{
  "family": "grammy-workers",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "generation-worker",
      "image": "YOUR_WORKERS_REPO_URI:latest",
      "command": ["celery", "-A", "workers.celery_app", "worker", "-Q", "generation", "-c", "2"],
      "environment": [
        {"name": "REDIS_URL", "value": "redis://YOUR_REDIS_ENDPOINT:6379"}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/grammy-workers",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "generation"
        }
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition \
    --cli-input-json file://workers-task-def.json
```

---

### **5. Create ECS Services**

#### **Backend Service with Load Balancer**
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name grammy-alb \
    --subnets subnet-xxxxx subnet-yyyyy \
    --security-groups sg-xxxxx \
    --scheme internet-facing

# Create Target Group
aws elbv2 create-target-group \
    --name grammy-backend-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-xxxxx \
    --target-type ip \
    --health-check-path /health

# Create Listener
aws elbv2 create-listener \
    --load-balancer-arn YOUR_ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=YOUR_TG_ARN

# Create ECS Service
aws ecs create-service \
    --cluster grammy-engine-cluster \
    --service-name backend \
    --task-definition grammy-backend \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=YOUR_TG_ARN,containerName=backend,containerPort=8000
```

#### **Workers Service**
```bash
# Create workers service (no load balancer needed)
aws ecs create-service \
    --cluster grammy-engine-cluster \
    --service-name workers \
    --task-definition grammy-workers \
    --desired-count 3 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

---

### **6. Frontend Deployment (Vercel)**

#### **Install & Configure**
```bash
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://api.grammyengine.com

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Enter: YOUR_SUPABASE_URL

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Enter: YOUR_SUPABASE_ANON_KEY
```

#### **Configure Custom Domain**
```bash
# Add domain in Vercel dashboard or via CLI
vercel domains add grammyengine.com
vercel domains add www.grammyengine.com

# Set up DNS records (A or CNAME)
# Point to Vercel's IP: 76.76.21.21
```

---

## 🔐 Secrets Management

### **AWS Secrets Manager**
```bash
# Store OpenAI API Key
aws secretsmanager create-secret \
    --name openai-api-key \
    --secret-string "sk-YOUR_OPENAI_KEY"

# Store Supabase Key
aws secretsmanager create-secret \
    --name supabase-key \
    --secret-string "YOUR_SUPABASE_SERVICE_ROLE_KEY"

# Store JWT Secret
aws secretsmanager create-secret \
    --name jwt-secret-key \
    --secret-string "$(openssl rand -hex 32)"
```

---

## 📊 Monitoring Setup

### **CloudWatch Alarms**
```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name grammy-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# Error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name grammy-high-errors \
    --alarm-description "Alert on high error rate" \
    --metric-name 5XXError \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 60 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

### **Sentry Integration**
```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Add to main.py
import sentry_sdk
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    environment="production",
    traces_sample_rate=0.1
)
```

---

## 🔄 CI/CD with GitHub Actions

### **GitHub Secrets**
Add these secrets to your repository (Settings > Secrets):
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
ECR_BACKEND_REPOSITORY
ECR_WORKERS_REPOSITORY
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
```

### **Workflow File** (`.github/workflows/deploy.yml`)
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push backend image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ secrets.ECR_BACKEND_REPOSITORY }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster grammy-engine-cluster \
            --service backend \
            --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./frontend
```

---

## ✅ Post-Deployment Checklist

### **1. Health Checks**
```bash
# Check backend health
curl https://api.grammyengine.com/health

# Check frontend
curl https://grammyengine.com

# Check Celery workers
# Visit: https://flower.grammyengine.com
```

### **2. Database Verification**
```sql
-- Connect to Supabase via psql or dashboard
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM tracks;
```

### **3. Load Testing**
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=https://api.grammyengine.com
```

### **4. Security Scan**
```bash
# Run OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://grammyengine.com
```

---

## 🐛 Troubleshooting

### **Common Issues**

**Issue:** ECS task fails to start
```bash
# Check CloudWatch logs
aws logs tail /ecs/grammy-backend --follow

# Describe task
aws ecs describe-tasks \
    --cluster grammy-engine-cluster \
    --tasks TASK_ARN
```

**Issue:** Celery workers not processing tasks
```bash
# Check Redis connection
redis-cli -h YOUR_REDIS_ENDPOINT ping

# Check Celery logs
aws logs tail /ecs/grammy-workers --follow

# Inspect Flower dashboard
# Visit: http://YOUR_ALB_DNS:5555
```

**Issue:** High latency
```bash
# Check ALB metrics
aws elbv2 describe-target-health \
    --target-group-arn YOUR_TG_ARN

# Scale up services
aws ecs update-service \
    --cluster grammy-engine-cluster \
    --service backend \
    --desired-count 5
```

---

## 💰 Cost Optimization

### **Estimated Monthly Costs**

| Service | Configuration | Cost |
|---------|--------------|------|
| **ECS Fargate** | 2 backend tasks (1 vCPU, 2GB) | $60 |
| **ECS Fargate** | 3 worker tasks (2 vCPU, 4GB) | $270 |
| **ElastiCache Redis** | cache.t3.micro x2 | $25 |
| **ALB** | 1 load balancer | $20 |
| **Supabase** | Pro Plan | $25 |
| **Vercel** | Pro Plan | $20 |
| **CloudWatch** | Logs + Metrics | $15 |
| **OpenAI API** | Variable (GPT-4) | $500-2000 |
| **Data Transfer** | 1TB egress | $90 |
| **Total** | | **~$1,525/mo** |

### **Cost Reduction Tips**
1. Use Spot instances for workers (50% savings)
2. Enable auto-scaling (scale down at night)
3. Cache OpenAI responses (reduce API calls)
4. Use CloudFront CDN (reduce ALB traffic)
5. Compress audio files (reduce storage)

---

## 📚 Additional Resources

- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Deployment Docs](https://vercel.com/docs/deployments)
- [Celery Production Checklist](https://docs.celeryproject.org/en/stable/userguide/deployment.html)

---

**Last Updated:** 2025-01-20  
**Version:** 1.0.0  
**Support:** devops@grammyengine.com
