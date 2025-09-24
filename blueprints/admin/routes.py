from flask import Blueprint, render_template, redirect, jsonify , url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User
from models.booking import Booking
from models.room import Room
from models.application import Application
from models.payment import Payment
from models.service_request import ServiceRequest
from models.complain import Complain
import os, time
from models.room_image import RoomImage
from extensions import db
from datetime import datetime
from werkzeug.utils import secure_filename

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

# Middleware: chỉ admin mới vào được
@admin_bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("Bạn không có quyền truy cập trang quản trị.", "danger")
        return redirect(url_for("auth.login"))

# Dashboard
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/admin_dashboard.html", user=current_user)


# Quản lý phòng
@admin_bp.route("/rooms")
@login_required
def manage_rooms():
    # Bộ lọc từ query string
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

    return render_template("admin/manage_rooms.html", rooms=rooms)


# Chi tiết phòng
@admin_bp.route("/rooms/<int:room_id>")
@login_required
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)

    # Tìm tất cả sinh viên đang ở phòng này (bookings active)
    bookings = (
        Booking.query.filter_by(room_id=room_id, status="active")
        .join(User, Booking.user_id == User.id)
        .all()
    )

    return render_template("admin/room_detail.html", room=room, bookings=bookings)

# Sửa phòng
@admin_bp.route("/rooms/edit", methods=["GET", "POST"])
@admin_bp.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
@login_required
def edit_room(room_id=None):
    room = Room.query.get(room_id) if room_id else None

    if request.method == "POST":
        # --- nhận form cơ bản (có thể thêm các trường giá nếu bạn có) ---
        block        = (request.form.get("block") or "").strip()
        room_number  = (request.form.get("room_number") or "").strip()
        address      = (request.form.get("address") or "").strip()
        capacity     = int(request.form.get("capacity") or 0)

        if room:  # cập nhật
            room.block = block
            room.room_number = room_number
            room.address = address
            room.capacity = capacity
            flash("Cập nhật phòng thành công!", "success")
        else:     # thêm mới
            room = Room(
                block=block,
                room_number=room_number,
                address=address,
                capacity=capacity,
                current_occupancy=0,
            )
            db.session.add(room)
            # cần ID để gắn ảnh
            db.session.flush()

            flash("Thêm phòng thành công!", "success")

        # --- upload nhiều ảnh ---
        files = request.files.getlist("images")
        if files:
            # Lưu theo thư mục con address/block (nếu muốn phân loại)
            base_folder = os.path.join(current_app.config["UPLOAD_FOLDER_ROOMS"], address, block)
            os.makedirs(base_folder, exist_ok=True)

            for f in files:
                if not (f and f.filename and allowed_file(f.filename)):
                    continue
                safe = secure_filename(f.filename)
                # chống trùng tên
                filename = f"{int(time.time()*1000)}_{safe}"
                save_path = os.path.join(base_folder, filename)
                f.save(save_path)

                rel_url = f"/static/img/room/{address}/{block}/{filename}"
                db.session.add(RoomImage(room_id=room.id, image_url=rel_url))

        db.session.commit()
        return redirect(url_for("admin.room_detail", room_id=room.id))

    return render_template("admin/edit_room.html", room=room)



# Quản lý đơn đăng ký
@admin_bp.route("/manage_applications")
@login_required
def manage_applications():
    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    applications = Application.query.order_by(Application.created_at.asc()).all()
    return render_template("admin/manage_applications.html", applications=applications)


# API: Lấy chi tiết 1 đơn (JSON) -> dùng AJAX gọi
@admin_bp.route("/api/application/<int:app_id>")
@login_required
def get_application_detail(app_id):
    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    app = Application.query.get_or_404(app_id)
    data = {
        "id": app.id,
        "fullname": app.fullname,
        "student_id": app.student_id,
        "class_id": app.class_id,
        "citizen_id": app.citizen_id,
        "email": app.email,
        "phone_number": app.phone_number,
        "room": f"{app.room.block}{app.room.room_number} - {app.room.address}",
        "status": app.status,
        "created_at": app.created_at.strftime("%d/%m/%Y %H:%M"),
        # chỉ cho phép hành động khi còn pending
        "can_approve": app.status == "pending",
        "can_reject": app.status == "pending",
    }
    return jsonify(data)

