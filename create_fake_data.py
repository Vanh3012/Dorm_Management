import random
from datetime import datetime, timedelta
from extensions import db
from app import app
from models import ApplicationRoom, Booking, Payment, ServiceRequest

# ====== CONFIG ======
NUM_REQUESTS = 100  # số yêu cầu dịch vụ giả
MONTHS = list(range(10, 13)) + list(range(1, 11))  # từ 10/2024 đến 10/2025
YEARS = [2024, 2025]
# =====================

def random_date(base_date, days_range=10):
    """Sinh ngày ngẫu nhiên cách base_date vài ngày"""
    return base_date + timedelta(days=random.randint(3, days_range))

def create_bookings():
    print("📦 Tạo booking từ application_rooms...")

    applications = ApplicationRoom.query.filter(
        ApplicationRoom.status.in_(["completed", "approved_pending_deposit"])
    ).all()

    bookings = []
    for app_item in applications:
        start_date = random_date(app_item.created_at, days_range=15)
        booking = Booking(
            user_id=app_item.user_id,
            room_id=app_item.room_id,
            application_id=app_item.id,
            start_date=start_date,
            status="active",
            created_at=app_item.created_at
        )
        bookings.append(booking)

    db.session.bulk_save_objects(bookings)
    db.session.commit()
    print(f"✅ Đã tạo {len(bookings)} booking.")
    return bookings


def create_payments(bookings):
    print("💰 Tạo dữ liệu Payment giả...")

    payments = []
    for booking in bookings:
        for _ in range(random.randint(4, 12)):  # mỗi sinh viên có 4–12 hóa đơn
            year = random.choice(YEARS)
            month = random.choice(MONTHS)
            service = random.choice(["rent", "electricity", "water", "service_fee"])

            if service == "rent":
                amount = random.randint(900000, 1600000)
            elif service == "electricity":
                amount = random.randint(100000, 250000)
            elif service == "water":
                amount = random.randint(50000, 150000)
            else:  # service_fee
                amount = random.randint(30000, 100000)

            pay_date = datetime(year, month, random.randint(1, 28))
            payment = Payment(
                room_id=booking.room_id,
                user_id=booking.user_id,
                service_type=service,
                amount=amount,
                month_paid=month,
                year_paid=year,
                status=random.choice(["success", "pending"]),
                created_at=pay_date
            )
            payments.append(payment)

    db.session.bulk_save_objects(payments)
    db.session.commit()
    print(f"✅ Đã tạo {len(payments)} hóa đơn giả (trải nhiều tháng 2024–2025).")


def create_service_requests(bookings):
    print("🧰 Tạo dữ liệu ServiceRequest giả...")

    if not hasattr(ServiceRequest, "description"):
        print("⚠️ Bỏ qua vì bảng service_requests chưa có.")
        return

    reasons = [
        "Hỏng quạt trần",
        "Rò nước nhà tắm",
        "Bóng đèn cháy",
        "Khóa cửa hư",
        "Điện yếu",
        "Máy nước nóng không hoạt động",
        "Dọn rác phòng",
        "Cửa sổ vỡ kính"
    ]

    requests = []
    for booking in random.sample(bookings, min(NUM_REQUESTS, len(bookings))):
        month = random.choice(MONTHS)
        year = random.choice(YEARS)
        req = ServiceRequest(
            room_id=booking.room_id,
            user_id=booking.user_id,
            description=random.choice(reasons),
            status=random.choice(["pending", "completed"]),
            created_at=datetime(year, month, random.randint(1, 28))
        )
        requests.append(req)

    db.session.bulk_save_objects(requests)
    db.session.commit()
    print(f"✅ Đã tạo {len(requests)} yêu cầu dịch vụ giả.")


if __name__ == "__main__":
    with app.app_context():
        print("🚀 Bắt đầu tạo dữ liệu giả Dorm_Management...\n")

        bookings = create_bookings()
        create_payments(bookings)
        create_service_requests(bookings)

        print("\n🎉 Hoàn tất tạo dữ liệu giả thành công — dashboard sẽ cực sinh động!")
