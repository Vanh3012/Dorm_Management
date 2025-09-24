from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db
from models.user import User
from datetime import datetime

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
                return redirect(url_for("admin.dashboard"))  # sau này sẽ tạo admin dashboard
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
