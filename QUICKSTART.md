# Quick Start Guide

## For First-Time Setup

### 1. Push to GitHub

```bash
cd ~/git/xlsx-xls-converter

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create repository on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/xlsx-xls-converter.git
git branch -M main
git push -u origin main
```

### 2. Wait for Build

Go to your repository → Actions tab → Wait for the build to complete (2-3 minutes)

### 3. Make Package Public

1. Go to your repository on GitHub
2. Click "Packages" (right sidebar)
3. Click on `xlsx-xls-converter`
4. Package settings → Change visibility → Public

## Deploy on Remote Server

### Quick Commands (Copy-Paste)

```bash
# 1. Install Docker (if needed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in

# 2. Pull the image (replace YOUR-USERNAME)
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# 3. Run it
docker run -d \
  --name xlsx-converter \
  -p 5000:5000 \
  -e MAX_FILE_SIZE_MB=10 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# 4. Verify it's running
docker ps
curl http://localhost:5000/health

# 5. Check logs if needed
docker logs xlsx-converter -f
```

Access at: `http://YOUR-SERVER-IP:5000`

## Update to Latest Version

```bash
# Pull latest
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Stop and remove old container
docker stop xlsx-converter
docker rm xlsx-converter

# Start new one
docker run -d \
  --name xlsx-converter \
  -p 5000:5000 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Clean up old images
docker image prune -f
```

## Using Docker Compose (Alternative)

### 1. Create docker-compose.prod.yml on server

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
    restart: unless-stopped
```

### 2. Run

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 3. Update

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Cannot pull image (403 error)
Make sure package is public (see step 3 above)

### Port 5000 already in use
Change `-p 8080:5000` in the docker run command

### Cannot access from other machines
```bash
sudo ufw allow 5000/tcp
```

### Check if it's running
```bash
docker ps
docker logs xlsx-converter
curl http://localhost:5000/health
```

## Use Port 80 (HTTP)

```bash
docker run -d \
  --name xlsx-converter \
  -p 80:5000 \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest
```

Access at: `http://YOUR-SERVER-IP` (no port needed)

## Complete One-Liner for Remote Server

```bash
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest && docker stop xlsx-converter 2>/dev/null; docker rm xlsx-converter 2>/dev/null; docker run -d --name xlsx-converter -p 5000:5000 --restart unless-stopped ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest && docker ps | grep xlsx-converter
```
