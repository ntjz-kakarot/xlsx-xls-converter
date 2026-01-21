# XLSX to XLS Converter

A simple web application to convert Excel 2007+ (.xlsx) files to legacy Excel (.xls) format. Designed for local deployment using Docker.

## Features

- Drag-and-drop interface for easy file uploads
- Converts .xlsx files to .xls format
- Validates file formats and handles errors gracefully
- Automatic file cleanup to prevent disk space issues
- Docker-based deployment for easy setup
- No authentication required (designed for local/internal use)

## XLS Format Limitations

The .xls format has the following limitations:
- Maximum 65,536 rows
- Maximum 256 columns
- Sheet names limited to 31 characters
- Images and charts are not supported

## Quick Start

### Option 1: Using Pre-built Image (Recommended for Remote Servers)

Pull and run the pre-built image from GitHub Container Registry:

```bash
# Pull the latest image
docker pull ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Run it
docker run -d -p 5000:5000 --name xlsx-converter \
  --restart unless-stopped \
  ghcr.io/YOUR-USERNAME/xlsx-xls-converter:latest

# Or use docker-compose
# Edit docker-compose.prod.yml with your GitHub username, then:
docker compose -f docker-compose.prod.yml up -d
```

Access at: `http://localhost:5000` or `http://YOUR-SERVER-IP:5000`

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide with GitHub Container Registry.**

### Option 2: Build Locally

Build and run from source:

```bash
docker compose up -d
```

Access the application at `http://localhost:5000`

View logs:
```bash
docker compose logs -f
```

Stop the application:
```bash
docker compose down
```

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.11 or higher
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
flask run --host=0.0.0.0 --port=5000
```

Or for production:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. Access the application at `http://localhost:5000`

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `MAX_FILE_SIZE_MB` | Maximum upload file size in MB | `10` |
| `CLEANUP_INTERVAL_MINUTES` | How often to run cleanup job | `30` |
| `CLEANUP_AGE_MINUTES` | Delete files older than this | `60` |
| `UPLOAD_FOLDER` | Path for temporary uploads | `./uploads` |
| `CONVERTED_FOLDER` | Path for converted files | `./converted` |

### Example with Custom Configuration

```bash
docker-compose up -d
```

Or edit `docker-compose.yml` to change the environment variables:
```yaml
environment:
  - MAX_FILE_SIZE_MB=20
  - CLEANUP_AGE_MINUTES=120
```

## Usage

1. Open the application in your web browser
2. Drag and drop a .xlsx file onto the upload area, or click to browse
3. Wait for the conversion to complete
4. Download will start automatically
5. Click "Convert Another File" to convert more files

## Project Structure

```
.
├── app.py                      # Main Flask application
├── converter.py                # Conversion logic
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Client-side logic
├── uploads/                    # Temporary upload directory
├── converted/                  # Temporary converted files
├── convert_xlsx_to_xls.py     # Original batch conversion script
└── verify_conversion.py       # Verification script
```

## API Endpoints

### `GET /`
Serves the main web interface.

### `POST /upload`
Handles file upload and conversion.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File with key `file`

**Response:**
```json
{
  "success": true,
  "download_url": "/download/filename.xls",
  "filename": "filename.xls"
}
```

### `GET /download/<filename>`
Downloads the converted file and triggers cleanup.

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Troubleshooting

### Docker build fails
```bash
docker-compose build --no-cache
```

### Permission issues
Make sure the upload and converted directories are writable:
```bash
chmod 755 uploads converted
```

### Port 5000 already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Large file conversions fail
Increase the timeout in `Dockerfile`:
```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--timeout", "300"]
```

### Files not being cleaned up
Check the logs:
```bash
docker-compose logs -f
```

Adjust cleanup settings in `docker-compose.yml`.

## Security Notes

This application is designed for local/internal use:
- No authentication is implemented
- Files are stored temporarily and cleaned up automatically
- Runs in a Docker container with a non-root user
- File validation is performed on upload
- Path traversal attacks are prevented

For production deployment on public networks, consider adding:
- Authentication (basic auth, OAuth, etc.)
- HTTPS/TLS encryption
- Rate limiting
- Firewall rules

## Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest

# Run tests (if test files are created)
pytest
```

### Modifying the UI
- HTML: Edit `templates/index.html`
- CSS: Edit `static/css/style.css`
- JavaScript: Edit `static/js/app.js`

Changes will be reflected after restarting the application.

### Modifying Conversion Logic
Edit `converter.py` and restart the application.

## License

This project is provided as-is for internal use.

## Original Scripts

The original batch conversion scripts are preserved:
- `convert_xlsx_to_xls.py` - Batch converts all .xlsx files in current directory
- `verify_conversion.py` - Verifies conversion accuracy

These can still be used standalone if needed.
