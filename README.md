# 🏩 Dorm Management System (KTX_Management)

A complete **Dormitory Management System** built with **Flask**, **SQLAlchemy**, and **MySQL**.
This project allows students to register dorm rooms, submit complaints, and helps admins manage rooms, bookings, and payments efficiently.

---

## 🚀 Features

### 👩‍🎓 Student

- Register & login securely
- View available dorm rooms with details and images
- Apply for room registration
- Submit complaints with image attachments
- View payment status and booking history

### 👨‍💼 Admin

- Manage students and user accounts
- Add, edit, or delete rooms
- Approve or reject dorm applications
- Handle maintenance complaints
- Track payments and room occupancy

---

## 🧱 Tech Stack

| Layer          | Technologies                |
| -------------- | --------------------------- |
| **Backend**    | Flask, SQLAlchemy, Alembic  |
| **Frontend**   | HTML, Tailwind CSS          |
| **Database**   | MySQL                       |
| **Mailing**    | Gmail SMTP / Mailtrap       |
| **Deployment** | Render / Railway (optional) |

---

## 🗂️ Project Structure

```
Dorm_Management/
│
├── app.py
├── .env
├── requirements.txt
├── .gitignore
│
├── blueprints/
│   ├── auth/
│   │   ├── routes.py
│   │   └── forms.py
│   ├── student/
│   ├── admin/
│   └── ...
│
├── models/
│   ├── user.py
│   ├── room.py
│   ├── booking.py
│   ├── complain.py
│   ├── payment.py
│   └── __init__.py
│
├── migrations/
│   └── versions/
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── reset_password.html
│   └── ...
│
└── static/
    ├── css/
    ├── js/
    └── img/room/
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone the repository

```
git clone https://github.com/Vanh3012/Dorm_Management.git
cd Dorm_Management
```

### 2️⃣ Create virtual environment

```
python -m venv venv
venv\Scripts\activate        # on Windows
# source venv/bin/activate   # on macOS/Linux
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Create .env file

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key

# Database
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost/dorm_management
```

### 5️⃣ Initialize the database

```
flask db upgrade
```

### 6️⃣ Run the app

```
flask run
```

Now open in your browser:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧾 Default Roles

| Role        | Description                                |
| ----------- | ------------------------------------------ |
| **Admin**   | Full control of dorm management            |
| **Student** | Can view rooms, apply, and file complaints |

---

## 📸 Screenshots (add later)

![Homepage Screenshot](static/img/room/home.png)
![Admin Dashboard](static/img/room/dashboard.png)

---

## 👨‍💻 Contributors

| Name                                    | Role                                |
| --------------------------------------- | ----------------------------------- |
| **Vanh**                                | Project Owner / Fullstack Developer |
| _(Add teammates here if group project)_ |                                     |

---

## 🧠 Future Improvements

- Add real-time chat between students and admins
- Implement automatic room availability updates
- Add export reports (CSV / Excel) for admin dashboard
- Integrate payment gateway (VNPay, Momo)

---

## 🛄 Deployment (optional)

You can deploy on **Render** or **Railway** for free.

### Render setup:

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Add environment variables from `.env`
4. Set **Start Command:**

```
gunicorn app:app
```

---

## 🖋️ License

This project is open-source and free for educational use.

---

💬 **Developed by Vanh — PTIT Student**
_A modern dormitory management system built with Flask + Tailwind CSS._
