# 📚 FazeSoft-EMS Backend — API Endpoints Reference

> **Base URL:** `http://localhost:8000`
> **Production:** `https://faze-soft-ems-backend.vercel.app`
> **Interactive Docs:** [`/docs`](/docs) | [`/redoc`](/redoc)

> Every endpoint below shows the exact **Request** to copy into Postman. Replace `<token>` with the Bearer token from login.

---

## 🏠 Health Check

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/` | ❌ | API status check |
| `GET` | `/health` | ❌ | Health check endpoint |

---

### GET /
**Request**
```
GET http://localhost:8000/
Content-Type: application/json
```

**Response (200):**
```json
{
  "status": "ok",
  "message": "HireMate API is running 🚀"
}
```

---

### GET /health
**Request**
```
GET http://localhost:8000/health
Content-Type: application/json
```

**Response (200):**
```json
{
  "status": "healthy"
}
```

---

## 🔐 Authentication

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/api/auth/signup` | ❌ | Register a new user |
| `POST` | `/api/auth/login` | ❌ | Login with credentials |
| `POST` | `/api/auth/create-employee` | ❌ | Create employee login account |
| `GET` | `/api/auth/me` | ✅ | Get current authenticated user |

---

### POST /api/auth/signup
**Request**
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "employee",
    "phone": null,
    "location": null,
    "job_title": null,
    "bio": null,
    "avatar": null,
    "is_active": true,
    "created_at": "2026-08-10T12:00:00"
  }
}
```

**Errors:**
- `409` — Email already exists

---

### POST /api/auth/login
**Request**
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "employee",
    "phone": "+1234567890",
    "location": "New York",
    "job_title": "Software Engineer",
    "bio": "Experienced developer",
    "avatar": "https://example.com/avatar.jpg",
    "is_active": true,
    "created_at": "2026-08-10T12:00:00"
  }
}
```

**Errors:**
- `401` — Incorrect email or password
- `403` — Account has been deactivated

---

### POST /api/auth/create-employee
**Request**
```
POST http://localhost:8000/api/auth/create-employee
Content-Type: application/json

Body:
{
  "email": "employee@example.com",
  "password": "securepass123",
  "full_name": "Jane Smith",
  "job_title": "Frontend Developer"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "employee@example.com",
  "full_name": "Jane Smith",
  "role": "employee",
  "job_title": "Frontend Developer",
  "phone": null,
  "location": null,
  "bio": null,
  "avatar": null,
  "is_active": true,
  "created_at": "2026-08-10T12:30:00"
}
```

**Errors:**
- `409` — Email already exists

---

### GET /api/auth/me
**Request**
```
GET http://localhost:8000/api/auth/me
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "hr",
  "phone": "+1234567890",
  "location": "New York",
  "job_title": "HR Manager",
  "bio": "Managing talent acquisition",
  "avatar": "https://example.com/avatar.jpg",
  "is_active": true,
  "created_at": "2026-08-10T12:00:00"
}
```

---

## 👥 Candidates

| Method | Endpoint | Auth Required | Role Required | Description |
|--------|----------|---------------|---------------|-------------|
| `GET` | `/api/candidates` | ✅ | Any | List candidates |
| `POST` | `/api/candidates` | ✅ | Any* | Create candidate |
| `GET` | `/api/candidates/{id}` | ✅ | Any* | Get candidate details |
| `PUT` | `/api/candidates/{id}` | ✅ | Any* | Update candidate |
| `PATCH` | `/api/candidates/{id}/status` | ✅ | HR/Admin | Update pipeline status |
| `DELETE` | `/api/candidates/{id}` | ✅ | HR/Admin | Delete candidate |

> \* Candidates can only view/edit their own profile. HR/Admin can access all.

---

### GET /api/candidates
**Request**
```
GET http://localhost:8000/api/candidates
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1234567890",
    "position": "Software Engineer",
    "ai_score": 85,
    "experience": "5 years",
    "skills": ["React", "TypeScript", "Node.js"],
    "education": [
      {
        "degree": "BS Computer Science",
        "school": "MIT",
        "year": 2020
      }
    ],
    "certifications": ["AWS Certified Developer"],
    "status": "Applied",
    "avatar": "https://example.com/alice.jpg",
    "applied_date": "2026-08-01",
    "match_reasons": ["Strong technical background", "Relevant experience"],
    "created_at": "2026-08-01T10:00:00",
    "updated_at": "2026-08-01T10:00:00"
  }
]
```

**RBAC Notes:**
- **HR/Admin:** Returns all candidates
- **Candidate:** Returns only their own record

---

