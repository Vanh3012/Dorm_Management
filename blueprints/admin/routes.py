from flask import Blueprint, render_template, redirect, jsonify , url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User
from models.booking import Booking
from models.room import Room
from models.application_rooms import ApplicationRoom
from models.payment import Payment
from models.service_request import ServiceRequest
from models.complain import Complain
from models.complain_image import ComplainImage
from models.announcement import Announcement 
import os, time
from models.room_image import RoomImage
from models.notification import Notification
from extensions import db
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import or_, func, extract
import unicodedata, calendar

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

# Middleware: chỉ admin mới vào được
@admin_bp.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("Bạn không có quyền truy cập trang quản trị.", "danger")
        return redirect(url_for("auth.login"))
#-------------------------------------------------------
#Dashboard
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    # Lấy tháng/năm từ query params (mặc định là tháng/năm hiện tại)
    selected_month = request.args.get('month', type=int)
    selected_year = request.args.get('year', type=int)
    
    # Nếu không có giá trị, dùng tháng/năm hiện tại
    if not selected_month:
        selected_month = datetime.now().month
    if not selected_year:
        selected_year = datetime.now().year

    # Tổng sinh viên, phòng, hóa đơn chưa thanh toán
    total_students = User.query.filter_by(role="student").count()
    total_rooms = Room.query.count()
    unpaid_bills = Payment.query.filter(Payment.status != "success").count()

    # Thống kê doanh thu theo loại dịch vụ trong tháng đã chọn
    revenue_by_service = (
        db.session.query(Payment.service_type, func.sum(Payment.amount))
        .filter(
            Payment.month_paid == selected_month,
            Payment.year_paid == selected_year,
            Payment.status == "success"
        )
        .group_by(Payment.service_type)
        .all()
    )
    service_name_map = {
    "deposit": "Tiền đặt cọc",
    "utilities": "Điện & Nước",
    "trash": "Thu gom rác",
    "maintenance": "Bảo trì - Sửa chữa"
    }
    service_labels = [service_name_map.get(r[0], "Khác") for r in revenue_by_service]
    service_values = [float(r[1]) if r[1] else 0 for r in revenue_by_service]

    # Tổng tiền hóa đơn tháng đã chọn
    total_revenue = sum(service_values)

    # Số sinh viên đăng ký mới theo tuần trong tháng đã chọn
    start_of_month = datetime(selected_year, selected_month, 1)
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    end_of_month = datetime(selected_year, selected_month, last_day, 23, 59, 59)
    
    # Lấy tất cả booking trong tháng
    bookings_this_month = Booking.query.filter(
        Booking.created_at >= start_of_month,
        Booking.created_at <= end_of_month
    ).order_by(Booking.created_at).all()
    
    # Chia theo tuần (7 ngày một tuần)
    week_counts = {}
    for booking in bookings_this_month:
        # Tính tuần thứ mấy trong tháng (bắt đầu từ ngày 1)
        day_of_month = booking.created_at.day
        week_number = ((day_of_month - 1) // 7) + 1
        week_label = f"Tuần {week_number}"
        week_counts[week_label] = week_counts.get(week_label, 0) + 1
    
    # Đảm bảo có đủ 4-5 tuần
    max_weeks = (last_day // 7) + (1 if last_day % 7 else 0)
    reg_labels = [f"Tuần {i+1}" for i in range(max_weeks)]
    reg_values = [week_counts.get(label, 0) for label in reg_labels]

    # Phòng trống vs đã có người
    occupied = Room.query.filter(Room.available < Room.capacity).count()
    empty = Room.query.filter(Room.available == Room.capacity).count()

    # Danh sách tháng và năm
    months = list(range(1, 13))
    years = list(range(2020, datetime.now().year + 2))

    return render_template(
        "admin/admin_dashboard.html",
        total_students=total_students,
        total_rooms=total_rooms,
        unpaid_bills=unpaid_bills,
        total_revenue=total_revenue,
        service_labels=service_labels,
        service_values=service_values,
        reg_labels=reg_labels,
        reg_values=reg_values,
        occupied=occupied,
        empty=empty,
        selected_month=selected_month,
        selected_year=selected_year,
        months=months,
        years=years
    )
#-------------------------------------------------------
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

# Xoá sinh viên khỏi phòng (kick)
@admin_bp.route("/rooms/<int:room_id>/kick/<int:booking_id>", methods=["POST"])
@login_required
def kick_student(room_id, booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.status != "active":
        flash("Sinh viên này không còn ở phòng.", "warning")
        return redirect(url_for("admin.room_detail", room_id=room_id))

    # Cập nhật trạng thái booking
    booking.status = "canceled"   # hoặc "finished" tuỳ quy ước
    booking.end_date = db.func.current_date()

    # Cập nhật phòng
    room = booking.room
    if room:
        room.available = room.available + 1

    db.session.commit()

    # Tạo thông báo cho sinh viên
    notif = Notification(
        user_id=booking.user_id,
        message=f"Bạn đã bị kích khỏi phòng {room.room_number}."
    )
    db.session.add(notif)
    db.session.commit()
    

    flash("Đã kick sinh viên ra khỏi phòng!", "success")
    return redirect(url_for("admin.room_detail", room_id=room_id))
#-------------------------------------------------------
# Quản lý đơn đăng ký
@admin_bp.route("/manage_applications")
@login_required
def manage_applications():
    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int, default=datetime.now().year)

    query = ApplicationRoom.query
    if month:
        query = query.filter(db.extract('month', ApplicationRoom.created_at) == month)
    if year:
        query = query.filter(db.extract('year', ApplicationRoom.created_at) == year)

    applications = query.order_by(ApplicationRoom.created_at.desc()).all()
    return render_template("admin/manage_applications.html", applications=applications, month=month, year=year)

# API: Lấy chi tiết 1 đơn (JSON) -> dùng AJAX gọi
@admin_bp.route("/api/application/<int:app_id>")
@login_required
def get_application_detail(app_id):
    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    app = ApplicationRoom.query.get_or_404(app_id)
    room = Room.query.get(app.room_id)

    data = {
        "id": app.id,
        "fullname": app.fullname,
        "student_id": app.student_id,
        "class_id": app.class_id,
        "citizen_id": app.citizen_id,
        "email": app.email,
        "phone_number": app.phone_number,
        "room": f"{room.block}{room.room_number} - {room.address}",
        "status": app.status,
        "created_at": app.created_at.strftime("%d/%m/%Y %H:%M"),
        "can_approve": app.status == "pending",
        "can_reject": app.status == "pending",
    }

    # Thêm chi tiết từ ApplicationRoom
    data.update({
        "address": app.address,
        "relative1_name": app.relative1_name,
        "relative1_phone": app.relative1_phone,
        "relative1_birthyear": app.relative1_birthyear,
        "relative2_name": app.relative2_name,
        "relative2_phone": app.relative2_phone,
        "relative2_birthyear": app.relative2_birthyear,
        "policy_type": app.policy_type,
        "policy_proof": app.policy_proof,
        "student_photo": app.student_photo,
        "citizen_proof": app.citizen_proof,
    })

    return jsonify(data)

# Duyệt đơn
@admin_bp.route("/application/<int:app_id>/approve")
@login_required
def approve_application(app_id):
    if current_user.role != "admin":
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("home"))

    application = ApplicationRoom.query.get_or_404(app_id)
    room = Room.query.get(application.room_id)

    # Kiểm tra phòng còn chỗ không
    if room.available <= 0:
        flash("Phòng đã hết chỗ, không thể duyệt đơn!", "danger")
        return redirect(url_for("admin.manage_applications"))

    # Kiểm tra đơn đã được xử lý chưa
    if application.status != "pending":
        flash("Đơn này đã được xử lý trước đó.", "info")
        return redirect(url_for("admin.manage_applications"))
    
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
        payment_method="cash",
        status="pending"   
    )

    db.session.add(payment)
    db.session.commit()

    # Tạo thông báo cho sinh viên
    notif = Notification(
    user_id=application.user_id,
    message=f"Đơn đăng ký phòng {room.room_number} của bạn đã được duyệt. Vui lòng thanh toán tiền cọc để hoàn tất."
    )
    db.session.add(notif)
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

    application = ApplicationRoom.query.get_or_404(app_id)
    if application.status != "pending":
        flash("Đơn này đã được xử lý trước đó.", "info")
        return redirect(url_for("admin.manage_applications"))

    application.status = "rejected"
    db.session.commit()

    # Tạo thông báo cho sinh viên
    notif = Notification(
    user_id=application.user_id,
    message=f"Đơn đăng ký phòng {application.room.room_number} của bạn đã bị TỪ CHỐI."
    )
    db.session.add(notif)
    db.session.commit()
    

    flash("Đơn đã bị từ chối.", "info")
    return redirect(url_for("admin.manage_applications"))

