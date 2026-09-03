# 📬 FazeSoft-EMS Backend — Postman API Testing Guide

Complete collection of every API with JSON request bodies, example responses, and Postman setup steps.

> **Base URLs**
> - Local: `http://localhost:8000`
> - Production: `https://faze-soft-ems-backend.vercel.app`
>
> All routes are available under **`/api/v1`** and backward-compatible **`/api`** (e.g. `/api/v1/auth/login` = `/api/auth/login`).
> Interactive docs: `http://localhost:8000/docs`

---

## 🔧 Postman Setup

### 1. Environment Variables
Create an environment in Postman (gear icon → Environments → Add) with:

| Variable | Initial Value | Example |
|----------|---------------|---------|
| `base_url` | `http://localhost:8000` | |
| `token` | *(leave empty)* | |

### 2. Authorization
For every **protected** endpoint, set:
- **Type:** `Bearer Token`
- **Token:** `{{token}}`

1. Call `POST {{base_url}}/api/v1/auth/login` first.
2. Copy `access_token` from the response into the `token` variable.
3. Optionally add a **Test** script on the login request to auto-set it:

```js
const json = pm.response.json();
pm.environment.set("token", json.access_token);
```

---

## 🏠 Health Check

### 1. GET `{{base_url}}/api/v1/`
**Auth:** ❌ None

**Response 200:**
```json
{
  "status": "ok",
  "message": "HireMate API is running 🚀"
}
```

### 2. GET `{{base_url}}/api/v1/health`
**Auth:** ❌ None

**Response 200:**
```json
{
  "status": "healthy"
}
```

---

## 🔐 Authentication

### 3. POST `{{base_url}}/api/v1/auth/signup`
**Auth:** ❌ None

**Body (raw JSON):**
```json
{
  "email": "john@example.com",
  "password": "securepass123",
  "full_name": "John Doe"
}
```

**Response 201:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "candidate",
    "phone": null,
    "location": null,
    "job_title": null,
    "bio": null,
    "avatar": null,
    "is_active": true,
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

**Error 409 (duplicate email):**
```json
{
  "detail": "An account with this email already exists."
}
```

### 4. POST `{{base_url}}/api/v1/auth/login`
**Auth:** ❌ None

**Body (raw JSON):**
```json
{
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response 200:** *(same shape as signup — Token with user object)*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "candidate",
    "phone": null,
    "location": null,
    "job_title": null,
    "bio": null,
    "avatar": null,
    "is_active": true,
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

**Error 401 (bad credentials):**
```json
{
  "detail": "Incorrect email or password."
}
```

### 5. POST `{{base_url}}/api/v1/auth/create-employee`
**Auth:** ❌ None *(note: does not enforce admin — see your RBAC requirements)*

**Body (raw JSON):**
```json
{
  "email": "hradmin@example.com",
  "password": "securepass123",
  "full_name": "HR Admin",
  "job_title": "HR Manager"
}
```

**Response 201 (UserOut):**
```json
{
  "id": "6a9b2c3d-1e4f-5a6b-7c8d-9e0f1a2b3c4d",
  "email": "hradmin@example.com",
  "full_name": "HR Admin",
  "role": "employee",
  "phone": null,
  "location": null,
  "job_title": "HR Manager",
  "bio": null,
  "avatar": null,
  "is_active": true,
  "created_at": "2026-08-13T10:05:00Z"
}
```

### 6. GET `{{base_url}}/api/v1/auth/me`
**Auth:** ✅ Bearer `{{token}}`

**Response 200 (UserOut):**
```json
{
  "id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "phone": null,
  "location": null,
  "job_title": null,
  "bio": null,
  "avatar": null,
  "is_active": true,
  "created_at": "2026-08-13T10:00:00Z"
}
```

---

## 🧑💼 Candidates

### 7. GET `{{base_url}}/api/v1/candidates`
**Auth:** ✅ Bearer

**Response 200 (array of CandidateOut):**
```json
[
  {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "+1 555 0100",
    "position": "Backend Engineer",
    "ai_score": 87,
    "experience": "4 years",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "education": [{ "degree": "BSc Computer Science", "institution": "MIT" }],
    "certifications": ["AWS Certified"],
    "status": "Applied",
    "avatar": null,
    "applied_date": "2026-08-01",
    "match_reasons": ["Strong Python background", "API experience"],
    "created_at": "2026-08-01T09:00:00Z",
    "updated_at": "2026-08-01T09:00:00Z"
  }
]
```

### 8. POST `{{base_url}}/api/v1/candidates`
**Auth:** ✅ Bearer *(HR/admin see all; candidates may create only their own record)*

**Body (raw JSON):**
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+1 555 0100",
  "position": "Backend Engineer",
  "ai_score": 87,
  "experience": "4 years",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "education": [{ "degree": "BSc Computer Science", "institution": "MIT" }],
  "certifications": ["AWS Certified"],
  "status": "Applied",
  "avatar": null,
  "applied_date": "2026-08-01",
  "match_reasons": ["Strong Python background", "API experience"]
}
```

