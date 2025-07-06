# Docker Deployment Guide

This guide covers how to deploy the Flashcards API with LangChain Agent Support using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- 10GB free disk space

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd flashcards-api
cp env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
# Required: Set your API key
G4F_API_KEY=your-actual-api-key-here

# Optional: Configure default model and provider
G4F_MODEL=gpt-4o
G4F_PROVIDER=openai
```

### 3. Build and Run

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f flashcards-api
```

### 4. Verify Deployment

```bash
# Check if the service is running
curl http://localhost:1337/v1

# Test the agent API
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "Hello, how are you?",
    "config": {
      "agent_type": "zero-shot-react-description",
      "tools": []
    }
  }'
```

## Docker Commands

### Basic Operations

```bash
# Build the image
docker build -t flashcards-api .

# Run the container
docker run -d \
  --name flashcards-api \
  -p 1337:1337 \
  -e G4F_API_KEY=your-api-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/cookies:/app/cookies \
  -v $(pwd)/media:/app/media \
  flashcards-api

# Stop the container
docker stop flashcards-api

# Remove the container
docker rm flashcards-api

# View logs
docker logs -f flashcards-api

# Execute commands in the container
docker exec -it flashcards-api bash
```

### Docker Compose Operations

```bash
# Start all services
docker-compose up -d

# Start with specific profiles
docker-compose --profile cache up -d  # With Redis
docker-compose --profile proxy up -d  # With Nginx proxy

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f

# Scale the service
docker-compose up -d --scale flashcards-api=3
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `G4F_API_KEY` | `your-api-key-here` | API key for authentication |
| `G4F_MODEL` | `gpt-4o` | Default model to use |
| `G4F_PROVIDER` | `openai` | Default provider |
| `G4F_MEDIA_PROVIDER` | `openai` | Default media provider |
| `G4F_PROXY` | `` | Proxy configuration |
| `DEBUG` | `false` | Enable debug mode |
| `GUI` | `false` | Enable GUI mode |
| `DEMO` | `false` | Enable demo mode |
| `TIMEOUT` | `600` | Request timeout in seconds |
| `IGNORE_COOKIES` | `false` | Ignore cookie files |
| `IGNORED_PROVIDERS` | `` | Comma-separated list of providers to ignore |

### Volume Mounts

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./data` | `/app/data` | Persistent data storage |
| `./logs` | `/app/logs` | Application logs |
| `./cookies` | `/app/cookies` | Cookie files for authentication |
| `./media` | `/app/media` | Generated media files |
| `./config` | `/app/config` | Custom configuration files |

## Production Deployment

### 1. Security Considerations

```bash
# Use a strong API key
G4F_API_KEY=your-very-secure-api-key

# Enable HTTPS with Nginx proxy
docker-compose --profile proxy up -d

# Set resource limits
docker-compose up -d --scale flashcards-api=2
```

### 2. Monitoring and Logging

```bash
# View application logs
docker-compose logs -f flashcards-api

# Monitor resource usage
docker stats flashcards-api

# Check health status
curl http://localhost:1337/v1
```

### 3. Backup and Recovery

```bash
# Backup data volumes
docker run --rm -v flashcards-api_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restore data volumes
docker run --rm -v flashcards-api_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

## Advanced Configuration

### Custom Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream flashcards-api {
        server flashcards-api:1337;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://flashcards-api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### SSL/TLS Configuration

```bash
# Generate SSL certificates
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Start with SSL
docker-compose --profile proxy up -d
```

### Redis Caching

```bash
# Start with Redis cache
docker-compose --profile cache up -d

# Configure Redis connection in your application
REDIS_URL=redis://redis:6379
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs flashcards-api
   
   # Check resource usage
   docker stats
   ```

2. **API key issues**
   ```bash
   # Verify API key is set
   docker exec flashcards-api env | grep G4F_API_KEY
   
   # Test API endpoint
   curl -H "Authorization: Bearer your-api-key" http://localhost:1337/v1
   ```

3. **Port conflicts**
   ```bash
   # Check if port is in use
   netstat -tulpn | grep 1337
   
   # Change port in docker-compose.yml
   ports:
     - "1338:1337"  # Use port 1338 instead
   ```

4. **Permission issues**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 data logs cookies media
   ```

### Performance Optimization

```bash
# Increase memory limit
docker-compose up -d --scale flashcards-api=2

# Use Redis for caching
docker-compose --profile cache up -d

# Monitor performance
docker stats flashcards-api
```

### Health Checks

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test health endpoint
curl -f http://localhost:1337/v1 || echo "Service is down"
```

## Development with Docker

### Development Mode

```bash
# Run with debug mode
docker-compose up -d -e DEBUG=true

# Mount source code for development
docker run -d \
  --name flashcards-api-dev \
  -p 1337:1337 \
  -v $(pwd):/app \
  -e DEBUG=true \
  flashcards-api
```

### Testing

```bash
# Run tests in container
docker exec flashcards-api python test_agent_api.py

# Run with test environment
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Scaling

### Horizontal Scaling

```bash
# Scale to multiple instances
docker-compose up -d --scale flashcards-api=3

# Use load balancer
docker-compose --profile proxy up -d
```

### Vertical Scaling

```bash
# Increase resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Cleanup

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

## Support

For issues and questions:
- Check the logs: `docker-compose logs flashcards-api`
- Review the troubleshooting section above
- Open an issue on GitHub with Docker logs attached 