from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db, mail
from models.user import User
from flask_mail import Message
from models.password_reset import PasswordReset
from datetime import datetime
import hashlib, random 

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

# Đăng ký
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")
        student_id = request.form.get("student_id")
        class_id = request.form.get("class_id")
        email = request.form.get("email")
        citizen_id = request.form.get("citizen_id")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # ✅ Check nhập lại mật khẩu
        if password != confirm_password:
            flash("Mật khẩu không khớp, vui lòng nhập lại!", "danger")
            return redirect(url_for("auth.register"))

        # Kiểm tra user trùng
        if User.query.filter((User.email == email) | (User.student_id == student_id)).first():
            flash("Email hoặc mã sinh viên đã tồn tại!", "danger")
            return redirect(url_for("auth.register"))

        # Tạo user mới
        user = User(
            fullname=fullname,
            username=username,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"),
            student_id=student_id,
            class_id=class_id,
            email=email,
            citizen_id=citizen_id,
            phone_number=phone_number
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

# Đăng nhập
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            if user.role == "student":
                return redirect(url_for("student.dashboard"))
            elif user.role == "admin":
                return redirect(url_for("admin.dashboard")) 
            else:
                return redirect(url_for("home"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")

    return render_template("login.html")

# Đăng xuất
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))


# Quên mật khẩu - Gửi email OTP# Quên mật khẩu ---Cái này chưa làm xong, khộ quạ......
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email không tồn tại trong hệ thống.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # Sinh OTP
        otp = f"{random.randint(100000, 999999)}"
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        # Tạo record mới
        reset = PasswordReset.new_for(user.id, otp_hash)
        db.session.add(reset)
        db.session.commit()

        # Gửi mail
        msg = Message("Mã xác nhận đặt lại mật khẩu", recipients=[email])
        msg.body = f"Mã OTP của bạn: {otp}\nCó hiệu lực trong 10 phút."
        mail.send(msg)

        flash("Mã OTP đã gửi vào email.", "success")
        return redirect(url_for("auth.reset_password", reset_id=reset.id))

    return render_template("forgot_password.html")


# Nhập OTP và đổi mật khẩu
@auth_bp.route("/reset-password/<int:reset_id>", methods=["GET", "POST"])
def reset_password(reset_id):
    reset = PasswordReset.query.get_or_404(reset_id)

    if request.method == "POST":
        otp = request.form.get("otp")
        new_password = request.form.get("password")
        confirm = request.form.get("confirm")

        # check OTP
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        if reset.otp_hash != otp_hash:
            reset.attempts += 1
            db.session.commit()
            flash("Mã OTP không chính xác.", "danger")
            return redirect(request.url)

        if reset.expires_at < datetime.utcnow():
            flash("Mã OTP đã hết hạn.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if reset.used:
            flash("Mã OTP đã được dùng rồi.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if new_password != confirm:
            flash("Mật khẩu nhập lại không khớp.", "danger")
            return redirect(request.url)

        # update password
        reset.user.set_password(new_password)
        reset.used = True
        db.session.commit()

        flash("Đặt lại mật khẩu thành công!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", reset=reset)

# Gửi lại OTP sau 60s
@auth_bp.route("/resend-otp/<int:reset_id>")
def resend_otp(reset_id):
    reset = PasswordReset.query.get_or_404(reset_id)

    # Không cho gửi lại quá sớm
    if (datetime.utcnow() - reset.created_at) < timedelta(seconds=60):
        flash("Vui lòng đợi 60s trước khi yêu cầu lại.", "danger")
        return redirect(url_for("auth.reset_password", reset_id=reset.id))

    # Tạo OTP mới
    otp = f"{random.randint(100000, 999999)}"
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    reset.otp_hash = otp_hash
    reset.expires_at = datetime.utcnow() + timedelta(minutes=10)
    reset.created_at = datetime.utcnow()
    reset.attempts = 0
    db.session.commit()

    msg = Message("Mã OTP mới", recipients=[reset.user.email])
    msg.body = f"Mã OTP mới của bạn: {otp} (hiệu lực 10 phút)"
    mail.send(msg)

    flash("Đã gửi lại OTP mới.", "success")
    return redirect(url_for("auth.reset_password", reset_id=reset.id))

#Trang thông tin
@auth_bp.route("/info")
def info():
    return render_template("info.html")