### POST /api/candidates
**Request**
```
POST http://localhost:8000/api/candidates
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "+1234567890",
  "position": "Software Engineer",
  "ai_score": 85,
  "experience": "5 years",
  "skills": ["React", "TypeScript", "Node.js"],
  "education": [
    {
      "degree": "BS Computer Science",
      "school": "MIT",
      "year": 2020
    }
  ],
  "certifications": ["AWS Certified Developer"],
  "status": "Applied",
  "avatar": "https://example.com/alice.jpg",
  "applied_date": "2026-08-01",
  "match_reasons": ["Strong technical background"]
}
```

**Valid Status Values:** `Applied`, `Screened`, `Interview`, `Offer`, `Hired`, `Approved`, `Rejected`

**Response (201):** Full `CandidateOut` object with `id`, `created_at`, `updated_at`

**Errors:**
- `403` — Non-HR user trying to create for another email
- `422` — Invalid status value

---

### GET /api/candidates/{candidate_id}
**Request**
```
GET http://localhost:8000/api/candidates/{candidate_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Single `CandidateOut` object

**Errors:**
- `404` — Candidate not found
- `403` — Access denied (not owner, not HR)

---

### PUT /api/candidates/{candidate_id}
**Request**
```
PUT http://localhost:8000/api/candidates/{candidate_id}
Content-Type: application/json
Authorization: Bearer <token>

Body (all fields optional):
{
  "name": "Alice Johnson Updated",
  "email": "alice.new@example.com",
  "phone": "+1234567891",
  "position": "Senior Software Engineer",
  "ai_score": 90,
  "experience": "6 years",
  "skills": ["React", "TypeScript", "Node.js", "Python"],
  "education": [],
  "certifications": ["AWS Certified Developer", "GCP Professional"],
  "avatar": "https://example.com/alice-new.jpg",
  "match_reasons": ["Updated match reason"]
}
```

**Response (200):** Updated `CandidateOut` object

**Errors:**
- `404` — Candidate not found
- `403` — Access denied

---

### PATCH /api/candidates/{candidate_id}/status
**Request**
```
PATCH http://localhost:8000/api/candidates/{candidate_id}/status
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "status": "Interview"
}
```

**Valid Status Values:**
| Status | Description |
|--------|-------------|
| `Applied` | Initial application received |
| `Screened` | Resume screened by HR |
| `Interview` | Scheduled for interview |
| `Offer` | Job offer extended |
| `Hired` | Candidate accepted offer |
| `Approved` | Final approval complete |
| `Rejected` | Application rejected |

**Response (200):** Updated `CandidateOut` object

**Errors:**
- `403` — Non-HR user
- `404` — Candidate not found
- `422` — Invalid status value

---

### DELETE /api/candidates/{candidate_id}
**Request**
```
DELETE http://localhost:8000/api/candidates/{candidate_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response:** `204 No Content`

**Errors:**
- `403` — Non-HR user
- `404` — Candidate not found

---

## 📄 Resume Parsing

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/api/resumes/parse` | ❌ | Parse uploaded resume |

> **Supported Formats:** PDF, DOCX, DOC, JSON · **Max File Size:** 10 MB · **AI Engine:** Groq (Llama 3.3 70B)

---

### POST /api/resumes/parse
**Request**
```
POST http://localhost:8000/api/resumes/parse
Content-Type: multipart/form-data

Body (form-data):
file = <resume.pdf>
```

**Response (200):**
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "+1234567890",
  "location": "New York, NY",
  "summary": "Experienced software engineer with 5+ years...",
  "experience": [
    {
      "company": "Tech Corp",
      "role": "Senior Developer",
      "duration": "2022 - Present",
      "description": "Led development of..."
    }
  ],
  "education": [
    {
      "degree": "BS Computer Science",
      "school": "MIT",
      "year": "2020"
    }
  ],
  "skills": ["React", "TypeScript", "Node.js", "Python"],
  "certifications": ["AWS Certified Developer"],
  "languages": ["English", "Spanish"]
}
```

**Errors:**
- `400` — No filename / Empty file
- `413` — File too large (>10 MB)
- `422` — Unsupported file type / Parse error
- `500` — Internal parsing failure

---

## 📅 Interviews

| Method | Endpoint | Auth Required | Role Required | Description |
|--------|----------|---------------|---------------|-------------|
| `GET` | `/api/interviews` | ✅ | Any | List interviews |
| `POST` | `/api/interviews` | ✅ | HR/Admin | Create interview |
| `GET` | `/api/interviews/{id}` | ✅ | Any* | Get interview details |
| `DELETE` | `/api/interviews/{id}` | ✅ | HR/Admin | Cancel interview |

