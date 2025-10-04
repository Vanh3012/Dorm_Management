from extensions import db

class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(150), nullable=False)
    block = db.Column(db.String(10), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, default=4)
    available = db.Column(db.Integer, default=4)

    price_room = db.Column(db.Numeric(10, 2), nullable=False)
    price_electricity = db.Column(db.Numeric(10, 2), default=0)
    price_water = db.Column(db.Numeric(10, 2), default=0)
    price_service = db.Column(db.Numeric(10, 2), default=0)
    deposit = db.Column(db.Numeric(10, 2), default=0)

    status = db.Column(
        db.Enum("available", "occupied", "maintenance", "closed", name="room_status"),
        default="available"
    )


    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Quan hệ
    applications = db.relationship("ApplicationRoom", back_populates="room", cascade="all, delete")
    bookings = db.relationship("Booking", back_populates="room", cascade="all, delete")
    payments = db.relationship("Payment", back_populates="room", cascade="all, delete")
    images = db.relationship(
        "RoomImage",
        back_populates="room",
        cascade="all, delete-orphan"
    )