**Response 201:** *(same as one element of the list above, with `id`, `created_at`, `updated_at` populated)*

### 9. GET `{{base_url}}/api/v1/candidates/{candidate_id}`
**Auth:** ✅ Bearer — e.g. `/api/v1/candidates/1`

**Response 200 (CandidateOut):**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+1 555 0100",
  "position": "Backend Engineer",
  "ai_score": 87,
  "experience": "4 years",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "education": [{ "degree": "BSc Computer Science", "institution": "MIT" }],
  "certifications": ["AWS Certified"],
  "status": "Applied",
  "avatar": null,
  "applied_date": "2026-08-01",
  "match_reasons": ["Strong Python background"],
  "created_at": "2026-08-01T09:00:00Z",
  "updated_at": "2026-08-01T09:00:00Z"
}
```

**Error 404:**
```json
{
  "detail": "Candidate with id=99 not found."
}
```

### 10. PUT `{{base_url}}/api/v1/candidates/{candidate_id}`
**Auth:** ✅ Bearer — e.g. `/api/v1/candidates/1`

**Body (raw JSON — all fields optional):**
```json
{
  "status": "Interview",
  "phone": "+1 555 0199",
  "ai_score": 92
}
```

**Response 200 (CandidateOut):**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+1 555 0199",
  "position": "Backend Engineer",
  "ai_score": 92,
  "experience": "4 years",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "education": [{ "degree": "BSc Computer Science", "institution": "MIT" }],
  "certifications": ["AWS Certified"],
  "status": "Interview",
  "avatar": null,
  "applied_date": "2026-08-01",
  "match_reasons": ["Strong Python background"],
  "created_at": "2026-08-01T09:00:00Z",
  "updated_at": "2026-08-13T11:00:00Z"
}
```

### 11. PATCH `{{base_url}}/api/v1/candidates/{candidate_id}/status`
**Auth:** ✅ Bearer *(HR/admin only)* — e.g. `/api/v1/candidates/1/status`

**Body (raw JSON):**
```json
{
  "status": "Hired"
}
```

**Valid statuses:** `Applied`, `Screened`, `Interview`, `Offer`, `Hired`, `Approved`, `Rejected`

**Response 200 (CandidateOut):** *(status updated to `"Hired"`)*

**Error 422 (invalid status):**
```json
{
  "detail": "Invalid status 'Random'. Must be one of: ['Applied', 'Screened', 'Interview', 'Offer', 'Hired', 'Approved', 'Rejected']"
}
```

### 12. DELETE `{{base_url}}/api/v1/candidates/{candidate_id}`
**Auth:** ✅ Bearer *(HR/admin only)* — e.g. `/api/v1/candidates/1`

**Response 204:** No Content

---

## 📅 Interviews

### 13. GET `{{base_url}}/api/v1/interviews`
**Auth:** ✅ Bearer *(HR/admin see all; candidates see their own by email)*

**Response 200 (array of InterviewOut):**
```json
[
  {
    "id": 1,
    "candidate_name": "Alice Smith",
    "candidate_email": "alice@example.com",
    "position": "Backend Engineer",
    "date": "2026-08-20",
    "time": "10:00",
    "duration": "45 min",
    "type": "Technical",
    "interviewer": "Bob Jones",
    "meeting_link": "https://meet.google.com/abc-defg-hij",
    "avatar": null,
    "created_at": "2026-08-10T14:00:00Z"
  }
]
```

### 14. POST `{{base_url}}/api/v1/interviews`
**Auth:** ✅ Bearer *(HR/admin only)*

**Body (raw JSON):**
```json
{
  "candidate_name": "Alice Smith",
  "candidate_email": "alice@example.com",
  "position": "Backend Engineer",
  "date": "2026-08-20",
  "time": "10:00",
  "duration": "45 min",
  "type": "Technical",
  "interviewer": "Bob Jones",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "avatar": null
}
```