> \* Candidates can only view their own interviews.

---

### GET /api/interviews
**Request**
```
GET http://localhost:8000/api/interviews
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "candidate_name": "Alice Johnson",
    "candidate_email": "alice@example.com",
    "position": "Software Engineer",
    "date": "2026-08-15",
    "time": "10:00 AM",
    "duration": "60 minutes",
    "type": "Technical",
    "interviewer": "John Smith",
    "meeting_link": "https://meet.google.com/abc-defg-hij",
    "avatar": "https://example.com/alice.jpg",
    "created_at": "2026-08-10T09:00:00"
  }
]
```

**RBAC Notes:**
- **HR/Admin:** Returns all interviews (sorted by date ascending)
- **Candidate:** Returns only interviews matching their email

---

### POST /api/interviews
**Request**
```
POST http://localhost:8000/api/interviews
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "candidate_name": "Alice Johnson",
  "candidate_email": "alice@example.com",
  "position": "Software Engineer",
  "date": "2026-08-15",
  "time": "10:00 AM",
  "duration": "60 minutes",
  "type": "Technical",
  "interviewer": "John Smith",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "avatar": "https://example.com/alice.jpg"
}
```

**Response (201):** Full `InterviewOut` object with `id`, `created_at`

**Errors:**
- `403` — Non-HR user

---

### GET /api/interviews/{interview_id}
**Request**
```
GET http://localhost:8000/api/interviews/{interview_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Single `InterviewOut` object

**Errors:**
- `404` — Interview not found
- `403` — Access denied (not candidate, not HR)

---

### DELETE /api/interviews/{interview_id}
**Request**
```
DELETE http://localhost:8000/api/interviews/{interview_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response:** `204 No Content`

**Errors:**
- `403` — Non-HR user
- `404` — Interview not found

---

## 🔔 Notifications

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/api/notifications` | ✅ | List user's notifications |
| `POST` | `/api/notifications` | ✅ | Create notification |
| `PATCH` | `/api/notifications/{id}/read` | ✅ | Mark notification as read/unread |

---

### GET /api/notifications
**Request**
```
GET http://localhost:8000/api/notifications
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Returns notifications for the logged-in user only, ordered by creation date descending.

```json
[
  {
    "id": 1,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Interview Scheduled",
    "message": "Your technical interview has been scheduled for August 15th at 10:00 AM.",
    "type": "info",
    "is_read": false,
    "created_at": "2026-08-10T09:00:00"
  }
]
```

**Notification Types:** `info`, `success`, `warning`, `error`

---

### POST /api/notifications
**Request**
```
POST http://localhost:8000/api/notifications
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Interview Reminder",
  "message": "You have an interview tomorrow at 10:00 AM.",
  "type": "warning"
}
```

**Response (201):** Full `NotificationOut` object with `id`, `is_read: false`, `created_at`

---

### PATCH /api/notifications/{notification_id}/read
**Request**
```
PATCH http://localhost:8000/api/notifications/{notification_id}/read
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "is_read": true
}
```

**Response (200):** Updated `NotificationOut` object

**Errors:**
- `404` — Notification not found
- `403` — Not owner of notification

---

## 📁 Projects

| Method | Endpoint | Auth Required | Role/Permission Required | Description |
|--------|----------|---------------|--------------------------|-------------|
| `POST` | `/api/v1/projects` | ✅ | Admin + `create_project` | Create a new project |
| `GET` | `/api/v1/projects` | ✅ | Any | List all projects |
| `GET` | `/api/v1/projects/{project_id}` | ✅ | Any | Get project details |
| `POST` | `/api/v1/projects/{project_id}/teams` | ✅ | Admin + `create_project` | Assign a team to a project |
| `GET` | `/api/v1/projects/{project_id}/teams` | ✅ | Any | List teams assigned to a project |

---

### POST /api/v1/projects
**Request**
```
POST http://localhost:8000/api/v1/projects
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "project_name": "FazeSoft EMS",
  "project_code": "FZ-001",
  "description": "Enterprise Management System",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31"
}
```

**Response (201):**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "project_name": "FazeSoft EMS",
  "project_code": "FZ-001",
  "description": "Enterprise Management System",
  "status": "In Progress",
  "manager_id": "a9f0d7b2-1ca1-4fc2-8057-a9464afed2c2",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31",
  "created_at": "2026-08-10T09:00:00",
  "updated_at": "2026-08-10T09:00:00"
}
```

**Errors:**
- `403` — Missing `create_project` permission
- `409` — Project code already exists

---

### GET /api/v1/projects
**Request**
```
GET http://localhost:8000/api/v1/projects
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Lightweight list of projects ordered by newest first.

