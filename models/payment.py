from extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application_rooms.id"), nullable=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    fullname = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.String(20), nullable=False)
    citizen_id = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    service_type = db.Column(
        db.Enum("room", "trash", "deposit", "utilities", "maintenance", name="payment_services"),
        nullable=False
    )

    month_paid = db.Column(db.Integer, nullable=False)  # tháng
    year_paid = db.Column(db.Integer, nullable=False)   # năm

    address = db.Column(db.String(150), nullable=False)
    block = db.Column(db.String(10), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(
        db.Enum("cash", "bank_transfer", "qr_code", name="payment_methods"),
        default="cash"
    )
    transaction_id = db.Column(db.String(100))

    status = db.Column(
        db.Enum("success", "pending", name="payment_status"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Quan hệ
    booking = db.relationship("Booking", back_populates="payments")
    user = db.relationship("User", back_populates="payments")
    room = db.relationship("Room", back_populates="payments")
    application = db.relationship("ApplicationRoom", back_populates="payments")




