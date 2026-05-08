# Videoflix Backend (Django REST Framework)

Backend API for the Videoflix frontend.  
Videoflix is an educational video streaming project with user authentication, email-based account activation, password reset flow, protected video endpoints, asynchronous video processing, and HLS streaming.

- [Tech Stack](tech-stack)
- [Key Concepts](#key-concepts)
- [API Base URL](#api-base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Video Processing Flow](#video-processing)
- [Data Model](#data-model)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Setup with Docker Compose](#setup-with-docker-compose)
- [Production Deployment Notes](#production-deployment-notes)
- [Useful Commands](#useful-commands)
- [Frontend Integration](#frontend-integration)
- [Security Notes](#security-notes)
- [Project Status](#project-status)
- [License](#license)

License Project Status Security Notes Frontend Integration
Useful Commands

## Tech Stack

- Python
- Django
- Django REST Framework (DRF)
- Simple JWT
- Cookie-based authentication with HTTP-only cookies
- PostgreSQL
- Redis
- Django RQ
- FFmpeg
- Gunicorn
- Nginx
- django-cors-headers
- Pillow
- python-dotenv

## Key Concepts

- Custom user model using email as the login identifier
- Account registration with email activation
- Login via JWT access and refresh tokens stored in HTTP-only cookies
- Password reset via email token link
- Protected API endpoints for authenticated users
- Video upload through the Django admin
- Automatic background processing after video upload
- FFmpeg-based thumbnail generation
- HLS video generation in multiple resolutions:
  - 480p
  - 720p
  - 1080p
- Master playlist generation for adaptive streaming
- Redis-backed Django RQ worker for long-running video processing jobs
- PostgreSQL database for production-ready persistence

## API Base URL

Local development:

```text
http://127.0.0.1:8000/api/
```

Production example:

```text
https://api.videoflix.saschaheinze.de/api/
```

## Authentication

This project uses JWT authentication with HTTP-only cookies.

After a successful login, the backend sets:

```text
access_token
refresh_token
```

Protected endpoints read the access token from the cookie. The frontend does not need to store tokens in localStorage or sessionStorage.

## Endpoints

### Auth

#### POST /api/register/

Creates a new inactive user account and sends an activation email.

Request:

```json
{
  "email": "user@example.com",
  "password": "your_password",
  "confirmed_password": "your_password"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "activation_token"
}
```

Notes:

- The user is inactive until the account is activated.
- The activation link is sent via email.
- If email delivery fails, the registration is rolled back.

#### GET /api/activate/&lt;uidb64&gt;/&lt;token&gt;/

Activates a registered user account.

Success response:

```json
{
  "message": "Account successfully activated."
}
```

#### POST /api/login/

Logs in an activated user and sets authentication cookies.

Request:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:

```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user@example.com"
  }
}
```

#### POST /api/logout/

Logs out the user, deletes authentication cookies and invalidates the refresh token.

Response:

```json
{
  "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
}
```

#### POST /api/token/refresh/

Refreshes the access token by using the refresh token cookie.

Response:

```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

#### POST /api/password_reset/

Sends a password reset email if the email address belongs to an existing user.

Request:

```json
{
  "email": "user@example.com"
}
```

Response:

```json
{
  "detail": "An email has been sent to reset your password."
}
```

Note: The response is intentionally the same whether the email exists or not.

#### POST /api/password_confirm/&lt;uidb64&gt;/&lt;token&gt;/

Sets a new password after a valid password reset request.

Request:

```json
{
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

Response:

```json
{
  "detail": "Your Password has been successfully reset."
}
```

### Videos

#### GET /api/video/

Returns all processed videos that are ready for streaming.

Auth required.

Response:

```json
[
  {
    "id": 1,
    "created_at": "2026-05-06T14:00:00Z",
    "title": "Example Video",
    "description": "Example description",
    "thumbnail_url": "https://api.example.com/media/thumbnails/video_1.jpg",
    "category": "Drama"
  }
]
```

Notes:

- Only videos with `processing_status = ready` are returned.
- Videos that are still processing or failed are hidden from the public list.

#### GET /api/video/&lt;movie_id&gt;/master.m3u8

Returns the HLS master playlist for a video.

Auth required.

Content-Type:

```text
application/vnd.apple.mpegurl
```

#### GET /api/video/&lt;movie_id&gt;/&lt;resolution&gt;/index.m3u8

Returns the HLS playlist for one specific resolution.

Auth required.

Example:

```text
/api/video/1/720p/index.m3u8
```

Content-Type:

```text
application/vnd.apple.mpegurl
```

#### GET /api/video/&lt;movie_id&gt;/&lt;resolution&gt;/&lt;segment&gt;/

Returns a single HLS video segment.

Auth required.

Example:

```text
/api/video/1/720p/segment_000.ts/
```

Content-Type:

```text
video/MP2T
```

## Video Processing Flow

```text
1. Admin uploads a video file
2. Django saves the Video object with status pending
3. A post_save signal enqueues a background job
4. Django RQ worker starts processing the video
5. FFmpeg creates a thumbnail
6. FFmpeg creates HLS streams for 480p, 720p and 1080p
7. A master.m3u8 playlist is generated
8. The video status is set to ready
9. The video becomes available via /api/video/
```

If processing fails, the video status is set to `failed` and the error is stored in `processing_error`.

## Data Model

### User

- Email-based custom user model
- Uses email as `USERNAME_FIELD`
- Supports inactive users before activation
- Supports Django permissions and admin access

### Video

- Title
- Description
- Category
- Source file
- Thumbnail
- Processing status
- Processing error
- Created timestamp
- Updated timestamp

Processing statuses:

```text
pending
processing
ready
failed
```

## Project Structure

```text
videoflix-backend/
├─ authentication/                    Custom user model and authentication API
│  ├─ api/
│  │  ├─ serializers.py               Register, login and password serializers
│  │  ├─ urls.py                      Auth endpoint routes
│  │  ├─ utils.py                     Token and email helper functions
│  │  └─ views.py                     Auth API views
│  ├─ tests/
│  │  ├─ __init__.py
│  │  ├─ test_happy.py
│  │  └─ test_unhappy.py
│  ├─ authentication.py               Cookie JWT authentication class
│  ├─ admin.py
│  ├─ apps.py
│  └─ models.py                       Custom User and UserManager
│
├─ content/                           Video domain and streaming API
│  ├─ api/
│  │  ├─ serializers.py               Video response serializer
│  │  ├─ urls.py                      Video and HLS routes
│  │  └─ views.py                     Video list and HLS file responses
│  ├─ tests/
│  │  ├─ __init__.py
│  │  ├─ test_happy.py
│  │  └─ test_unhappy.py
│  ├─ admin.py                        Video admin configuration
│  ├─ apps.py
│  ├─ models.py                       Video model
│  ├─ signals.py                      Starts video processing jobs
│  └─ tasks.py                        FFmpeg thumbnail and HLS processing
│
├─ core/                              Django project configuration
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py
│  └─ wsgi.py
│
├─ backend.Dockerfile
├─ backend.entrypoint.sh
├─ docker-compose.yml
├─ manage.py
├─ requirements.txt
├─ .env.template
├─ .gitignore
└─ README.md
```

## Environment Variables

Create a `.env` file based on `.env.template`.

Example for production-like deployment:

```env
SECRET_KEY=your_secret_key
DEBUG=False

ALLOWED_HOSTS=api.videoflix.example.com,localhost,127.0.0.1

CORS_ALLOWED_ORIGINS=https://videoflix.example.com
CSRF_TRUSTED_ORIGINS=https://videoflix.example.com,https://api.videoflix.example.com

FRONTEND_URL=https://videoflix.example.com

AUTH_COOKIE_SECURE=True

DB_NAME=videoflix
DB_USER=videoflix_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_app_password
DEFAULT_FROM_EMAIL=your_email@example.com
```

Do not commit real secrets to Git.

## Setup with Docker Compose

### 1) Clone repository

```bash
git clone https://github.com/codebySaschaHeinze/videoflix-backend.git
cd videoflix-backend
```

### 2) Create environment file

```bash
cp .env.template .env
```

Adjust the values in `.env`.

### 3) Build and start containers

```bash
docker compose up --build
```

The backend will be available at:

```text
http://127.0.0.1:8000/api/
```

### 4) Run tests inside the container

```bash
docker compose exec web python manage.py test
```

## Setup without Docker

### 1) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Install system dependencies

FFmpeg and Redis are required for video processing.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg redis-server postgresql postgresql-contrib
```

### 4) Run migrations

```bash
python manage.py migrate
```

### 5) Create superuser

```bash
python manage.py createsuperuser
```

### 6) Start development server

```bash
python manage.py runserver
```

### 7) Start RQ worker

In a second terminal:

```bash
python manage.py rqworker default
```

## Running Tests

```bash
python manage.py test
```

Current test coverage includes happy and unhappy path tests for authentication and content endpoints.

## Production Deployment Notes

This project can be deployed with:

- Gunicorn as WSGI server
- Nginx as reverse proxy
- PostgreSQL as database
- Redis as message broker
- Django RQ worker as a separate systemd service
- Nginx serving `/static/` and `/media/`
- HTTPS via Certbot

Example service layout:

```text
Nginx
  → Gunicorn on 127.0.0.1:8003
  → Django backend
  → PostgreSQL
  → Redis
  → RQ worker
  → FFmpeg processing
```

Important production settings:

```text
DEBUG=False
AUTH_COOKIE_SECURE=True
HTTPS enabled
static files collected
media directory writable by the Django/RQ process
```

## Useful Commands

Run migrations:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Run tests:

```bash
python manage.py test
```

Start RQ worker manually:

```bash
python manage.py rqworker default
```

Check generated media files:

```bash
find media -maxdepth 5 -type f
```

Check production service logs:

```bash
sudo journalctl -u videoflix -n 50 --no-pager
sudo journalctl -u videoflix-rqworker -n 50 --no-pager
```

## Frontend Integration

The frontend should point to the backend API base URL:

```javascript
const API_BASE_URL = "https://api.videoflix.example.com/api/";
```

For cookie-based authentication, frontend requests to protected endpoints must include credentials:

```javascript
fetch(url, {
  credentials: "include",
});
```

## Security Notes

- JWT tokens are stored in HTTP-only cookies.
- Access to video endpoints requires authentication.
- Passwords are stored hashed by Django.
- Password reset responses do not reveal whether an email exists.
- Production cookies should use `Secure`.
- Real secrets must never be committed to the repository.

## Project Status

Implemented:

- Email-based registration
- Account activation by email
- Login and logout with HTTP-only JWT cookies
- Refresh token flow
- Password reset and password confirmation
- Protected video list endpoint
- Protected HLS playlist and segment endpoints
- Video upload through Django admin
- Asynchronous video processing with Django RQ
- FFmpeg thumbnail generation
- FFmpeg HLS generation for 480p, 720p and 1080p
- Master playlist generation
- Happy and unhappy path tests

## License

Educational project. Adjust the license information as needed before publishing or reusing this project.
