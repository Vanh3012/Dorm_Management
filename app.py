from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from extensions import db, mail
from flask_migrate import Migrate
from datetime import datetime

# Setup Flask
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Lưu và upload ảnh complain
UPLOAD_FOLDER_COMPLAINS = os.path.join(os.path.dirname(__file__), "static", "uploads","complains")
os.makedirs(UPLOAD_FOLDER_COMPLAINS, exist_ok=True)

#Lưu và update ảnh rooms
UPLOAD_FOLDER_ROOMS = os.path.join(os.path.dirname(__file__), "static", "img","room")
os.makedirs(UPLOAD_FOLDER_ROOMS, exist_ok=True)

#Lưu và update ảnh announcements
UPLOAD_FOLDER_ANNOUNCEMENTS = os.path.join(os.path.dirname(__file__), "static", "uploads", "announcements")
os.makedirs(UPLOAD_FOLDER_ANNOUNCEMENTS, exist_ok=True)

# Lưu & upload ảnh hồ sơ ApplicationRoom
UPLOAD_FOLDER_APPLICATIONS = os.path.join(os.path.dirname(__file__), "static", "uploads", "applications")
os.makedirs(os.path.join(UPLOAD_FOLDER_APPLICATIONS, "priority"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER_APPLICATIONS, "citizen"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER_APPLICATIONS, "student_photo"), exist_ok=True)

app.config["UPLOAD_FOLDER_APPLICATIONS"] = UPLOAD_FOLDER_APPLICATIONS
app.config["UPLOAD_FOLDER_COMPLAINS"] = UPLOAD_FOLDER_COMPLAINS
app.config["UPLOAD_FOLDER_ROOMS"] = UPLOAD_FOLDER_ROOMS
app.config["UPLOAD_FOLDER_ANNOUNCEMENTS"] = UPLOAD_FOLDER_ANNOUNCEMENTS
app.config["ALLOWED_EXTENSIONS"] = {"png", "jfif", "jpg", "jpeg", "gif"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB/file

# Cấu hình Flask-Mail
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),          # ví dụ: yourname@gmail.com
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),          # App password 16 ký tự
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
)


# Khởi tạo db, migrate, mail
db.init_app(app)
migrate = Migrate(app, db)
mail.init_app(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

# Import models sau khi db đã init
from models import User, Room, ApplicationRoom, Booking, Payment, ServiceRequest


# Import blueprints
from blueprints.auth.routes import auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth")

from blueprints.student.routes import student_bp
app.register_blueprint(student_bp, url_prefix="/student")

from blueprints.admin.routes import admin_bp
app.register_blueprint(admin_bp, url_prefix="/admin")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html", year=datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True)
