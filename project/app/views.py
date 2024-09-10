from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import QRCode, QRCodeUsage
import segno

@app.route('/')
def home():
    return redirect(url_for('scan'))

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/admin_panel')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.form['data']
    qr = segno.make(data)
    qr.save(f'static/qr_codes/{data}.png')

    new_qr = QRCode(code=data, image=f'static/qr_codes/{data}.png')
    db.session.add(new_qr)
    db.session.commit()

    return redirect(url_for('admin_panel'))
