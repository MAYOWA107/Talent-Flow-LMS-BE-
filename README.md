# 📘 TalentFlow LMS API

A scalable Learning Management System (LMS) backend built with Django Rest Framework.  
This API powers an e-learning platform where instructors can create courses and students can enroll, learn, and submit assignments.

---

## 🚀 Features

- 🔐 JWT Authentication (Login & Register)
- 📧 Email Verification with OTP (Celery + Signals)
- 👨‍🏫 Instructor-only course creation & management
- 🎓 Student enrollment system
- 📊 Course progress tracking
- 📝 Assignment creation & submission
- ⏰ Deadline validation for assignments
- ⭐ Course reviews & dynamic rating system
- 🔒 Role-based permissions (Instructor / Student)
- ⚡ Optimized database queries
- 📄 Auto-generated API documentation (Swagger)

---

## 🛠 Tech Stack

- Python
- Django
- Django REST Framework
- Celery (Background Tasks)
- Redis (Message Broker)
- SQLite (can be switched to PostgreSQL)
- JWT Authentication (SimpleJWT)
- drf-yasg (Swagger API Docs)

---

## ⚙️ Architecture Highlights

### 🔁 Asynchronous Tasks (Celery)

- OTP emails are sent in the background using Celery
- Prevents blocking the main request-response cycle

### ⚡ Signals (Automation)

- Automatically creates OTP tokens when a user registers
- Triggers email sending without manual intervention

### 📧 Email Verification Flow

1. User registers
2. OTP token is created via Django signals
3. OTP email is sent asynchronously via Celery
4. User verifies account using OTP

---

## 📂 Project Structure



LMS_project/
│
├── account/
│ ├── signals.py # Auto OTP generation
│ ├── tasks.py # Celery email tasks
│
├── course/ # Courses & LMS logic
├── core/ # Shared utilities
├── manage.py

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Talent-Flow-LMS-BE-.git
cd Talent-Flow-LMS-BE-

### 2. Create Virtual environment
python -m venv venv
venv\Scripts\activate   # Windows


### 3. Install Dependencies
pip install -r requirements.txt


### 4. Create .env file and add the following
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_secret

### 5. Make sure Redis is runing(For Celery)
  redis-server


##W Run migration
python manage.py migrate


### Start Celery worker
  celery -A LMS_project worker -l info


📄 API Documentation (Swagger)
After running the server, access interactive API docs at:

  http://127.0.0.1:8000/swagger/


### Login uses JWT authentication and retun access and refresh token in json format
{
  "access": "your_access_token",
  "refresh": "your_refresh_token"
}


### Use token in your request
Authorization: Bearer your_access_token


📌 Key API Endpoints

Courses
| Method | Endpoint             | Description                     |
| ------ | -------------------- | ------------------------------- |
| GET    | /course/             | List all courses                |
| GET    | /course/{id}/        | Get course details              |
| POST   | /course/create/      | Create course (Instructor only) |
| PUT    | /course/{id}/update/ | Update course                   |
| DELETE | /course/{id}/delete/ | Delete course                   |


🎓 Enrollment
| Method | Endpoint             | Description          |
| ------ | -------------------- | -------------------- |
| POST   | /course/{id}/enroll/ | Enroll in course     |
| GET    | /course/my_courses   | Get enrolled courses |


📝 Assignments
| Method | Endpoint                                    | Description       |
| ------ | ------------------------------------------- | ----------------- |
| POST   | /course/{course_id}/assignment/create/      | Create assignment |
| GET    | /course/{course_id}/assignments/            | List assignments  |
| POST   | /course/{course_id}/{assignment_id}/submit/ | Submit assignment |


⭐ Reviews
| Method | Endpoint             | Description   |
| ------ | -------------------- | ------------- |
| POST   | /course/{id}/review/ | Add review    |
| PUT    | /review/{id}/update/ | Update review |
| DELETE | /review/{id}/delete/ | Delete review |



🧠 How It Works
 - Instructors create courses and assignments
 - Students enroll in courses
 - Students submit assignments before deadlines
 - Students leave reviews and ratings
 - Course ratings are calculated dynamically

🔒 Permissions
Only instructors can create/update/delete courses
Only enrolled students can access course content
Only owners can edit/delete their submissions or reviews

