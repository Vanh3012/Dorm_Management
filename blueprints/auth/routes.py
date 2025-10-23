from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models.user import User
from models.password_reset import PasswordReset
from datetime import datetime, timedelta

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

        # Check nhập lại mật khẩu
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

# -----------------------------------------------------------------------------
# Quên mật khẩu
def mask_email(email: str) -> str:
    if not email or "@" not in email: return "***"
    local, domain = email.split("@", 1)
    masked_local = (local[:2] + "***" + (local[-1:] if len(local) > 3 else "")) if len(local) > 2 else local[:1] + "***"
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    if not phone: return "***"
    p = phone.strip()
    return f"{p[:3] if len(p)>=3 else p[:1]}****{p[-2:] if len(p)>=2 else ''}"

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        u = User.query.filter_by(username=username).first()
        if not u:
            flash("Tên đăng nhập không tồn tại.", "danger")
            return render_template("forgot_password.html", show_modal=False)

        return render_template(
            "forgot_password.html",
            show_modal=True,
            fp_user=u,
            fp_masked_email=mask_email(u.email or ""),
            fp_masked_phone=mask_phone(getattr(u, "phone_number", "") or ""),
        )

    return render_template("forgot_password.html", show_modal=False)

@auth_bp.route("/verify-contact", methods=["POST"])
def verify_contact():
    username = request.form.get("username", "").strip()
    method   = request.form.get("method")
    value    = request.form.get("input_value", "").strip()

    u = User.query.filter_by(username=username).first()
    if not u:
        flash("Không tìm thấy người dùng.", "danger")
        return redirect(url_for("auth.forgot_password"))

    ok = (method == "email" and value == (u.email or "")) or \
         (method == "phone" and value == (getattr(u, "phone_number", "") or ""))

    if not ok:
        flash("Thông tin xác nhận không đúng.", "danger")
        return redirect(url_for("auth.forgot_password"))

    return redirect(url_for("auth.reset_password", u=username))

# Đặt lại mật khẩu
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    username = request.args.get("u") or request.form.get("username")
    if not username:
        flash("Thiếu thông tin người dùng.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    u = User.query.filter_by(username=username).first_or_404()
    if not u:
        flash("Không tìm thấy người dùng.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        pw = request.form.get("password")
        cf = request.form.get("confirm")
        if pw != cf:
            flash("Mật khẩu nhập lại không khớp.", "danger")
            return redirect(url_for("auth.reset_password", u=username))
        u.set_password(pw)
        db.session.commit()
        flash("Đặt lại mật khẩu thành công!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", username=username)

#Trang thông tin
@auth_bp.route("/info")
def info():
    return render_template("info.html")