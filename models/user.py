from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.String(20), nullable=False, unique=True)
    class_id = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    citizen_id = db.Column(db.String(20), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)  # phòng hiện tại

    role = db.Column(
        db.Enum("admin", "student", name="user_roles"),
        default="student"
    )
    status = db.Column(
        db.Enum("active", "inactive", "banned", name="user_status"),
        default="active"
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Quan hệ với các bảng khác (chỉ cần tên class, không cần import Application/Booking/Payment ở đây)
    applications = db.relationship("ApplicationRoom", back_populates="user", lazy=True)
    bookings = db.relationship("Booking", back_populates="user", lazy=True)
    payments = db.relationship("Payment", back_populates="user", lazy=True)
    complains = db.relationship("Complain", back_populates="user")
    service_requests = db.relationship(
    "ServiceRequest",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
