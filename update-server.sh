#!/bin/bash
# Update script for remote server
# Place this on your remote server and run it to update to the latest version
#
# Usage:
#   1. Copy this script to your remote server
#   2. Edit the IMAGE_NAME variable below with your GitHub username
#   3. Make it executable: chmod +x update-server.sh
#   4. Run: ./update-server.sh

set -e

# Configuration
IMAGE_NAME="ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest"
CONTAINER_NAME="xlsx-converter"
PORT="5000:5000"

echo "========================================="
echo "XLSX to XLS Converter - Update Script"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

echo "[1/6] Pulling latest image..."
docker pull "$IMAGE_NAME"

echo ""
echo "[2/6] Checking if container exists..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[3/6] Stopping existing container..."
    docker stop "$CONTAINER_NAME" || true

    echo "[4/6] Removing old container..."
    docker rm "$CONTAINER_NAME" || true
else
    echo "[3/6] No existing container found"
    echo "[4/6] Skipping removal"
fi

echo ""
echo "[5/6] Starting new container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT" \
  -e FLASK_ENV=production \
  -e MAX_FILE_SIZE_MB=10 \
  --restart unless-stopped \
  "$IMAGE_NAME"

echo ""
echo "[6/6] Waiting for health check..."
sleep 5

# Check if container is running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "========================================="
    echo "✓ Update successful!"
    echo "========================================="
    echo ""
    echo "Container is running:"
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Health check:"
    curl -s http://localhost:5000/health | grep -q "healthy" && echo "✓ Service is healthy" || echo "✗ Service health check failed"
    echo ""
    echo "Access at: http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "View logs: docker logs ${CONTAINER_NAME} -f"
    echo ""

    # Cleanup old images
    echo "Cleaning up old images..."
    docker image prune -f

else
    echo ""
    echo "========================================="
    echo "✗ Update failed!"
    echo "========================================="
    echo ""
    echo "Container failed to start. Check logs:"
    echo "docker logs ${CONTAINER_NAME}"
    exit 1
fi
