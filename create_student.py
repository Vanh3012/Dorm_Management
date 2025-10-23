from app import app, db
from models.user import User
from datetime import date

with app.app_context():
    User.query.filter(User.id > 4).delete()
    db.session.commit()

    ustu = [
        ("Nguyễn Văn An", "nguyenvanan", "2003-02-14", "B23DCCN091", "D23CQCN01-B", "nvan@gmail.com", "012345678901", "0912345678"),
        ("Trần Thị Bình", "tranthibinh", "2003-05-21", "B23DCCN002", "D23CQCN01-B", "ttb@gmail.com", "012345678902", "0912345679"),
        ("Lê Văn Cường", "levancuong", "2003-08-10", "B23DCCN123", "D23CQCN01-B", "lvc@gmail.com", "012345678903", "0912345680"),
        ("Phạm Thị Dung", "phamthidung", "2003-03-30", "B23DCCN004", "D23CQCN02-B", "ptd@gmail.com", "012345678904", "0912345681"),
        ("Hoàng Văn Em", "hoangvanem", "2003-09-02", "B23DCCN005", "D23CQCN02-B", "hve@gmail.com", "012345678905", "0912345682"),
        ("Đỗ Thị Hoa", "dothihoa", "2003-12-12", "B23DCCN006", "D23CQCN02-B", "dth@gmail.com", "012345678906", "0912345683"),
        ("Nguyễn Văn Huy", "nguyenvanhuy", "2003-04-25", "B23DCCN007", "D23CQCN03-B", "nvh@gmail.com", "012345678907", "0912345684"),
        ("Trần Thị Kim", "tranthikim", "2003-06-18", "B23DCCN008", "D23CQCN03-B", "ttk@gmail.com", "012345678908", "0912345685"),
        ("Lê Văn Long", "levanlong", "2003-01-09", "B23DCCN009", "D23CQCN03-B", "lvl@gmail.com", "012345678909", "0912345686"),
        ("Phạm Thị Mai", "phamthimai", "2003-07-27", "B23DCCN010", "D23CQCN04-B", "ptm@gmail.com", "012345678910", "0912345687"),
    ]

    for u in ustu:
        student = User(
            fullname=u[0],
            username=u[1],
            date_of_birth=u[2],
            student_id=u[3],
            class_id=u[4],
            email=u[5],
            citizen_id=u[6],
            phone_number=u[7],
        )
        student.role = "student"
        student.set_password('123456')
        db.session.add(student)

    db.session.commit()
    print("thành công!")