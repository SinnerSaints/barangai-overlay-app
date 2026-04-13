# BarangAI Backend

A real-time AI support backend API for Barangay officials. This Django REST framework powers the BarangAI platform with intelligent features for lessons, assessments, quizzes, and progress tracking.

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** Django
- **API:** Django REST Framework
- **Authentication:** JWT (Simple JWT)
- **Deployment:** Railway
- **Database:** PostgreSQL (Production)

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/fuzziiz/BarangAI_Backend.git
cd BarangAI_Backend
```
### 2. Create Virutal Enivronment
```bash
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Apply Migrations
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000`

## API Endpoints
### Authentication (Accounts)
| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| `POST` | `/accounts/register` | Register a new user |
| `POST` | `/accounts/login` | Login |
| `GET` | `/accounts/users` | List all users (Admin) |
| `POST` | `/accounts/users/<id>/approve` | Approve user (Admin) |
| `PATCH` | `/accounts/users/<id>/update` | Update user profile |
| `DELETE` | `/accounts/users/<id>/delete` | Delete user (Admin) |
| `POST` | `/accounts/token/` | Obtain JWT token |
| `POST` | `/accounts/token/refresh` | Refresh JWT token |

### Lessons
| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| `GET` | `/lessons/` | Get all lessons |
| `GET` | `/lessons/<id>` | Get specific lesson |
| `POST` | `/lessons/<id>` | Create lesson |
| `PUT` | `/lessons/<id>` | Update lesson (Admin) |
| `DELETE` | `/lessons/<id>/` | Delete lesson (Admin) |
| `POST` | `/lessons/<id>/complete/` | Mark lesson complete |
| `GET` | `/lessons/progress/` | Get all topics progress |
| `GET` | `/lessons/progress/?topic-<topic_name>` | Get specific topic progress |

### Assessments
| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| `POST` | `/assessments/start/` | Start pre-assessment |
| `POST` | `/assessments/submit/` | Submit assessment |
| `GET` | `/assessments/result/` | Get assessment result |
| `GET` | `/assessments/status/` | Check assessment status |
| `POST` | `/assessments/create/` | Create assessment (Admin) |
| `GET` | `/assessments/list-assessment/` | List all assessment (Admin) |
| `GET` | `/assessments/list-assessment/<id>/` | Get specific assessment (Admin) |
| `PATCH` | `/assessments/list-assessment/<id>/` | Partial update assessment (Admin) |
| `PUT` | `/assessments/list-assessment/<id>/` | Full update assessment (Admin) |
| `DELETE` | `/assessments/list-assessment/<id>/` | Delete assessment (Admin) |

### Quizzes
| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| `GET` | `/quizzes/` | Get all quizzes |
| `GET` | `/quizzes/<id>/` | Get specific quiz |
| `POST` | `/quizzes/<id>/submit/` | Submit quiz |
| `GET` | `/quizzes/<id>/progress/` | Get quiz progress |
| `GET` | `/quizzes/admin/` | List all quizzes (Admin) |
| `POST` | `/quizzes/admin/` | Create quiz (Admin) |
| `PUT` | `/quizzes/admin/<id>/` | Update quiz (Admin) |
| `DELETE` | `/quizzes/admin/<id>/` | Delete quiz (Admin) |

## Authentication
All protected endpoints require JWT token in the Authorization header:
```bash
Authorization: Bearer <jwt_token>
```
Obtain a token by posting credentials to `/accounts/token/`

## Project Structure
```bash
BarangAI_Backend/
├── accounts/           # User authentication & management
├── lessons/            # Lesson content & progress tracking
├── assessments/        # Pre-assessments & evaluations
├── quizzes/            # Quiz management & attempts
├── progress/           # User progress tracking
├── barangai_backend/   # Django project settings
├── media/              # User uploads (avatars, etc.)
├── staticfiles/        # Static files (admin, DRF UI)
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── Procfile            # Heroku deployment config
```
## Features
- User authentication with JWT tokens
- Comprehensive lesson management with progress tracking
- Pre-assessments and quizzes with scoring
- Admin panel for content management
- Role-based access control
- Real-time progress updates