```json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440010",
    "project_name": "FazeSoft EMS",
    "project_code": "FZ-001",
    "status": "In Progress",
    "start_date": "2026-08-01"
  }
]
```

---

### GET /api/v1/projects/{project_id}
**Request**
```
GET http://localhost:8000/api/v1/projects/{project_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Full `ProjectOut` object (same shape as create response)

**Errors:**
- `404` — Project not found

---

### POST /api/v1/projects/{project_id}/teams
**Request**
```
POST http://localhost:8000/api/v1/projects/{project_id}/teams
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "team_id": "550e8400-e29b-41d4-a716-446655440020"
}
```

**Response (201):**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440010",
  "team_id": "550e8400-e29b-41d4-a716-446655440020",
  "assigned_at": "2026-08-10T10:00:00"
}
```

**Errors:**
- `400` — Team already assigned to this project
- `403` — Missing `create_project` permission
- `404` — Project or team not found

---

### GET /api/v1/projects/{project_id}/teams
**Request**
```
GET http://localhost:8000/api/v1/projects/{project_id}/teams
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** List of `TeamWithMembersOut` objects assigned to the project.

```json
[
  {
    "team_id": "550e8400-e29b-41d4-a716-446655440020",
    "team_name": "Frontend Squad",
    "description": "Frontend development team",
    "created_at": "2026-08-10T09:30:00",
    "updated_at": "2026-08-10T09:30:00",
    "members": [
      {
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "role": "front_end",
        "joined_at": "2026-08-10T09:30:00"
      }
    ]
  }
]
```

**Errors:**
- `404` — Project not found

---

## 👥 Teams

| Method | Endpoint | Auth Required | Role/Permission Required | Description |
|--------|----------|---------------|--------------------------|-------------|
| `POST` | `/api/v1/teams` | ✅ | Admin + `create_team` | Create a team with members |
| `GET` | `/api/v1/teams` | ✅ | Any | List all teams |
| `GET` | `/api/v1/teams/{team_id}` | ✅ | Any | Get team details with members |

> **Team Member Roles:** `front_end`, `back_end`

---

### POST /api/v1/teams
**Request**
```
POST http://localhost:8000/api/v1/teams
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "team_name": "Frontend Squad",
  "description": "Frontend development team",
  "members": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "front_end"
    },
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "back_end"
    }
  ]
}
```

**Response (201):**
```json
{
  "team_id": "550e8400-e29b-41d4-a716-446655440020",
  "team_name": "Frontend Squad",
  "description": "Frontend development team",
  "created_at": "2026-08-10T09:30:00",
  "updated_at": "2026-08-10T09:30:00",
  "members": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "front_end",
      "joined_at": "2026-08-10T09:30:00"
    },
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "back_end",
      "joined_at": "2026-08-10T09:30:00"
    }
  ]
}
```

**Errors:**
- `403` — Missing `create_team` permission

---

### GET /api/v1/teams
**Request**
```
GET http://localhost:8000/api/v1/teams
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** List of `TeamWithMembersOut` objects ordered by newest first.

```json
[
  {
    "team_id": "550e8400-e29b-41d4-a716-446655440020",
    "team_name": "Frontend Squad",
    "description": "Frontend development team",
    "created_at": "2026-08-10T09:30:00",
    "updated_at": "2026-08-10T09:30:00",
    "members": [
      {
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "role": "front_end",
        "joined_at": "2026-08-10T09:30:00"
      }
    ]
  }
]
```

---

### GET /api/v1/teams/{team_id}
**Request**
```
GET http://localhost:8000/api/v1/teams/{team_id}
Content-Type: application/json
Authorization: Bearer <token>
```

**Response (200):** Single `TeamWithMembersOut` object

**Errors:**
- `404` — Team not found

---

## 🔑 Authentication Header

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## 📊 Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all endpoints |
| `hr` | Full access to candidates, interviews, notifications |
| `employee` | Can view/edit own profile, view own interviews |

---

## 📋 Status Pipeline (Candidates)

```
Applied → Screened → Interview → Offer → Hired → Approved
                                         ↘ Rejected
```

---

## ⚠️ Common Error Responses

```json
{
  "detail": "Error message describing the problem"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad Request — Invalid input |
| `401` | Unauthorized — Invalid or missing token |
| `403` | Forbidden — Insufficient permissions |
| `404` | Not Found — Resource doesn't exist |
| `409` | Conflict — Resource already exists |
| `413` | Payload Too Large — File exceeds 10 MB |
| `422` | Unprocessable Entity — Validation error |
| `500` | Internal Server Error — Unexpected failure |