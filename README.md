# 🎥 Attend AI 🤖

### AI-Powered Smart Attendance System using Face Recognition

<p align="center">
  <img src="https://img.shields.io/badge/AI-Face%20Recognition-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-Flask-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-JavaScript-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey?style=for-the-badge" />
</p>

---

## 🚀 Overview

**Attend AI** is a real-time smart attendance system that uses **face recognition** to automatically mark attendance.
It replaces traditional manual attendance methods with an **AI-driven, efficient, and scalable solution**.

---

## ✨ Features

* 🎥 Real-Time Face Detection
* 🧠 Face Recognition with Name Identification
* 😊 Emotion Detection (Happy, Neutral, Sad, etc.)
* ⚡ Automatic Attendance Marking (Present/Absent)
* 📊 Attendance Analytics (Monthly Summary & Defaulters)
* 🔔 Notification System
* 🧾 Export Reports (CSV)
* 📁 Face Data Management

---

## 🏗️ Tech Stack

| Layer     | Technology                         |
| --------- | ---------------------------------- |
| Frontend  | HTML, CSS, JavaScript, face-api.js |
| Backend   | Flask (Python)                     |
| Database  | SQLite                             |
| Libraries | OpenCV, NumPy                      |

---

## 📂 Project Structure

```
Attend-AI/
│
├── app.py
├── database.py
├── face_utils.py
├── download_model.py
│
├── static/
│   └── models/
│
├── templates/
│   └── index.html
│
├── face_data/
├── attendance.db
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/Attend-AI.git
cd Attend-AI
```

---

### 2️⃣ Install Dependencies

```bash
pip install flask flask-cors opencv-python numpy
```

---

### 3️⃣ Download Models

```bash
python download_model.py
```

---

### 4️⃣ Run the Application

```bash
python app.py
```

---

### 5️⃣ Open in Browser

```
http://localhost:5000
```

---

## 🔐 Default Credentials

### 👨‍🏫 Teacher

```
ID: teacher1
Password: teacher123
```

### 👨‍🎓 Student

```
ID: <roll_number>
Password: student123
```

---

## 🧠 How It Works

1. 📸 Camera captures face in real-time
2. 🤖 Face is matched with stored dataset
3. ✅ Recognized → Marked Present
4. ❌ Not detected → Marked Absent (after session finalize)
5. 📊 Data stored for analytics & reports

---

## 📊 Future Enhancements

* 🔐 JWT Authentication
* 🎥 Live Attendance Mode
* 🧠 Anti-Spoofing (Blink Detection)
* ☁️ Cloud Deployment
* 📱 Mobile App Integration



<p align="center">
  <b>🚀 Turning traditional attendance into intelligent automation using AI</b>
</p>
