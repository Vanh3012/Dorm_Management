# 🏫 Hệ Thống Quản Lý Ký Túc Xá (Dorm Management System)

Đây là dự án web **quản lý ký túc xá sinh viên**, được xây dựng bằng **Flask (Python)** và **MySQL**.
Ứng dụng cho phép sinh viên đăng ký phòng, gửi khiếu nại, thanh toán, và giúp admin quản lý phòng, người dùng, thông báo, v.v.

---

## ⚙️ 1️⃣ Chuẩn bị môi trường

### Yêu cầu cần có

* **Python ≥ 3.10**
* **MySQL Server** (đã cài và chạy)
* **Git** (để clone project)
* (Khuyến khích) **VS Code** để chạy và chỉnh sửa tiện hơn

> 💡 Kiểm tra nhanh:
>
> ```bash
> python --version
> mysql --version
> ```

---

## 📁 2️⃣ Tạo thư mục test project

Tạo một thư mục mới để test project từ đầu (mô phỏng người dùng mới):

### Windows:

```bash
cd D:\
mkdir <tên_thư_mục>
cd <tên_thư_mục>
```

### macOS/Linux:

```bash
mkdir ~/<tên_thư_mục>
cd ~/<tên_thư_mục>
```

---

## 📥 3️⃣ Clone project về máy

```bash
git clone https://github.com/Vanh3012/Dorm_Management.git
cd Dorm_Management
```

---

## 🧱 4️⃣ (Tùy chọn) Tạo môi trường ảo (virtual environment)

Giúp quản lý thư viện gọn gàng và không ảnh hưởng các project khác.

### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

> Khi kích hoạt thành công, bạn sẽ thấy đầu dòng terminal có `(venv)`.

---

## 📦 5️⃣ Cài các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Nếu không dùng môi trường ảo, bạn vẫn có thể chạy được — chỉ cần đảm bảo pip cài toàn cục.

> 💡 Nếu gặp lỗi `No module named 'flask'` hoặc tương tự → chạy lại lệnh trên.

---

## 🗄️ 6️⃣ Tạo database MySQL

Mở **MySQL Workbench** hoặc terminal MySQL rồi tạo database mới để test riêng:

```sql
CREATE DATABASE dorm_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🔐 7️⃣ Cấu hình file `.env`

Trong thư mục `Dorm_Management`, tạo file mới tên **`.env`** (nếu chưa có) hoặc mở file sẵn có rồi chỉnh lại:

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key

# Đường kết nối MySQL (đổi mật khẩu và tên DB nếu cần)
DATABASE_URL=mysql+mysqlconnector://root:mat_khau_database@localhost:3306/dorm_management
```

> ⚠️ Nếu mật khẩu MySQL chứa ký tự đặc biệt như `@`, hãy thay bằng `%40`.
> Ví dụ: `root:%40levietanh@localhost:3306/dorm_test`

---

## 🧬 8️⃣ Khởi tạo cấu trúc bảng trong database

```bash
flask db upgrade
```

Nếu thấy log như:

```
INFO  [alembic.runtime.migration] Running upgrade ...
```

→ Làm việc thành công ✅

> Nếu báo lỗi `Unknown database`, nghĩa là bạn chưa tạo DB ở bước 6.

---

## 👑 9️⃣ Tạo tài khoản admin mặc định

```bash
python create_admin.py
```

Nếu thành công, bạn sẽ thấy:

```
✅ Admin account created successfully!
```

Thông tin đăng nhập mặc định:

* Username: `admin`
* Password: `admin123`

---

## 🚀 🔟 Chạy ứng dụng web

```bash
flask run
```

Sau khi chạy, Flask sẽ in ra địa chỉ:

```
* Running on http://127.0.0.1:5000
```

Mở trình duyệt và truy cập:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

Nếu hiện giao diện đăng nhập hoặc trang chủ là OK 🎉

---

## 🔁 11️⃣ Lần sau muốn chạy lại web

Không cần cài đặt lại từ đầu.

### Nếu dùng môi trường ảo:

```bash
cd D:\dorm_test\Dorm_Management
venv\Scripts\activate
flask run
```

### Nếu không dùng môi trường ảo:

```bash
cd D:\dorm_test\Dorm_Management
flask run
```

Dữ liệu cũ trong MySQL vẫn còn nguyên.

---

## ❌ 12️⃣ Các lỗi thường gặp & cách khắc phục

| Lỗi                       | Nguyên nhân                              | Cách xử lý                                           |
| ------------------------- | ---------------------------------------- | ---------------------------------------------------- |
| `Unknown database`        | Chưa tạo DB hoặc sai tên DB trong `.env` | Tạo DB mới bằng Workbench / sửa `.env`               |
| `No module named 'flask'` | Chưa cài Flask                           | `pip install -r requirements.txt`                    |
| `Admin already exists`    | Đã chạy `create_admin.py` trước đó       | Không sao, admin đã có sẵn                           |
| Web hiện dữ liệu cũ       | `.env` vẫn trỏ DB cũ (`dorm_management`) | Đổi thành `dorm_test` và chạy lại `flask db upgrade` |
| Không gửi được mail       | Chưa cấu hình Gmail App Password         | Có thể tạm bỏ qua nếu chưa dùng tính năng gửi mail   |

---

## 🧹 13️⃣ Reset database test (nếu muốn làm mới hoàn toàn)

Mở MySQL Workbench và chạy:

```sql
DROP DATABASE dorm_test;
CREATE DATABASE dorm_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Sau đó chạy lại:

```bash
flask db upgrade
python create_admin.py
```

---

##  Mẹo thêm

* Có thể chạy app mà không cần venv nếu đã cài đủ thư viện toàn cục.
* Nếu muốn người khác truy cập web → cần deploy lên **Render / Railway / VPS**.
* Thư mục `static/img/room` sẽ tự tạo khi upload ảnh.

---

 **Tác giả:** Vanh 
 Dự án học tập: Quản lý ký túc xá bằng Flask + MySQL.
