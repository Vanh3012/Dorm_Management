from extensions import db
from datetime import datetime

class ApplicationRoom(db.Model):
    __tablename__ = "application_rooms"

    id = db.Column(db.Integer, primary_key=True)

    # Liên kết
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    # Thông tin cơ bản
    fullname = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.String(20), nullable=False)
    citizen_id = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)      

    relative1_name  = db.Column(db.String(100))
    relative1_phone = db.Column(db.String(15))
    relative1_birthyear = db.Column(db.Integer)

    relative2_name  = db.Column(db.String(100))
    relative2_phone = db.Column(db.String(15))
    relative2_birthyear = db.Column(db.Integer)

    # Chính sách xã hội / ưu tiên
    policy_type   = db.Column(db.String(255))      # VD: Con liệt sĩ, dân tộc thiểu số...
    policy_proof  = db.Column(db.String(255))      # File minh chứng

    # Hoàn cảnh khó khăn
    hardship_detail = db.Column(db.Text)           # kê khai cụ thể: thu nhập, đất đai, tư liệu sản xuất
    hardship_proof  = db.Column(db.String(255))    # File xác nhận

    citizen_proof = db.Column(db.String(255))      # Ảnh CCCD
    student_photo = db.Column(db.String(255))      # Ảnh chân dung

    # Trạng thái
    status = db.Column(
        db.Enum("pending", "rejected", "approved_pending_deposit", "completed", name="application_status"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ
    user = db.relationship("User", back_populates="applications")
    room = db.relationship("Room", back_populates="applications")
    bookings = db.relationship("Booking", back_populates="application", cascade="all, delete")
    payments = db.relationship("Payment", back_populates="application", cascade="all, delete")

    