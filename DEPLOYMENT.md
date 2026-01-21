# Deployment Guide - GitHub Container Registry

This guide explains how to deploy the XLSX to XLS converter on your remote server using the pre-built Docker image from GitHub Container Registry.

## Prerequisites

- Docker installed on remote server
- Access to GitHub Container Registry (ghcr.io)

## Step 1: Setup on GitHub

### 1.1 Push Code to GitHub

```bash
cd ~/git/xlsx-xls-converter

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/xlsx-xls-converter.git
git branch -M main
git push -u origin main
```

### 1.2 Enable GitHub Actions

The workflow will automatically run on push to `main` branch. Check the "Actions" tab on GitHub to see the build progress.

### 1.3 Make Repository/Package Public or Setup Authentication

**Option A: Make Package Public (Easier)**
1. Go to your GitHub repository
2. Click on "Packages" on the right sidebar
3. Click on the `xlsx-xls-converter` package
4. Go to "Package settings" (bottom right)
5. Scroll down to "Danger Zone"
6. Click "Change visibility" → "Public"

**Option B: Use Authentication (Private Package)**
- You'll need a Personal Access Token (PAT) with `read:packages` permission
- See "Authentication" section below

## Step 2: Deploy on Remote Server

### 2.1 Install Docker (if not installed)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### 2.2 Pull and Run (Public Package)

```bash
# Pull the latest image
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Run the container
docker run -d \
  --name xlsx-converter \
  -p 5000:5000 \
  -e MAX_FILE_SIZE_MB=10 \
  -e CLEANUP_INTERVAL_MINUTES=30 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Check if it's running
docker ps
docker logs xlsx-converter

# Access at: http://YOUR-SERVER-IP:5000
```

### 2.3 Using Docker Compose (Recommended)

Create `docker-compose.prod.yml` on your remote server:

```yaml
services:
  web:
    image: ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest
    container_name: xlsx-xls-converter
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MAX_FILE_SIZE_MB=10
      - CLEANUP_INTERVAL_MINUTES=30
      - CLEANUP_AGE_MINUTES=60
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

Then run:
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Step 3: Authentication (For Private Packages)

### 3.1 Create Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `read:packages` permission
3. Copy the token

### 3.2 Login to GitHub Container Registry

On your remote server:

```bash
# Login with your PAT
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR-USERNAME --password-stdin

# Now you can pull private images
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest
```

### 3.3 Docker Compose with Authentication

Create `.env` file:
```bash
GITHUB_USERNAME=your-username
GITHUB_TOKEN=your-token
```

Then login before running:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Step 4: Updates and Maintenance

### 4.1 Update to Latest Version

```bash
# Pull latest image
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Restart container
docker stop xlsx-converter
docker rm xlsx-converter
docker run -d \
  --name xlsx-converter \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Or with docker-compose
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 4.2 Rollback to Specific Version

```bash
# List available tags
# Visit: https://github.com/YOUR-USERNAME/xlsx-xls-converter/pkgs/container/xlsx-xls-converter

# Pull specific version
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:v1.0.0

# Run it
docker run -d \
  --name xlsx-converter \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:v1.0.0
```

### 4.3 Create Versioned Releases

```bash
# Tag a release locally
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically build and push:
# - ghcr.io/YOUR-USERNAME/xlsx-xls-converter:v1.0.0
# - ghcr.io/YOUR-USERNAME/xlsx-xls-converter:1.0
# - ghcr.io/YOUR-USERNAME/xlsx-xls-converter:1
# - ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest
```

## Step 5: Production Configuration

### 5.1 Use Port 80 (HTTP)

Edit `docker-compose.prod.yml`:
```yaml
ports:
  - "80:5000"
```

### 5.2 Setup Systemd Service (Auto-start on boot)

Create `/etc/systemd/system/xlsx-converter.service`:

```ini
[Unit]
Description=XLSX to XLS Converter
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/xlsx-converter
ExecStartPre=/usr/bin/docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable xlsx-converter
sudo systemctl start xlsx-converter
sudo systemctl status xlsx-converter
```

### 5.3 Automated Updates Script

Create `update.sh` on remote server:

```bash
#!/bin/bash
set -e

echo "Pulling latest image..."
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

echo "Stopping current container..."
docker compose -f docker-compose.prod.yml down

echo "Starting new container..."
docker compose -f docker-compose.prod.yml up -d

echo "Waiting for health check..."
sleep 10

if docker compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
    echo "✓ Update successful!"
    docker image prune -f
else
    echo "✗ Health check failed!"
    exit 1
fi
```

```bash
chmod +x update.sh
./update.sh
```

### 5.4 Setup Cron for Auto-updates (Optional)

```bash
# Edit crontab
crontab -e

# Add line to update every day at 3 AM
0 3 * * * /opt/xlsx-converter/update.sh >> /var/log/xlsx-converter-update.log 2>&1
```

## Step 6: Monitoring

### 6.1 Check Health

```bash
curl http://localhost:5000/health
```

### 6.2 View Logs

```bash
docker logs xlsx-converter -f

# Or with docker-compose
docker compose -f docker-compose.prod.yml logs -f
```

### 6.3 Container Stats

```bash
docker stats xlsx-converter
```

## Troubleshooting

### Image Pull Fails (403 Forbidden)

**Problem:** Cannot pull private package
**Solution:**
1. Make package public (see Step 1.3)
2. Or authenticate with PAT (see Step 3)

### Port Already in Use

**Problem:** Port 5000 is already taken
**Solution:** Change port in docker-compose.prod.yml:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Container Stops Immediately

**Problem:** Container exits right after starting
**Solution:**
```bash
docker logs xlsx-converter
# Check the error and fix configuration
```

### Cannot Access from Other Machines

**Problem:** Can access locally but not from other machines
**Solution:**
```bash
# Check firewall
sudo ufw allow 5000/tcp
sudo ufw reload

# Or for firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Complete Deployment Example

```bash
# On Remote Server

# 1. Login to GitHub Container Registry (if private)
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 2. Create docker-compose.prod.yml (see Step 2.3)
nano docker-compose.prod.yml

# 3. Start the service
docker compose -f docker-compose.prod.yml up -d

# 4. Verify it's running
docker ps
curl http://localhost:5000/health

# 5. Access from browser
# http://YOUR-SERVER-IP:5000

# 6. Check logs if needed
docker compose -f docker-compose.prod.yml logs -f
```

## Security Checklist

- [ ] Use strong GitHub token with minimal permissions
- [ ] Don't commit tokens to git
- [ ] Use firewall to restrict access if needed
- [ ] Keep Docker and system updated
- [ ] Monitor disk usage (uploads/converted folders)
- [ ] Set appropriate MAX_FILE_SIZE_MB
- [ ] Use HTTPS with reverse proxy for public access
- [ ] Consider adding authentication if needed

## Support

For issues:
1. Check GitHub Actions build logs
2. Check container logs: `docker logs xlsx-converter`
3. Check health endpoint: `curl http://localhost:5000/health`
4. Verify network/firewall settings
