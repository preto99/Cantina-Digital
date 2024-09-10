import qrcode
from io import BytesIO
import base64
import tempfile
import zipfile
import os
from flask import send_file, jsonify, request, render_template
from datetime import datetime
from app import app, db
from app.models import QRCode, QRCodeUsage

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    qr_codes = QRCode.query.all()
    return render_template('admin_panel.html', qr_codes=qr_codes)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/generate_qr_batch', methods=['POST'])
def generate_qr_batch():
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400

    data = request.get_json()
    if data is None:
        return jsonify({'message': 'Invalid JSON data'}), 400

    count = data.get('count', 100)
    if not isinstance(count, int) or count <= 0:
        return jsonify({'message': 'Invalid count provided'}), 400

    temp_dir = tempfile.mkdtemp()
    qr_codes = []

    for i in range(count):
        code = f"unique_code_{i}_{datetime.utcnow().timestamp()}"
        img = qrcode.make(code)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        qr_code = QRCode(code=code, image=img_str)
        db.session.add(qr_code)
        file_path = os.path.join(temp_dir, f"{code}.png")
        img.save(file_path)
        qr_codes.append(file_path)

    db.session.commit()

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_path in qr_codes:
            zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)

    for file_path in qr_codes:
        os.remove(file_path)
    os.rmdir(temp_dir)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, attachment_filename='qr_codes.zip')

@app.route('/download_all_qr_codes', methods=['GET'])
def download_all_qr_codes():
    qr_codes = QRCode.query.all()
    temp_dir = tempfile.mkdtemp()
    qr_files = []

    for qr_code in qr_codes:
        file_path = os.path.join(temp_dir, f"{qr_code.code}.png")
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(qr_code.image))
        qr_files.append(file_path)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_path in qr_files:
            zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)

    for file_path in qr_files:
        os.remove(file_path)
    os.rmdir(temp_dir)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, attachment_filename='all_qr_codes.zip')

@app.route('/download_qr_code/<int:qr_code_id>', methods=['GET'])
def download_qr_code(qr_code_id):
    qr_code = QRCode.query.get(qr_code_id)
    if not qr_code:
        return jsonify({'message': 'QR code not found'}), 404

    file_path = f"{qr_code.code}.png"
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(qr_code.image))
    
    return send_file(file_path, mimetype='image/png', as_attachment=True)

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400

    data = request.get_json()
    if data is None or 'qr_code' not in data:
        return jsonify({'message': 'Invalid JSON data'}), 400

    qr_code = QRCode.query.filter_by(code=data['qr_code']).first()
    if qr_code:
        date = datetime.utcnow().date()
        qr_usage = QRCodeUsage.query.filter_by(qr_code_id=qr_code.id, date=date).first()
        if qr_usage:
            qr_usage.count += 1
        else:
            qr_usage = QRCodeUsage(qr_code_id=qr_code.id, date=date, count=1)
            db.session.add(qr_usage)
        db.session.commit()

        # Send data for interactive display
        return jsonify({'message': 'QR code scanned successfully', 'data': qr_code.code, 'count': qr_usage.count, 'date': str(date)})
    return jsonify({'message': 'QR code not found'}), 404

@app.route('/qr_statistics', methods=['GET'])
def qr_statistics():
    stats = db.session.query(QRCodeUsage.qr_code_id, db.func.count(QRCodeUsage.qr_code_id)).group_by(QRCodeUsage.qr_code_id).all()
    statistics = {qr_code_id: count for qr_code_id, count in stats}
    return jsonify(statistics)