#-------------------------------------------------------
# Quản lý sinh viên
def normalize_text(s):
    """Bỏ dấu và chuyển thành lowercase"""
    if not s:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', s)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

@admin_bp.route("/students")
@login_required
def students():
    keyword = request.args.get("q", "").strip().lower()
    normalized_keyword = normalize_text(keyword)

    students = User.query.filter_by(role="student").all()
    data = []

    for s in students:
        # Ghép các trường để tìm một lần
        combined = f"{s.student_id} {s.fullname} {s.class_id} {s.citizen_id} {s.phone_number} {s.email or ''}"
        normalized_text = normalize_text(combined)

        if normalized_keyword in normalized_text or not keyword:
            booking = Booking.query.filter_by(user_id=s.id, status="active").first()
            room = Room.query.get(booking.room_id) if booking else None
            payments = Payment.query.filter_by(user_id=s.id).all()
            unpaid = [p for p in payments if p.status != "success"]

            data.append({
                "student": s,
                "room": room,
                "payments": payments,
                "unpaid": unpaid
            })

    return render_template("admin/students.html", students=data, keyword=keyword)

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

#-------------------------------------------------------
import random
# Quản lý hóa đơn
@admin_bp.route("/payments")
@login_required
def payments():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int, default=datetime.now().year)

    query = Payment.query
    if month:
        query = query.filter(db.extract('month', Payment.created_at) == month)
    if year:
        query = query.filter(db.extract('year', Payment.created_at) == year)

    payments = query.order_by(Payment.created_at.desc()).all()
    return render_template("admin/payments.html", payments=payments, month=month, year=year, current_time=datetime.now())

