from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.booking import Booking
from models.room import Room
from models.application import Application
from models.payment import Payment
from models.service_request import ServiceRequest
from models.complain import Complain
from models.complain_image import ComplainImage
from werkzeug.utils import secure_filename
import os
from datetime import datetime

student_bp = Blueprint("student", __name__, template_folder="../../templates/student")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

@student_bp.route("/dashboard")
@login_required
def dashboard():
    # Kiểm tra user hiện tại có phòng nào active không
    booking = Booking.query.filter_by(user_id=current_user.id, status="active").first()
    room = Room.query.get(booking.room_id) if booking else None

    return render_template("student_dashboard.html", user=current_user, room=room)

# Student Profile
@student_bp.route("/student_profile")
@login_required
def student_profile():
    # Kiểm tra user hiện tại có phòng nào active không
    booking = Booking.query.filter_by(user_id=current_user.id, status="active").first()
    room = Room.query.get(booking.room_id) if booking else None

    return render_template("student/student_profile.html", user=current_user, room=room)



# UPDATE PROFILE
@student_bp.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    if request.method == "POST":
        current_user.fullname = request.form.get("fullname")
        current_user.class_id = request.form.get("class_id")
        current_user.phone_number = request.form.get("phone_number")
        current_user.citizen_id = request.form.get("citizen_id")
        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/update_profile.html", user=current_user)


#Đăng ký phòng 
@student_bp.route("/dorm_register", methods=["GET", "POST"])
@login_required
def dorm_register():
    # Bộ lọc (cơ sở, block, số phòng)
    address = request.args.get("address")
    block = request.args.get("block")
    room_number = request.args.get("room_number")

    query = Room.query

    if address:
        query = query.filter_by(address=address)
    if block:
        query = query.filter_by(block=block)
    if room_number:
        query = query.filter_by(room_number=room_number)

    rooms = query.all()

    return render_template("student/dorm_register.html", rooms=rooms)


# Trang chi tiết phòng
@student_bp.route("/room/<int:room_id>", methods=["GET","POST"])
@login_required
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    # Kiểm tra nếu phòng đã full thì không cho đăng ký
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id, status="active"
    ).first()
    if existing_booking:
        flash("Bạn đã có phòng, không thể đăng ký thêm!", "danger")
        return redirect(url_for("student.dorm_register"))
    return render_template("student/room_detail.html", room=room, user=current_user)


# Route gửi đơn đăng ký
@student_bp.route("/register_room/<int:room_id>", methods=["POST"])
@login_required
def register_room(room_id):
    room = Room.query.get_or_404(room_id)

    # Nếu phòng full thì chặn luôn
    if room.available <= 0:
        flash("Phòng đã hết chỗ, không thể đăng ký!", "danger")
        return redirect(url_for("student.room_detail", room_id=room_id))

    # Tạo đơn đăng ký mới
    application = Application(
        user_id=current_user.id,
        room_id=room.id,
        fullname=request.form.get("fullname"),
        student_id=request.form.get("student_id"),
        class_id=request.form.get("class_id"),
        citizen_id=request.form.get("citizen_id"),
        email=request.form.get("email"),
        phone_number=request.form.get("phone_number"),
        status="pending"  # mặc định chờ duyệt
    )

    db.session.add(application)
    db.session.commit()

    flash("Đơn đăng ký của bạn đã được gửi! Vui lòng chờ duyệt từ admin.", "success")
    return redirect(url_for("student.dashboard"))


#Payments
@student_bp.route("/payments")
@login_required
def payments():
    service_type = request.args.get("type", "all")  # ?type=deposit / room / utilities / service

    query = Payment.query.filter_by(user_id=current_user.id)

    if service_type != "all":
        query = query.filter_by(service_type=service_type)

    payments = query.order_by(Payment.created_at.asc()).all()

    return render_template(
        "student/payments.html",
        payments=payments,
        current_type=service_type
    )


@student_bp.route("/pay/<int:payment_id>", methods=["POST"])
@login_required
def pay(payment_id):
    payment = Payment.query.get_or_404(payment_id)

    # check quyền: sinh viên chỉ được trả tiền của chính mình
    if payment.user_id != current_user.id:
        flash("Bạn không thể thanh toán hóa đơn này!", "danger")
        return redirect(url_for("student.payments"))

    if payment.status == "success":
        flash("Hóa đơn này đã được thanh toán trước đó.", "info")
        return redirect(url_for("student.payments"))

    # Giả lập: thanh toán thành công
    payment.status = "success"

    # Nếu là tiền cọc thì tạo booking và trừ số chỗ phòng
    if payment.service_type == "deposit":

        room = Room.query.get(payment.room_id)
        if room and room.available > 0:
            booking = Booking(
                user_id=current_user.id,
                room_id=room.id,
                application_id=payment.application_id,
                start_date=datetime.now(),
                status="active"
            )
            db.session.add(booking)
            room.available -= 1

            application = Application.query.get(payment.application_id)
            if application:
                application.status = "completed"

    db.session.commit()
    flash("Thanh toán thành công!", "success")
    return redirect(url_for("student.payments", type=payment.service_type))

# Service Requests
@student_bp.route("/services", methods=["GET", "POST"])
@login_required
def services():
    # Giá dịch vụ
    TRASH_PRICE = 50000  # 50k / tháng

    if request.method == "POST":
        service_type = request.form.get("service_type")
        description = request.form.get("description")

        booking = Booking.query.filter_by(user_id=current_user.id, status="active").first()
        room_id = booking.room_id if booking else None

        # Nếu là dịch vụ thu gom rác thì gán giá luôn
        price = TRASH_PRICE if service_type == "trash" else 0

        req = ServiceRequest(
            user_id=current_user.id,
            room_id=room_id,
            service_type=service_type,
            description=description,
            price=price
        )
        db.session.add(req)
        db.session.commit()
        flash("Đã gửi yêu cầu dịch vụ!", "success")
        return redirect(url_for("student.services"))

    service_requests = ServiceRequest.query.filter_by(user_id=current_user.id).order_by(ServiceRequest.created_at.asc()).all()
    return render_template("student/services.html", service_requests=service_requests)

# Complains
@student_bp.route("/complains", methods=["GET", "POST"])
@login_required
def complains():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        files = request.files.getlist("images")

        # Tạo complain
        complain = Complain(
            user_id=current_user.id,
            title=title,
            content=content,
        )
        db.session.add(complain)
        db.session.commit()

        # Lưu file ảnh (nếu có)
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER_COMPLAINS"], filename)
                file.save(save_path)

                img = ComplainImage(
                    complain_id=complain.id,
                    image_url=f"uploads/complains/{filename}"
                )
                db.session.add(img)

        db.session.commit()
        flash("Đã gửi khiếu nại thành công!", "success")
        return redirect(url_for("student.complains"))

    complains = Complain.query.filter_by(user_id=current_user.id).order_by(Complain.created_at.desc()).all()
    return render_template("student/complains.html", complains=complains)