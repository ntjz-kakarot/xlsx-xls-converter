from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import os
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config import config
from converter import XLSXConverter, InvalidFileFormatError, ConversionError, FileSizeLimitError

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

converter = XLSXConverter(
    xls_max_rows=app.config['XLS_MAX_ROWS'],
    xls_max_cols=app.config['XLS_MAX_COLS']
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_old_files():
    logger.info("Running cleanup job")
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=app.config['CLEANUP_AGE_MINUTES'])

    for folder in [app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER']]:
        for file_path in Path(folder).glob('*'):
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Error cleaning up {file_path.name}: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=cleanup_old_files,
    trigger="interval",
    minutes=app.config['CLEANUP_INTERVAL_MINUTES']
)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html', max_size_mb=app.config['MAX_FILE_SIZE_MB'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided', 'code': 'NO_FILE'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected', 'code': 'NO_FILE'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Please upload a .xlsx file', 'code': 'INVALID_TYPE'}), 415

    try:
        original_filename = secure_filename(file.filename)
        unique_id = uuid.uuid4().hex[:8]
        upload_filename = f"{unique_id}_{original_filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)

        file.save(upload_path)
        logger.info(f"File uploaded: {upload_filename}")

        output_filename = upload_filename.replace('.xlsx', '.xls')
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

        converter.convert_file(upload_path, output_path)
        logger.info(f"File converted: {upload_filename} -> {output_filename}")

        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'filename': output_filename.replace(f"{unique_id}_", "")
        })

    except InvalidFileFormatError as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        logger.warning(f"Invalid file format: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'code': 'INVALID_FORMAT'}), 422

    except FileSizeLimitError as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        logger.warning(f"File size limit exceeded: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'code': 'FILE_TOO_LARGE'}), 422

    except ConversionError as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'success': False, 'error': 'Conversion failed. Please try again.', 'code': 'CONVERSION_ERROR'}), 500

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'An unexpected error occurred', 'code': 'SERVER_ERROR'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        safe_filename = secure_filename(filename)

        file_path = os.path.join(app.config['CONVERTED_FOLDER'], safe_filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found', 'code': 'NOT_FOUND'}), 404

        upload_filename = safe_filename.replace('.xls', '.xlsx')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/vnd.ms-excel'
        )

        @response.call_on_close
        def cleanup_files():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up converted file: {safe_filename}")
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                    logger.info(f"Cleaned up upload file: {upload_filename}")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")

        return response

    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Download failed', 'code': 'DOWNLOAD_ERROR'}), 500

@app.route('/health')
def health():
    try:
        upload_writable = os.access(app.config['UPLOAD_FOLDER'], os.W_OK)
        converted_writable = os.access(app.config['CONVERTED_FOLDER'], os.W_OK)

        if upload_writable and converted_writable:
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        else:
            return jsonify({'status': 'unhealthy', 'error': 'Directory permissions issue'}), 503
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': f'File exceeds {app.config["MAX_FILE_SIZE_MB"]}MB limit',
        'code': 'FILE_TOO_LARGE'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found', 'code': 'NOT_FOUND'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'success': False, 'error': 'Internal server error', 'code': 'SERVER_ERROR'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
