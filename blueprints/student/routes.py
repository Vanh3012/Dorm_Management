from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.booking import Booking
from models.room import Room
from models.payment import Payment
from models.service_request import ServiceRequest
from models.complain import Complain
from models.complain_image import ComplainImage
from models.announcement import Announcement
from models.notification import Notification
from models.application_rooms import ApplicationRoom
from werkzeug.utils import secure_filename
import os, time
from datetime import datetime

student_bp = Blueprint("student", __name__, template_folder="../../templates/student")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

#-------------------------------------------------------
# Student Dashboard
@student_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("student_dashboard.html")

#-------------------------------------------------------
# Student Profile
@student_bp.route("/student_profile")
@login_required
def student_profile():
    # Kiểm tra user hiện tại có phòng nào active không
    booking = Booking.query.filter_by(user_id=current_user.id, status="active").first()
    room = Room.query.get(booking.room_id) if booking else None

    return render_template("student/student_profile.html", user=current_user, room=room, booking=booking)

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

#-------------------------------------------------------
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
    # Kiểm tra sinh viên đã có phòng chưa
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

    # Hàm lưu file upload
    def save_file(fileobj, subdir):
        if not fileobj or not fileobj.filename:
            return None
        safe = secure_filename(fileobj.filename)
        fname = f"{int(time.time()*1000)}_{safe}"
        base = os.path.join(current_app.config["UPLOAD_FOLDER_APPLICATIONS"], subdir)
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, fname)
        fileobj.save(path)
        return f"uploads/applications/{subdir}/{fname}"

    # Tạo ApplicationRoom trực tiếp
    application = ApplicationRoom(
        user_id=current_user.id,
        room_id=room.id,

        # Thông tin cơ bản
        fullname=request.form.get("fullname"),
        student_id=request.form.get("student_id"),
        class_id=request.form.get("class_id"),
        citizen_id=request.form.get("citizen_id"),
        email=request.form.get("email"),
        phone_number=request.form.get("phone_number"),
        status="pending",

        # Thông tin chi tiết
        address=request.form.get("address"),
        relative1_name=request.form.get("relative1_name"),
        relative1_phone=request.form.get("relative1_phone"),
        relative1_birthyear=request.form.get("relative1_birthyear"),
        relative2_name=request.form.get("relative2_name"),
        relative2_phone=request.form.get("relative2_phone"),
        relative2_birthyear=request.form.get("relative2_birthyear"),

        policy_type=request.form.get("policy_type"),
        # File upload
        policy_proof=save_file(request.files.get("priority_proof"), "priority"),
        citizen_proof=save_file(request.files.get("citizen_proof"), "citizen"),
        student_photo=save_file(request.files.get("student_photo"), "student_photo"),
    )

    db.session.add(application)
    db.session.commit()

    flash("Đơn đăng ký của bạn đã được gửi! Vui lòng chờ duyệt từ admin.", "success")
    return redirect(url_for("student.dashboard"))

#Trả phòng
@student_bp.route("/return_room/<int:booking_id>", methods=["POST"])
@login_required
def return_room(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Kiểm tra quyền: chỉ được trả phòng của chính mình và phòng đang active
    if booking.user_id != current_user.id or booking.status != "active":
        flash("Bạn không thể trả phòng này.", "danger")
        return redirect(url_for("student.student_profile"))

    # Đánh dấu booking là finished
    booking.status = "finished"
    booking.end_date = db.func.current_date()

    # Cập nhật số lượng chỗ trống
    room = booking.room
    if room:
        room.available = room.available + 1

    # Tạo thông báo cho sinh viên
    db.session.commit()
    notif = Notification(
        user_id=current_user.id,
        message=f"Bạn đã trả phòng {booking.room.room_number} thành công."
    )
    db.session.add(notif)
    db.session.commit()
    
    flash("Trả phòng thành công!", "success")
    return redirect(url_for("student.student_profile"))

#-------------------------------------------------------
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

            application = ApplicationRoom.query.get(payment.application_id)
            if application:
                application.status = "completed"

    db.session.commit()
    flash("Thanh toán thành công!", "success")
    return redirect(url_for("student.payments", type=payment.service_type))

#-------------------------------------------------------
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
#-------------------------------------------------------

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
#-------------------------------------------------------

# Announcement
@student_bp.route("/announcements")
def announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("student/announcements.html", announcements=anns)

@student_bp.route("/announcements/<int:ann_id>")
def announcement_detail(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    return render_template("student/announcement_detail.html", ann=ann)

#-------------------------------------------------------
#Notification
@student_bp.route("/notifications")
@login_required
def notifications():
    # Chỉ cho student xem
    if current_user.role != "student":
        flash("Chỉ sinh viên mới được xem trang này.", "warning")
        return redirect(url_for("auth.login"))

    notifs = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("student/notifications.html", notifs=notifs)
    
# Notification context processor
@student_bp.app_context_processor
def inject_notifications():
    if current_user.is_authenticated and current_user.role == "student":
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(notifs=notifs, unread_count=unread_count)
    return {}

@student_bp.route("/notifications/mark_all_read", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return "", 204   # trả rỗng để fetch gọi xong không reload trang

