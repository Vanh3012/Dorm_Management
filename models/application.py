from extensions import db

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    fullname = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.String(20), nullable=False)
    citizen_id = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    status = db.Column(
        db.Enum("pending", "rejected", "approved_pending_deposit", "completed", name="application_status"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Quan hệ
    user = db.relationship("User", back_populates="applications")
    room = db.relationship("Room", back_populates="applications")
    bookings = db.relationship("Booking", back_populates="application", cascade="all, delete")
