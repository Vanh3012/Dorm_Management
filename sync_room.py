from app import app, db
from models import Room, Booking

if __name__ == "__main__":
    with app.app_context():
        print("🔄 Bắt đầu đồng bộ số chỗ trống (theo từng cơ sở)...")

        rooms = Room.query.all()
        for room in rooms:
            active_count = Booking.query.filter_by(room_id=room.id, status='active').count()
            room.available = max(room.capacity - active_count, 0)
            print(f" - {room.address} | {room.room_number}: còn {room.available} chỗ trống")

        db.session.commit()
        print("✅ Đồng bộ số chỗ trống thành công!")
