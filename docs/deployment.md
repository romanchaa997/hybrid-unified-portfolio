# Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

## Development Setup

### Using Docker Compose
```bash
# Clone repository
git clone https://github.com/romanchaa997/hybrid-unified-portfolio.git
cd hybrid-unified-portfolio

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Initialize database
docker-compose exec app python scripts/init_db.py

# Run tests
docker-compose exec app pytest
```

### Local Setup (without Docker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Initialize database
python scripts/init_db.py

# Run application
uvicorn main:app --reload
```

## Production Deployment

### AWS ECS Deployment

```bash
# Build Docker image
docker build -t portfolio-system:latest .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker tag portfolio-system:latest YOUR_ECR_URI/portfolio-system:latest
docker push YOUR_ECR_URI/portfolio-system:latest

# Deploy to ECS
aws ecs update-service --cluster production --service portfolio-api --force-new-deployment
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace production

# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=postgres-user=dbuser \
  --from-literal=postgres-password=dbpass \
  -n production

# Deploy
kubectl apply -f k8s/deployment.yaml -n production
kubectl apply -f k8s/service.yaml -n production
```

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/portfolio
REDIS_URL=redis://localhost:6379

# API
API_HOST=0.0.0.0
API_PORT=8000

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
VECTOR_DB_TYPE=pinecone  # or milvus, weaviate
PINCONE_API_KEY=xxx
PINCONE_ENVIRONMENT=us-west1-gcp

# GitHub
GITHUB_TOKEN=ghp_xxx
GITHUB_API_URL=https://api.github.com

# Security
JWT_SECRET=your-secret-key
API_KEY_SALT=your-salt-key
```

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring

### Prometheus Metrics
Metrics available at: `http://localhost:8000/metrics`

### Grafana Dashboards
```bash
# Access Grafana
http://localhost:3000
# Default: admin/admin
```

### Logging
Logs are written to:
- `logs/app.log` - Application logs
- `logs/error.log` - Error logs
- `logs/access.log` - Access logs

## Health Checks

```bash
# Liveness probe
GET /health/live

# Readiness probe
GET /health/ready
```

## Scaling

### Horizontal Scaling
```bash
# Scale API replicas
kubectl scale deployment portfolio-api --replicas=5 -n production
```

### Database Connection Pooling
Configured via `DATABASE_POOL_SIZE` and `DATABASE_POOL_TIMEOUT` in `.env`

## Security Best Practices

1. Use HTTPS in production
2. Enable rate limiting
3. Implement CORS policies
4. Use environment variables for secrets
5. Enable API authentication (JWT)
6. Regular security audits

## Backup & Recovery

### Database Backup
```bash
pg_dump postgresql://user:pass@localhost/portfolio > backup.sql
```

### Vector Database Backup
```bash
# Pinecone: Automatic backups
# Milvus: Use collections export
milvus_cli collections export --collection_name portfolio_embeddings
```

## Troubleshooting

### Connection Issues
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Performance Tuning
- Increase PostgreSQL `shared_buffers`
- Tune Redis `maxmemory` policy
- Adjust embedding batch size
- Enable query caching

## Support
For deployment issues, contact: devops@portfolio-system.com
