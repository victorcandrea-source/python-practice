# Deployment & Operations Guide

## Production Deployment

This guide covers deploying the Task Management System to production environments.

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code coverage ≥ 80%: `pytest --cov=. --cov-report=term-missing`
- [ ] No PEP8 violations: Code reviewed for style compliance
- [ ] Environment variables validated against `.env.example`

### Docker Setup
- [ ] `Dockerfile` builds successfully: `docker build .`
- [ ] `docker-compose.yml` is valid: `docker-compose config`
- [ ] All volumes are properly defined
- [ ] Health checks configured

### Security
- [ ] Database password is strong (not "postgres")
- [ ] `.env` file is NOT committed to version control
- [ ] Database credentials are environment-specific
- [ ] HTTPS/TLS configured (if on public network)

## Deployment Steps

### Option 1: Docker Compose (Recommended)

```bash
# 1. Navigate to project directory
cd /Users/candreavictor/Practica/last_hw

# 2. Create production .env file
cat > .env << EOF
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_strong_password_here
DB_NAME=task_management
APP_PORT=8000
EOF

# 3. Build and start services
docker-compose up -d --build

# 4. Verify status
docker-compose ps

# 5. Check application health
curl http://localhost:8000/health

# 6. View logs
docker-compose logs -f app
docker-compose logs -f db
```

### Option 2: Kubernetes Deployment

For production Kubernetes deployment, create:

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-manager
  template:
    metadata:
      labels:
        app: task-manager
    spec:
      containers:
      - name: task-api
        image: task-management:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: postgres-service
        - name: DB_PORT
          value: "5432"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

## Running Tests

### Local Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Set up test database (PostgreSQL must be running)
export DB_NAME=test_task_management

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=. --cov-report=html tests/

# Run specific test class
pytest tests/test_api.py::TestCreateTask -v

# Run specific test
pytest tests/test_api.py::TestCreateTask::test_create_task_success -v
```

### Continuous Integration (GitHub Actions)

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_task_management
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pytest --cov=. tests/
```

## Monitoring & Health Checks

### Application Health
```bash
# Check if application is running
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "message": "Task Management System is running."}
```

### Database Health
```bash
# Check if database is accessible
docker-compose exec db pg_isready -U postgres
```

### View Real-time Logs
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# All services
docker-compose logs -f
```

### Monitor Container Resource Usage
```bash
docker stats
```

## Scaling & Performance

### Horizontal Scaling with Docker Compose

To run multiple app instances:
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 3
```

Or use Kubernetes with horizontal pod autoscaling.

### Database Performance Optimization

Current indexes:
```sql
CREATE INDEX idx_tasks_owner ON tasks(owner);
CREATE INDEX idx_tasks_status ON tasks(status);
```

For additional performance, consider:
```sql
-- Composite index for common filters
CREATE INDEX idx_tasks_owner_status ON tasks(owner, status);

-- Index on created_at for sorting
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Gunicorn Workers Configuration

Adjust in `Dockerfile`:
```bash
gunicorn --workers 8 --worker-class uvicorn.workers.UvicornWorker ...
```

Formula: workers = (2 × cpu_cores) + 1

## Backup & Recovery

### PostgreSQL Backup

```bash
# Backup database
docker-compose exec db pg_dump -U postgres task_management > backup.sql

# Backup volume
docker run --rm -v task_network_postgres_data:/data \
  -v $(pwd):/backup \
  busybox tar czf /backup/db_backup.tar.gz -C /data .
```

### Restore Database

```bash
# Restore from SQL dump
docker-compose exec -T db psql -U postgres < backup.sql

# Restore volume from backup
docker run --rm -v task_network_postgres_data:/data \
  -v $(pwd):/backup \
  busybox tar xzf /backup/db_backup.tar.gz -C /data
```

## Troubleshooting Deployment

### Application Won't Start
```bash
# Check logs
docker-compose logs app

# Verify database is healthy
docker-compose logs db

# Ensure ports are not in use
lsof -i :8000
```

### Database Connection Issues
```bash
# Check if database is running
docker-compose ps

# Verify environment variables
docker-compose config | grep DB_

# Test connection directly
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### High Memory Usage
```bash
# Check container memory
docker stats

# Reduce gunicorn workers in Dockerfile
CMD ["gunicorn", "--workers", "2", ...]

# Restart with new config
docker-compose restart app
```

### Database Lock/Performance Issues
```bash
# Check active queries
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity"

# Kill long-running queries
docker-compose exec db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '1 hour'"
```

## Rollback Procedures

### Rollback to Previous Image
```bash
# Stop current services
docker-compose down

# Keep volume with data
# docker-compose down -v  # Use only if you want to reset DB

# Rebuild with previous code
git checkout <previous-commit>
docker-compose build
docker-compose up -d
```

### Zero-Downtime Deployment
```bash
# Using docker-compose with multiple app instances
docker-compose up -d --scale app=3  # Run 3 instances
# Deploy new version to instances one at a time
# Remove old instances
docker-compose down
```

## Maintenance Tasks

### Regular Backups
Schedule daily backups:
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/task_manager"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T db pg_dump -U postgres task_management \
  > $BACKUP_DIR/backup_$TIMESTAMP.sql

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

### Database Maintenance
```bash
# Run vacuum to optimize database
docker-compose exec db psql -U postgres -c "VACUUM ANALYZE tasks"

# Check index health
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_user_indexes"
```

### Log Rotation
```bash
# Configure Docker logging driver in docker-compose.yml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
```

## Security Considerations

### Production Checklist
- [ ] Change default database password
- [ ] Use environment variables for all credentials
- [ ] Enable HTTPS/TLS
- [ ] Implement API rate limiting
- [ ] Set up request logging
- [ ] Configure CORS appropriately
- [ ] Regular security updates for Docker images
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)

### Network Security
```yaml
# docker-compose.yml
networks:
  task_network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_icc: "false"  # Disable inter-container communication if not needed
```

### Database Security
- Use strong, randomly generated passwords
- Restrict PostgreSQL to internal network only
- Enable PostgreSQL SSL for connections
- Regular security updates

## Monitoring Template

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'task-manager'
    static_configs:
      - targets: ['localhost:8000']
```

## Disaster Recovery Plan

1. **Identify**: Detect issue via monitoring/health checks
2. **Assess**: Check logs and database status
3. **Backup**: Create emergency backup
4. **Restore**: Restore from recent backup
5. **Verify**: Run tests and health checks
6. **Monitor**: Watch logs for 24 hours

---

**Last Updated:** March 30, 2026