**Response 201 (InterviewOut):**
```json
{
  "id": 1,
  "candidate_name": "Alice Smith",
  "candidate_email": "alice@example.com",
  "position": "Backend Engineer",
  "date": "2026-08-20",
  "time": "10:00",
  "duration": "45 min",
  "type": "Technical",
  "interviewer": "Bob Jones",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "avatar": null,
  "created_at": "2026-08-13T11:30:00Z"
}
```

### 15. GET `{{base_url}}/api/v1/interviews/{interview_id}`
**Auth:** ✅ Bearer — e.g. `/api/v1/interviews/1`

**Response 200 (InterviewOut):**
```json
{
  "id": 1,
  "candidate_name": "Alice Smith",
  "candidate_email": "alice@example.com",
  "position": "Backend Engineer",
  "date": "2026-08-20",
  "time": "10:00",
  "duration": "45 min",
  "type": "Technical",
  "interviewer": "Bob Jones",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "avatar": null,
  "created_at": "2026-08-13T11:30:00Z"
}
```

**Error 404:**
```json
{
  "detail": "Interview with id=99 not found."
}
```

### 16. DELETE `{{base_url}}/api/v1/interviews/{interview_id}`
**Auth:** ✅ Bearer *(HR/admin only)* — e.g. `/api/v1/interviews/1`

**Response 204:** No Content

---

## 🔔 Notifications

