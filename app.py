import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
import time
from converter import PDFToPowerPointConverter
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB - reduced for better performance

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = time.time()
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for filename in os.listdir(folder):
            if filename == '.gitkeep':
                continue
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > 3600:  # 1 hour
                    try:
                        os.remove(file_path)
                        logging.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error cleaning up file {file_path}: {str(e)}")

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF file.', 'error')
            return redirect(url_for('index'))
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename or 'upload.pdf')
        filename = f"{unique_id}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(filepath)
        logging.info(f"File uploaded: {filepath}")
        
        # Convert PDF to PowerPoint
        converter = PDFToPowerPointConverter()
        
        try:
            output_filename = f"{unique_id}_{original_filename.rsplit('.', 1)[0]}.pptx"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            success = converter.convert(filepath, output_path, max_pages=30)
            
            if success:
                flash('PDF converted successfully! Click the download button below.', 'success')
                return render_template('index.html', download_file=output_filename, 
                                     original_name=original_filename.rsplit('.', 1)[0])
            else:
                flash('Error converting PDF. Please ensure the file is valid and not corrupted.', 'error')
                return redirect(url_for('index'))
                
        except Exception as e:
            logging.error(f"Conversion error: {str(e)}")
            flash(f'Error during conversion: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                logging.error(f"Error removing uploaded file: {str(e)}")
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        
        if not os.path.exists(file_path):
            flash('File not found or has expired.', 'error')
            return redirect(url_for('index'))
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('index'))

@app.route('/status/<task_id>')
def get_status(task_id):
    # Simple status endpoint for future enhancement
    return jsonify({'status': 'processing'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)