@admin_bp.route("/payments/<int:payment_id>/mark_paid", methods=["POST"])
@login_required
def mark_payment_paid(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = "success"
    db.session.commit()
    flash("Hóa đơn đã được xác nhận thanh toán!", "success")
    return redirect(url_for("admin.payments"))

# Tự động tạo hóa đơn tiền phòng, điện nước hàng tháng cho tất cả booking active
@admin_bp.route('/generate_bills', methods=['GET'])
def generate_bills():
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    bookings = Booking.query.filter_by(status="active").all()  
    new_bills = 0
    
    for booking in bookings:
        user = booking.user
        room = booking.room

        # Kiểm tra hóa đơn tháng này đã tồn tại chưa
        existing_bill = Payment.query.filter_by(
            room_id=room.id,
            user_id=user.id,
            month_paid=current_month,
            year_paid=current_year,
            service_type="utilities"
        ).first()

        if existing_bill:
            continue  # bỏ qua nếu đã có hóa đơn tháng này, hoặc vừa cọc phòng tháng này

        # Tạo số điện nước ngẫu nhiên
        electricity_usage = random.randint(30, 80)
        water_usage = random.randint(3, 10)  

        # tính tiền
        electricity_bill = room.price_electricity * electricity_usage 
        water_bill = room.price_water * water_usage               
        total_amount = room.price_room + electricity_bill + water_bill

        # Tạo hóa đơn mới
        new_payment = Payment(
            user_id=user.id,
            room_id=room.id,
            booking_id=booking.id,
            fullname=user.fullname,
            student_id=user.student_id,
            class_id=user.class_id,
            citizen_id=user.citizen_id,
            email=user.email,
            phone_number=user.phone_number,
            service_type="utilities",
            month_paid=current_month,
            year_paid=current_year,
            address=f"Ký túc xá {room.block}",
            block=room.block,
            room_number=room.room_number,
            amount=total_amount,
            payment_method="cash",
            status="pending"
        )

        db.session.add(new_payment)
        new_bills += 1

    db.session.commit()
    flash(f"Đã tạo {new_bills} hóa đơn mới cho tháng {current_month}/{current_year}", "success")
    return redirect(url_for('admin.payments'))

#-------------------------------------------------------
# Quản lý yêu cầu dịch vụ
@admin_bp.route("/services")
@login_required
def manage_services():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int, default=datetime.now().year)

    query = ServiceRequest.query
    if month:
        query = query.filter(db.extract('month', ServiceRequest.created_at) == month)
    if year:
        query = query.filter(db.extract('year', ServiceRequest.created_at) == year)

    service_requests = query.order_by(ServiceRequest.created_at.desc()).all()
    return render_template("admin/services.html", service_requests=service_requests, month=month, year=year)

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

    notif = Notification(
        user_id=req.user.id,
        message=f"Yêu cầu dịch vụ '{req.service_type}' của bạn đã được cập nhật thành '{status}'."
    )
    db.session.add(notif)
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

        notif = Notification(
            user_id=req.user.id,
            message=f"Dịch vụ '{req.service_type}' của bạn đã được báo giá {price:,}đ. Vui lòng kiểm tra chi tiết."
        )
        db.session.add(notif)
        db.session.commit()

    except Exception:
        db.session.rollback()
        flash("Có lỗi khi cập nhật giá!", "danger")

    return redirect(url_for("admin.manage_services"))