# Duyệt đơn
@admin_bp.route("/application/<int:app_id>/approve")
@login_required
def approve_application(app_id):
    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    application = Application.query.get_or_404(app_id)
    room = Room.query.get(application.room_id)

    # Chỉ thay đổi trạng thái đơn, KHÔNG trừ available ở đây
    application.status = "approved_pending_deposit"

    # Tạo hóa đơn tiền cọc

    now = datetime.now()
    payment = Payment(
        application_id=application.id,
        booking_id=None,   # chưa có booking chính thức
        user_id=application.user_id,
        room_id=application.room_id,
        fullname=application.fullname,
        student_id=application.student_id,
        class_id=application.class_id,
        citizen_id=application.citizen_id,
        email=application.email,
        phone_number=application.phone_number,
        service_type="deposit",
        month_paid=datetime.now().month,
        year_paid=datetime.now().year,
        address=room.address,
        block=room.block,
        room_number=room.room_number,
        amount=room.deposit,
        payment_method="cash", # mặc định
        status="pending"   # chưa thanh toán
    )

    db.session.add(payment)
    db.session.commit()

    flash("Đơn đã được duyệt. Sinh viên cần thanh toán cọc trước khi được xếp phòng.", "success")
    return redirect(url_for("admin.manage_applications"))


#Từ chối đơn
@admin_bp.route("/application/<int:app_id>/reject")
@login_required
def reject_application(app_id):
    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    application = Application.query.get_or_404(app_id)
    if application.status != "pending":
        flash("Đơn này đã được xử lý trước đó.", "info")
        return redirect(url_for("admin.manage_applications"))

    application.status = "rejected"
    db.session.commit()
    flash("Đơn đã bị từ chối.", "info")
    return redirect(url_for("admin.manage_applications"))


# Quản lý sinh viên
@admin_bp.route("/students")
@login_required
def students():
    # Lấy tất cả sinh viên
    students = User.query.filter_by(role="student").all()

    data = []
    for s in students:
        # Phòng đang ở (nếu có booking active)
        booking = Booking.query.filter_by(user_id=s.id, status="active").first()
        room = Room.query.get(booking.room_id) if booking else None

        # Hóa đơn
        payments = Payment.query.filter_by(user_id=s.id).all()
        unpaid = [p for p in payments if p.status != "success"]

        data.append({
            "student": s,
            "room": room,
            "payments": payments,
            "unpaid": unpaid
        })

    return render_template("admin/students.html", students=data)

# Chi tiết sinh viên
@admin_bp.route("/students/<int:student_id>/detail")
@login_required
def student_detail_api(student_id):
    student = User.query.get_or_404(student_id)
    booking = Booking.query.filter_by(user_id=student.id, status="active").first()
    room = Room.query.get(booking.room_id) if booking else None
    payments = Payment.query.filter_by(user_id=student.id).all()

    return jsonify({
        "student_id": student.student_id,
        "fullname": student.fullname,
        "class_id": student.class_id,
        "email": student.email,
        "phone_number": student.phone_number,
        "room": f"{room.room_number} ({room.block})" if room else None,
        "payments": [
            {"service": p.service_type, "amount": p.amount, "status": p.status}
            for p in payments
        ]
    })

# Quản lý hóa đơn
@admin_bp.route("/payments")
@login_required
def payments():
    # Lấy toàn bộ hóa đơn, sắp xếp mới nhất trước
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template("admin/payments.html", payments=payments)


