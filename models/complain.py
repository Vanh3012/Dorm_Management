from extensions import db

class Complain(db.Model):
    __tablename__ = "complains"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = db.Column(db.String(200), nullable=False)     # tiêu đề ngắn
    content = db.Column(db.Text, nullable=False)          # nội dung complain
    reply = db.Column(db.Text)                            # phản hồi của admin

    status = db.Column(
        db.Enum("pending", "answered", "closed", name="complain_status"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship("User", back_populates="complains")
    images = db.relationship("ComplainImage", back_populates="complain", cascade="all, delete-orphan")