#-------------------------------------------------------
# Quản lý complain
@admin_bp.route("/complains")
@login_required
def manage_complains():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int, default=datetime.now().year)

    query = Complain.query
    if month:
        query = query.filter(db.extract('month', Complain.created_at) == month)
    if year:
        query = query.filter(db.extract('year', Complain.created_at) == year)
    complains = query.order_by(Complain.created_at.desc()).all()
    return render_template("admin/complains.html", complains=complains, month=month, year=year)

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

    notif = Notification(
        user_id=complain.user_id,
        message=f"Yêu cầu khiếu nại của bạn đã được đóng. Cảm ơn bạn đã phản hồi!"
    )
    db.session.add(notif)
    db.session.commit()


    flash("Đã phản hồi khiếu nại!", "success")
    return redirect(url_for("admin.manage_complains"))

#  Đóng complain
@admin_bp.route("/complains/<int:complain_id>/close", methods=["POST"])
@login_required
def close_complain(complain_id):
    complain = Complain.query.get_or_404(complain_id)
    complain.status = "closed"
    db.session.commit()

    flash("Đã đóng khiếu nại!", "success")
    return redirect(url_for("admin.manage_complains"))

#-------------------------------------------------------
#Announcement
@admin_bp.route("/announcements")
def manage_announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("admin/announcements.html", announcements=anns)

@admin_bp.route("/announcements/create", methods=["POST"])
def create_announcement():
    title = request.form.get("title")
    content = request.form.get("content")
    file = request.files.get("image")

    img_url = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER_ANNOUNCEMENTS"], filename)
        file.save(save_path)
        img_url = f"uploads/announcements/{filename}"

    ann = Announcement(title=title, content=content, image_url=img_url, admin_id=current_user.id)
    db.session.add(ann)
    db.session.commit()

    # Tạo thông báo cho tất cả sinh viên
    students = User.query.filter_by(role="student").all()
    for stu in students:
        notif = Notification(
            user_id=stu.id,
            message=f"Thông báo mới: {title}"
        )
        db.session.add(notif)
    db.session.commit()

    flash("Đã đăng thông báo!", "success")
    return redirect(url_for("admin.manage_announcements"))

@admin_bp.route("/announcements/<int:ann_id>")
def announcement_detail(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    return render_template("admin/announcement_detail.html", ann=ann)

# Sửa Announcement
@admin_bp.route("/announcements/<int:ann_id>/edit", methods=["GET", "POST"])
@login_required
def edit_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)

    if request.method == "POST":
        ann.title = request.form.get("title")
        ann.content = request.form.get("content")

        file = request.files.get("image")
        if file and file.filename != "":
            if file.filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]:
                filename = secure_filename(file.filename)
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER_ANNOUNCEMENTS"], filename)
                file.save(save_path)
                ann.image_url = f"uploads/announcements/{filename}"

        db.session.commit()
        flash("Cập nhật thông báo thành công!", "success")
        return redirect(url_for("admin.announcement_detail", ann_id=ann.id))

    return render_template("admin/edit_announcement.html", ann=ann)

# Xoá Announcement
@admin_bp.route("/announcements/<int:ann_id>/delete", methods=["POST"])
@login_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash("Đã xoá thông báo!", "success")
    return redirect(url_for("admin.manage_announcements"))
