# 🎥 Attend AI 🤖

### AI-Powered Smart Attendance System using Face Recognition

<p align="center">
  <img src="https://img.shields.io/badge/AI-Face%20Recognition-blue?style=for-the-badge&logo=ai" />
  <img src="https://img.shields.io/badge/Backend-Flask-green?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Frontend-JavaScript-yellow?style=for-the-badge&logo=javascript" />
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey?style=for-the-badge&logo=sqlite" />
</p>

<p align="center">
  🚀 Turning traditional attendance into intelligent automation
</p>

---

## 📌 Overview

**Attend AI** is a smart AI-based attendance system that uses **real-time face recognition** to automate attendance tracking.
It eliminates manual effort and introduces a seamless, intelligent, and scalable solution for classrooms and institutions.

---

## 🎯 Key Features

* 🎥 Real-Time Face Detection
* 🧠 Face Recognition with Name Identification
* 😊 Emotion Detection (Happy, Neutral, Sad, etc.)
* ⚡ Smart Attendance Marking (Present/Absent)
* 📊 Analytics Dashboard (Defaulters & Monthly Reports)
* 🔔 Notification System
* 🧾 Export Reports (CSV)
* 📁 Face Data Management

---

## 🏗️ Tech Stack

| Category  | Technology                         |
| --------- | ---------------------------------- |
| Frontend  | HTML, CSS, JavaScript, face-api.js |
| Backend   | Flask (Python)                     |
| Database  | SQLite                             |
| Libraries | OpenCV, NumPy                      |

---

## 📂 Project Structure

```bash
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

## ⚙️ Setup Instructions

### 🔹 1. Clone Repository

```bash
git clone https://github.com/your-username/Attend-AI.git
cd Attend-AI
```

### 🔹 2. Install Dependencies

```bash
pip install flask flask-cors opencv-python numpy
```

### 🔹 3. Download Face Models

```bash
python download_model.py
```

### 🔹 4. Run Application

```bash
python app.py
```

### 🔹 5. Open in Browser

```
http://localhost:5000
```

---

## 🔐 Default Credentials

| Role    | ID       | Password   |
| ------- | -------- | ---------- |
| Teacher | teacher1 | teacher123 |
| Student | roll_no  | student123 |

---

## 🧠 How It Works

1. 📸 Camera captures faces in real-time
2. 🤖 AI model detects & recognizes faces
3. ✅ Recognized → Marked Present
4. ❌ Not detected → Marked Absent
5. 📊 Data stored for analytics

---

## 📸 Demo (Add Screenshots/GIF)

> Add screenshots or demo video here for better visibility 👇

```
![Demo](your-demo-link-here)
```

---

## 👨‍💻 Contributors

| Name  | GitHub                |
| ----- | --------------------- |
| Yash  | @Yashrawal03          |
| Diggy | @chouhandrs864-dotcom |

---

## 🚀 Future Enhancements

* 🔐 JWT Authentication
* 🎥 Live Attendance Mode
* 🧠 Anti-Spoofing Detection
* ☁️ Cloud Deployment
* 📱 Mobile App Integration

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!

---

<p align="center">
  Made with ❤️ by Team Attend AI
</p>
