from extensions import db

class ServiceRequest(db.Model):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True)

    service_type = db.Column(
        db.Enum("trash", "maintenance", name="service_request_types"),
        nullable=False
    )
    description = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), default=0)  # trash thì gán cố định, maintenance admin nhập sau

    status = db.Column(
        db.Enum("pending", "in_progress", "completed", "rejected", name="service_request_statuses"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship("User", back_populates="service_requests")
    room = db.relationship("Room")
