from extensions import db

class ComplainImage(db.Model):
    __tablename__ = "complain_images"

    id = db.Column(db.Integer, primary_key=True)
    complain_id = db.Column(db.Integer, db.ForeignKey("complains.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  # đường dẫn file ảnh (trong /static/uploads)

    complain = db.relationship("Complain", back_populates="images")