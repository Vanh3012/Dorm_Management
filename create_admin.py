from app import app, db
from models.user import User
from datetime import date

with app.app_context():
    existing_admin = User.query.filter_by(username="admin").first()
    if existing_admin:
        print("⚠️ Admin account already exists!")
    else:
        admin = User(
            fullname="Admin",
            username="admin",
            date_of_birth=date(2000, 1, 1),  
            student_id="admin1",
            class_id="admin1",
            email="admin@example.com",
            citizen_id="123456789012",
            phone_number="0123456789",
            role="admin"
        )
        admin.set_password("admin123")  
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