### 17. GET `{{base_url}}/api/v1/notifications`
**Auth:** ✅ Bearer *(returns only the logged-in user's notifications)*

**Response 200 (array of NotificationOut):**
```json
[
  {
    "id": 5,
    "user_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
    "title": "Interview Scheduled",
    "message": "You have an interview on 2026-08-20 at 10:00.",
    "type": "info",
    "is_read": false,
    "created_at": "2026-08-13T11:30:00Z"
  }
]
```

### 18. POST `{{base_url}}/api/v1/notifications`
**Auth:** ✅ Bearer

**Body (raw JSON):**
```json
{
  "user_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "title": "Interview Scheduled",
  "message": "You have an interview on 2026-08-20 at 10:00.",
  "type": "info"
}
```

**Response 201 (NotificationOut):**
```json
{
  "id": 5,
  "user_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "title": "Interview Scheduled",
  "message": "You have an interview on 2026-08-20 at 10:00.",
  "type": "info",
  "is_read": false,
  "created_at": "2026-08-13T11:30:00Z"
}
```

### 19. PATCH `{{base_url}}/api/v1/notifications/{notification_id}/read`
**Auth:** ✅ Bearer — e.g. `/api/v1/notifications/5/read`

**Body (raw JSON):**
```json
{
  "is_read": true
}
```

**Response 200 (NotificationOut):**
```json
{
  "id": 5,
  "user_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "title": "Interview Scheduled",
  "message": "You have an interview on 2026-08-20 at 10:00.",
  "type": "info",
  "is_read": true,
  "created_at": "2026-08-13T11:30:00Z"
}
```

---

## 📄 Resume Parsing

### 20. POST `{{base_url}}/api/v1/resumes/parse`
**Auth:** ❌ None
**Body:** `form-data` (multipart) — key `file`, type *File*
- Accepts: `.pdf`, `.docx`, `.doc`, `.json` | Max 10 MB

**Response 200 (structured data):**
```json
{
  "personalDetails": {
    "fullName": "Alice Smith",
    "email": "alice@example.com",
    "phone": "+1 555 0100",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/alice",
    "portfolio": null
  },
  "summary": "Backend engineer with 4 years of experience building APIs.",
  "education": [
    {
      "degree": "BSc Computer Science",
      "institution": "MIT",
      "year": "2015-2019",
      "gpa": "3.8"
    }
  ],
  "experience": [
    {
      "position": "Backend Engineer",
      "company": "TechCorp",
      "duration": "2021 - Present",
      "description": ["Built REST APIs with FastAPI", "Optimized PostgreSQL queries"]
    }
  ],
  "skills": {
    "technical": ["Python", "FastAPI", "PostgreSQL"],
    "soft": ["Communication", "Problem Solving"],
    "languages": ["English (Native)"]
  },
  "certifications": ["AWS Certified Developer"]
}
```

**Error 413 (file too large):**
```json
{
  "detail": "File too large (15.0 MB). Maximum: 10 MB."
}
```

---

## 📦 Projects

> **Roles:** Create requires role **`Admin`** AND permission **`create_project`** (via `user_role` + `role_permission` junction tables). List/Get require any authenticated user.

### 21. GET `{{base_url}}/api/v1/projects`
**Auth:** ✅ Bearer

**Response 200 (array of ProjectListOut):**
```json
[
  {
    "project_id": "a1b2c3d4-1111-4f6a-b7c8-d9e0f1a2b3c4",
    "project_name": "HireMate Mobile App",
    "project_code": "PRJ-001",
    "status": "In Progress",
    "start_date": "2026-08-01"
  }
]
```

### 22. POST `{{base_url}}/api/v1/projects`
**Auth:** ✅ Bearer *(Admin + `create_project` permission)*

**Body (raw JSON):**
```json
{
  "project_name": "HireMate Mobile App",
  "project_code": "PRJ-001",
  "description": "Build the mobile companion app for HireMate.",
  "client_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31"
}
```

**Response 201 (ProjectOut):**
```json
{
  "project_id": "a1b2c3d4-1111-4f6a-b7c8-d9e0f1a2b3c4",
  "project_name": "HireMate Mobile App",
  "project_code": "PRJ-001",
  "description": "Build the mobile companion app for HireMate.",
  "status": "In Progress",
  "manager_id": "6a9b2c3d-1e4f-5a6b-7c8d-9e0f1a2b3c4d",
  "client_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31",
  "created_at": "2026-08-13T12:00:00Z",
  "updated_at": "2026-08-13T12:00:00Z"
}
```

**Error 403 (missing role/permission):**
```json
{
  "detail": "Access denied. Requires role: Admin."
}
```
```json
{
  "detail": "Access denied. Requires permission: create_project."
}
```

**Error 409 (duplicate project_code):**
```json
{
  "detail": "Project with code 'PRJ-001' already exists."
}
```

### 23. GET `{{base_url}}/api/v1/projects/{project_id}`
**Auth:** ✅ Bearer — e.g. `/api/v1/projects/a1b2c3d4-1111-4f6a-b7c8-d9e0f1a2b3c4`

**Response 200 (ProjectOut):**
```json
{
  "project_id": "a1b2c3d4-1111-4f6a-b7c8-d9e0f1a2b3c4",
  "project_name": "HireMate Mobile App",
  "project_code": "PRJ-001",
  "description": "Build the mobile companion app for HireMate.",
  "status": "In Progress",
  "manager_id": "6a9b2c3d-1e4f-5a6b-7c8d-9e0f1a2b3c4d",
  "client_id": "5f8a1b2c-9d4e-4f6a-b7c8-d9e0f1a2b3c4",
  "start_date": "2026-08-01",
  "end_date": "2026-12-31",
  "created_at": "2026-08-13T12:00:00Z",
  "updated_at": "2026-08-13T12:00:00Z"
}
```

**Error 404:**
```json
{
  "detail": "Project with id=a1b2c3d4-9999-4f6a-b7c8-d9e0f1a2b3c4 not found."
}
```

---

## ⚠️ Common Error Responses

| Status | Meaning | Example Body |
|--------|---------|--------------|
| `401` | Missing/invalid token | `{ "detail": "Not authenticated" }` |
| `403` | Insufficient permissions | `{ "detail": "Access denied..." }` |
| `404` | Resource not found | `{ "detail": "X with id=... not found." }` |
| `409` | Duplicate/conflict | `{ "detail": "An account with this email already exists." }` |
| `422` | Validation error | `{ "detail": [{ "loc": ["body","email"], "msg": "value is not a valid email address", "type": "value_error" }] }` |

---

## 🧪 Suggested Postman Test Order

1. `GET /api/v1/health`
2. `POST /api/v1/auth/signup` → `POST /api/v1/auth/login` (auto-saves token)
3. `GET /api/v1/auth/me`
4. Candidates: `POST` → `GET /` → `GET /{id}` → `PUT /{id}` → `PATCH /{id}/status` → `DELETE /{id}`
5. Interviews: `POST` → `GET /` → `GET /{id}` → `DELETE /{id}`
6. Notifications: `POST` → `GET /` → `PATCH /{id}/read`
7. Resumes: `POST /parse` (upload a PDF)
8. Projects: `POST /` → `GET /` → `GET /{id}`
