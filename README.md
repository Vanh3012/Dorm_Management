# 🏫 Hệ Thống Quản Lý Ký Túc Xá (Dorm Management System)

Đây là dự án web **quản lý ký túc xá sinh viên**, được xây dựng bằng **Flask (Python)** và **MySQL**.
Ứng dụng giúp sinh viên đăng ký phòng, nộp tiền, gửi phản ánh và giúp admin quản lý phòng, hóa đơn, khiếu nại, thông báo, v.v.

---

## ⚙️ 1. Yêu cầu môi trường

Để chạy được dự án này, máy tính của bạn cần có:

* **Python** ≥ 3.10
* **MySQL Server** (đã cài đặt và chạy)
* **Git** (để clone project)

> 💡 Kiểm tra nhanh:
>
> ```bash
> python --version
> mysql --version
> ```

---

## 🚀 2. Tải mã nguồn về

```bash
git clone https://github.com/Vanh3012/Dorm_Management.git
cd Dorm_Management
```

---

## 🧩 3. Tạo môi trường ảo và cài thư viện

```bash
python -m venv venv
venv\Scripts\activate      # (Windows)
# source venv/bin/activate  # (macOS/Linux)

pip install -r requirements.txt
```

> ⚠️ Nếu cài bị lỗi liên quan đến MySQL, hãy chắc rằng bạn đã cài **mysql-connector-python** (đã có sẵn trong file requirements.txt).

---

## 🧱 4. Tạo cơ sở dữ liệu MySQL

Mở **MySQL Workbench** hoặc **MySQL Command Line**, rồi chạy lệnh sau:

```sql
CREATE DATABASE dorm_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🔐 5. Tạo file `.env`

Trong thư mục chính của project, tạo file tên `.env` và dán nội dung ví dụ sau:

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=supersecretkey

# Đường dẫn kết nối MySQL (sửa username, password nếu khác)
DATABASE_URL=mysql+mysqlconnector://root:matkhau@localhost:3306/dorm_management
```

> ⚠️ Nếu mật khẩu MySQL của bạn có ký tự đặc biệt (ví dụ `@`), hãy mã hóa bằng **URL encoding**.
> Ví dụ: `@` → `%40` → `root:%40Anh3112005@localhost:3306/dorm_management`

---

## 🗄️ 6. Khởi tạo database (tạo bảng)

Sau khi đã có `.env`, chạy lệnh:

```bash
flask db upgrade
```

> 💡 Nếu gặp lỗi `Unknown database 'dorm_management'` → bạn chưa tạo database ở bước 4.

---

## 👑 7. Tạo tài khoản admin mặc định

Sau khi migrate xong, chạy file tạo admin:

```bash
python create_admin.py
```

Nếu thành công, bạn sẽ thấy:

```
✅ Admin account created successfully!
```

> Thông tin mặc định:
>
> * Username: `admin`
> * Password: `admin123`
> * Email: `admin@example.com`

---

## 🌐 8. Chạy ứng dụng

```bash
flask run
```

Sau khi chạy, mở trình duyệt tại:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

Nếu bạn thấy giao diện đăng nhập / trang chủ → nghĩa là setup thành công 🎉

---

## 🧰 9. Một số lỗi thường gặp

| Lỗi                                  | Nguyên nhân                          | Cách khắc phục                             |
| ------------------------------------ | ------------------------------------ | ------------------------------------------ |
| `ModuleNotFoundError`                | Chưa cài đủ thư viện                 | `pip install -r requirements.txt`          |
| `Unknown database`                   | Chưa tạo DB MySQL                    | Tạo DB bằng câu lệnh `CREATE DATABASE ...` |
| `RuntimeError: No application found` | Thiếu biến `FLASK_APP`               | Thêm dòng `FLASK_APP=app.py` vào `.env`    |
| `Admin already exists!`              | Chạy lại `create_admin.py` nhiều lần | Không cần lo, chỉ tạo admin một lần        |

---

## 💡 10. Tóm tắt nhanh (dành cho người quen Flask)

```bash
git clone https://github.com/Vanh3012/Dorm_Management.git
cd Dorm_Management
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
CREATE DATABASE dorm_management;
flask db upgrade
python create_admin.py
flask run
```

👉 Mở: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ✨ Ghi chú

* Khi chạy lần đầu, project sẽ tự tạo thư mục upload nếu chưa có.
* Nếu muốn tắt chế độ debug, sửa trong `.env`: `FLASK_ENV=production`.
* Có thể deploy dễ dàng lên **Render**, **Railway**, hoặc **PythonAnywhere**.

---

💬 **Tác giả:** Vanh
Dự án phục vụ mục đích học tập và thực hành web full-stack bằng Flask + MySQL.
