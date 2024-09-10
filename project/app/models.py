from app import db

class QRCode(db.Model):
    __tablename__ = 'qrcode'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    image = db.Column(db.Text)

class QRCodeUsage(db.Model):
    __tablename__ = 'qr_code_usage'
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qrcode.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    count = db.Column(db.Integer, default=1)

    db.UniqueConstraint('qr_code_id', 'date', name='unique_qr_code_date')
