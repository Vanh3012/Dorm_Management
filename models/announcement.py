from extensions import db
from datetime import datetime

class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))  # đường dẫn file ảnh
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    admin = db.relationship("User", backref="announcements")
    