from extensions import db
from datetime import datetime, timedelta

class PasswordReset(db.Model):
    __tablename__ = "password_resets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_hash = db.Column(db.String(128), nullable=False)     # SHA-256 OTP
    expires_at = db.Column(db.DateTime, nullable=False)      # hết hạn (10 phút)
    used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")

    @staticmethod
    def ttl_minutes():
        return 10

    @classmethod
    def new_for(cls, user_id, otp_hash):
        return cls(
            user_id=user_id,
            otp_hash=otp_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=cls.ttl_minutes()),
        )
