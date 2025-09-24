from extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    status = db.Column(
        db.Enum("active", "finished", "canceled", name="booking_status"),
        default="active"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Quan hệ
    user = db.relationship("User", back_populates="bookings")
    room = db.relationship("Room", back_populates="bookings")
    application = db.relationship("Application", back_populates="bookings")
    payments = db.relationship("Payment", back_populates="booking", cascade="all, delete")
