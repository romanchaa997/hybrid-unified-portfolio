# 🚀 Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/romanchaa997/hybrid-unified-portfolio.git
cd hybrid-unified-portfolio

# 2. Copy environment template
cp .env.example .env

# 3. Set up environment variables
sed -i 's/${DB_USER}/postgres/g; s/${DB_PASSWORD}/securepass123/g; s/${REDIS_PASSWORD}/redispass456/g' .env

# 4. Start all services
docker-compose up -d

# 5. Check status
docker-compose ps
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Ingest GitHub Profile
```bash
curl -X POST http://localhost:8000/api/v1/portfolio/ingest?username=romanchaa997
```

### Hybrid Search
```bash
curl -X POST http://localhost:8000/api/v1/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI engineer with Python",
    "top_k": 10,
    "weights": {
      "vector": 0.4,
      "structured": 0.3,
      "projects": 0.2,
      "experience": 0.1
    }
  }'
```

### Get Portfolio
```bash
curl http://localhost:8000/api/v1/portfolio/romanchaa997
```

## Docker Commands

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis

# Stop all services
docker-compose down

# Remove volumes (WARNING: data loss)
docker-compose down -v

# Rebuild image
docker-compose build --no-cache

# Execute command in container
docker-compose exec api python -m pytest
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|----------|
| API | http://localhost:8000 | FastAPI application |
| Docs | http://localhost:8000/api/docs | Swagger UI |
| ReDoc | http://localhost:8000/api/redoc | API documentation |
| Metrics | http://localhost:8000/metrics | Prometheus metrics |
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

## Production Deployment

### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker build -t hybrid-portfolio .
docker tag hybrid-portfolio:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/hybrid-portfolio:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/hybrid-portfolio:latest
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n hybrid-portfolio
kubectl logs -f deployment/hybrid-portfolio-api -n hybrid-portfolio

# Port forward
kubectl port-forward svc/hybrid-portfolio-api 8000:8000 -n hybrid-portfolio
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy hybrid-portfolio \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://...
```

## Monitoring

### Prometheus

1. Open http://localhost:9090
2. Query metrics:
   - `api_requests_total` — Total API requests
   - `api_request_duration_seconds` — Request duration
   - `search_requests_total` — Search requests
   - `embeddings_created_total` — Embeddings created

### Grafana

1. Open http://localhost:3000
2. Login: admin / admin
3. Import dashboards from `grafana/dashboards/`

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check PostgreSQL health
docker-compose exec postgres pg_isready -U postgres

# Reset PostgreSQL
docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS hybrid_portfolio; CREATE DATABASE hybrid_portfolio;"
```

### Redis Connection Error
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### API not responding
```bash
# Check API logs
docker-compose logs -f api

# Restart API
docker-compose restart api
```

## Scaling

### Horizontal Scaling (Kubernetes)
```bash
kubectl scale deployment hybrid-portfolio-api --replicas=5 -n hybrid-portfolio
```

### Vertical Scaling (Resources)
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Performance Tuning

### PostgreSQL
- Enable connection pooling (PgBouncer)
- Index key columns: username, created_at
- Vacuum and analyze regularly

### Redis
- Enable persistence (RDB snapshots)
- Set appropriate max-memory policy
- Monitor memory usage

### API
- Increase worker count (--workers=8)
- Enable async endpoints
- Implement caching headers

## Security Checklist

- [ ] Rotate database passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] DDoS protection (CloudFlare/AWS Shield)
- [ ] WAF rules configured
- [ ] Secrets in AWS Secrets Manager or HashiCorp Vault