@admin_bp.route("/payments/<int:payment_id>/mark_paid", methods=["POST"])
@login_required
def mark_payment_paid(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = "success"
    db.session.commit()
    flash("Hóa đơn đã được xác nhận thanh toán!", "success")
    return redirect(url_for("admin.payments"))
    
# Quản lý yêu cầu dịch vụ
@admin_bp.route("/services")
@login_required
def manage_services():
    # Lấy tất cả yêu cầu dịch vụ
    service_requests = ServiceRequest.query.order_by(ServiceRequest.id.asc()).all()
    return render_template("admin/services.html", service_requests=service_requests)


@admin_bp.route("/services/<int:req_id>/update/<string:status>")
@login_required
def update_service_status(req_id, status):
    req = ServiceRequest.query.get_or_404(req_id)

    if status not in ["in_progress", "completed", "rejected"]:
        flash("Trạng thái không hợp lệ!", "danger")
        return redirect(url_for("admin.manage_services"))

    req.status = status

    # Nếu là dịch vụ thu gom rác → khi completed thì tạo hóa đơn luôn
    if status == "completed" and req.service_type == "trash":
        payment = Payment(
            user_id=req.user.id,
            room_id=req.room.id if req.room else None,
            fullname=req.user.fullname,
            student_id=req.user.student_id,
            class_id=req.user.class_id,
            citizen_id=req.user.citizen_id,
            email=req.user.email,
            phone_number=req.user.phone_number,
            service_type="trash",
            month_paid=db.func.month(db.func.now()),
            year_paid=db.func.year(db.func.now()),
            address=req.room.address if req.room else "-",
            block=req.room.block if req.room else "-",
            room_number=req.room.room_number if req.room else "-",
            amount=req.price,  
            payment_method="cash",
            status="pending"
        )
        db.session.add(payment)
    db.session.commit()
    flash("Cập nhật trạng thái thành công!", "success")
    return redirect(url_for("admin.manage_services"))

@admin_bp.route("/services/<int:req_id>/set_price", methods=["POST"])
@login_required
def set_service_price(req_id):
    req = ServiceRequest.query.get_or_404(req_id)

    try:
        price = int(request.form.get("price", 0))
        req.price = price

        # Khi admin nhập giá xong thì cũng tạo Payment
        payment = Payment(
            user_id=req.user.id,
            room_id=req.room.id if req.room else None,
            fullname=req.user.fullname,
            student_id=req.user.student_id,
            class_id=req.user.class_id,
            citizen_id=req.user.citizen_id,
            email=req.user.email,
            phone_number=req.user.phone_number,
            service_type="maintenance",
            month_paid=db.func.month(db.func.now()),
            year_paid=db.func.year(db.func.now()),
            address=req.room.address if req.room else "-",
            block=req.room.block if req.room else "-",
            room_number=req.room.room_number if req.room else "-",
            amount=price,
            payment_method="cash",
            status="pending"
        )
        db.session.add(payment)

        db.session.commit()
        flash("Đã cập nhật giá và tạo hóa đơn!", "success")
    except Exception:
        db.session.rollback()
        flash("Có lỗi khi cập nhật giá!", "danger")

    return redirect(url_for("admin.manage_services"))

# Quản lý complain
@admin_bp.route("/complains")
@login_required
def manage_complains():
    complains = Complain.query.order_by(Complain.created_at.desc()).all()
    return render_template("admin/complains.html", complains=complains)

#  Trả lời complain
@admin_bp.route("/complains/<int:complain_id>/reply", methods=["POST"])
@login_required
def reply_complain(complain_id):
    complain = Complain.query.get_or_404(complain_id)
    reply = request.form.get("reply")

    if not reply.strip():
        flash("Nội dung phản hồi không được để trống!", "danger")
        return redirect(url_for("admin.manage_complains"))

    complain.reply = reply
    complain.status = "answered"
    db.session.commit()

    flash("Đã phản hồi khiếu nại!", "success")
    return redirect(url_for("admin.manage_complains"))

#  Đóng complain (nếu cần)
@admin_bp.route("/complains/<int:complain_id>/close", methods=["POST"])
@login_required
def close_complain(complain_id):
    complain = Complain.query.get_or_404(complain_id)
    complain.status = "closed"
    db.session.commit()

    flash("Đã đóng khiếu nại!", "success")
    return redirect(url_for("admin.manage_complains"))
