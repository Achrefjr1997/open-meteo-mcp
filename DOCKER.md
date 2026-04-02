# Open-Meteo MCP Server - Docker Documentation

Complete guide for running the Open-Meteo MCP Server with Docker.

---

## 🐳 Quick Start

### Build and Run (Production - stdio)

```bash
# Build the image
docker build -t open-meteo-mcp .

# Run with stdio transport (for MCP clients)
docker run -it --rm open-meteo-mcp
```

### Run with Docker Compose

```bash
# Production (stdio transport)
docker compose up open-meteo-mcp

# SSE mode (HTTP access on port 8000)
docker compose up open-meteo-sse

# Run tests
docker compose --profile test up open-meteo-test
```

---

## 📋 Docker Services

| Service | Transport | Port | Use Case |
|---------|-----------|------|----------|
| `open-meteo-mcp` | stdio | None | MCP clients (Claude Desktop, Cursor) |
| `open-meteo-sse` | SSE | 8000 | Remote HTTP access |
| `open-meteo-dev` | stdio | None | Development with hot reload |
| `open-meteo-test` | stdio | None | Run test suite |

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPEN_METEO_API_KEY` | API key for commercial use | None |
| `OPEN_METEO_TIMEOUT` | Request timeout (seconds) | 30.0 |
| `OPEN_METEO_TIMEZONE` | Default timezone | GMT |
| `OPEN_METEO_RATE_LIMIT` | Rate limit delay (seconds) | 0.1 |

### Using Environment Variables

**With docker run:**
```bash
docker run -e OPEN_METEO_API_KEY=your_key \
           -e OPEN_METEO_TIMEZONE=America/New_York \
           open-meteo-mcp
```

**With docker compose:**
```bash
# Create .env file
echo "OPEN_METEO_API_KEY=your_key" >> .env
echo "OPEN_METEO_TIMEZONE=America/New_York" >> .env

# Start with environment
docker compose up open-meteo-mcp
```

**With docker compose override:**
```yaml
# docker-compose.override.yml
services:
  open-meteo-mcp:
    environment:
      - OPEN_METEO_API_KEY=your_key
      - OPEN_METEO_TIMEZONE=America/New_York
```

---

## 🚀 Usage Examples

### 1. MCP Client Configuration (Claude Desktop)

**Step 1:** Run the container
```bash
docker run -d --name open-meteo-mcp open-meteo-mcp
```

**Step 2:** Configure Claude Desktop
```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "open-meteo-mcp"],
      "description": "Weather data from Open-Meteo API"
    }
  }
}
```

### 2. Remote SSE Access

**Start SSE server:**
```bash
docker compose up -d open-meteo-sse
```

**Access endpoints:**
- Health: `http://localhost:8000/health`
- SSE: `http://localhost:8000/sse`
- Messages: `http://localhost:8000/messages`

**Configure remote MCP client:**
```json
{
  "mcpServers": {
    "open-meteo": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

### 3. Run Tests in Docker

```bash
# Run all tests
docker compose --profile test up open-meteo-test

# Or directly
docker run --rm open-meteo-mcp python -m pytest tests/ -v
```

### 4. Development Mode

```bash
# Run with volume mounting for live code changes
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/tests:/app/tests \
  open-meteo-mcp-dev
```

---

## 🏗️ Docker Build Options

### Multi-Stage Build Targets

| Target | Purpose | Size |
|--------|---------|------|
| `production` | Production deployment | ~150MB |
| `development` | Development with tests | ~250MB |
| `builder` | Build stage (intermediate) | N/A |

### Build for Specific Target

```bash
# Production build
docker build --target production -t open-meteo-mcp .

# Development build (includes tests)
docker build --target development -t open-meteo-mcp-dev .
```

### Build Arguments

```bash
docker build \
  --build-arg OPEN_METEO_VERSION=0.1.0 \
  -t open-meteo-mcp .
```

---

## 🔒 Security

### Non-Root User

The production image runs as a non-root user (`appuser:appgroup`) for security:

```dockerfile
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser
USER appuser
```

### Health Checks

Built-in health checks monitor container health:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 📊 Resource Limits

### Docker Compose with Limits

```yaml
services:
  open-meteo-mcp:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Docker Run with Limits

```bash
docker run --rm \
  --cpus="0.5" \
  --memory="512m" \
  open-meteo-mcp
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs open-meteo-mcp

# Run interactively for debugging
docker run -it --rm open-meteo-mcp python -m src.server
```

### Connection Issues

```bash
# Check if container is running
docker ps

# Test health endpoint
curl http://localhost:8000/health

# Check network
docker network ls
docker network inspect bridge
```

### Permission Errors

```bash
# Fix volume permissions (Linux/Mac)
sudo chown -R 1000:1000 ./src ./tests

# Or run as root (not recommended for production)
docker run --user root open-meteo-mcp
```

---

## 🔄 Updating

### Rebuild After Code Changes

```bash
# Rebuild image
docker build -t open-meteo-mcp .

# Restart container
docker compose down
docker compose up -d open-meteo-mcp
```

### Pull Latest Base Image

```bash
docker pull python:3.11-slim
docker build --no-cache -t open-meteo-mcp .
```

---

## 📦 Registry Deployment

### Push to Docker Hub

```bash
# Tag image
docker tag open-meteo-mcp:latest yourusername/open-meteo-mcp:latest
docker tag open-meteo-mcp:latest yourusername/open-meteo-mcp:0.1.0

# Login
docker login

# Push
docker push yourusername/open-meteo-mcp:latest
docker push yourusername/open-meteo-mcp:0.1.0
```

### Push to GitHub Container Registry

```bash
# Tag for GHCR
docker tag open-meteo-mcp:latest ghcr.io/yourusername/open-meteo-mcp:latest

# Login
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin

# Push
docker push ghcr.io/yourusername/open-meteo-mcp:latest
```

---

## 🎯 Production Deployment

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-meteo-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: open-meteo-mcp
  template:
    metadata:
      labels:
        app: open-meteo-mcp
    spec:
      containers:
      - name: open-meteo-mcp
        image: yourusername/open-meteo-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPEN_METEO_API_KEY
          valueFrom:
            secretKeyRef:
              name: open-meteo-secrets
              key: api-key
        resources:
          limits:
            memory: "512Mi"
            cpu: "0.5"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
```

### Docker Swarm

```bash
# Deploy stack
docker stack deploy -c docker-compose.yml weather-mcp

# Scale service
docker service scale weather-mcp_open-meteo-sse=3
```

---

## 📝 Best Practices

1. **Use specific image tags** - Don't use `:latest` in production
2. **Limit resources** - Set CPU and memory limits
3. **Use secrets** - Store API keys in Docker secrets or environment files
4. **Enable health checks** - Monitor container health
5. **Run as non-root** - Security best practice
6. **Multi-stage builds** - Keep production images small
7. **Regular updates** - Keep base images updated

---

## 🔗 Related Files

- `Dockerfile` - Multi-stage Docker build
- `docker-compose.yml` - Service orchestration
- `.dockerignore` - Files excluded from build context
- `requirements.txt` - Python dependencies

---

**Happy Dockerizing! 🐳**
