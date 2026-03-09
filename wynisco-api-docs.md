# Wynisco API Documentation

> Reverse-engineered from HAR capture of `app.wynisco.com` (Feb 25, 2026).
> **Confirmed** endpoints were directly observed in the HAR. **Inferred** endpoints are educated guesses based on data models and REST conventions.

---

## Table of Contents

1. [Base URL & Authentication](#base-url--authentication)
2. [Data Models](#data-models)
3. [Confirmed Endpoints](#confirmed-endpoints)
4. [Inferred Endpoints](#inferred-endpoints)
5. [Enums & Known Values](#enums--known-values)
6. [Pagination](#pagination)
7. [Quirks & Notes](#quirks--notes)

---

## Base URL & Authentication

### Base URL

```
https://backend-dot-student-marketing-operations.el.r.appspot.com/api/v1/
```

- **Hosting:** Google App Engine (`student-marketing-operations` project)
- **Frontend:** `https://app.wynisco.com`
- **API version prefix:** `/api/v1/`

### CORS Configuration

| Header | Value |
|--------|-------|
| `access-control-allow-credentials` | `true` |
| `access-control-allow-origin` | `https://app.wynisco.com` |

### Authentication

The auth mechanism is **cookie-based** (httpOnly cookies not exported in the HAR):

- No `Authorization` header on any request
- No `cookie` header visible in the HAR export
- `access-control-allow-credentials: true` confirms the server expects credentials (cookies) to be sent cross-origin
- `GET /api/v1/auth/me` returns a specific user profile, confirming authentication is active

### Common Request Headers

| Header | Value |
|--------|-------|
| `accept` | `*/*` |
| `content-type` | `application/json` |
| `origin` | `https://app.wynisco.com` |
| `referer` | `https://app.wynisco.com/` |

### Common Response Headers

| Header | Value |
|--------|-------|
| `content-type` | `application/json` |
| `server` | `Google Frontend` |
| `vary` | `Accept-Encoding`, `Origin` |

---

## Data Models

### User

Returned by `GET /api/v1/auth/me`. The profile sub-objects are populated based on the user's `role`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `string (UUID)` | Primary key | `"0341f5a2-ded5-4d91-ac9e-1ed62bc2cf5a"` |
| `email` | `string` | Primary email | `"ramsankarharikrishnan@gmail.com"` |
| `first_name` | `string` | | `"Ram"` |
| `last_name` | `string` | | `"Harikrishnan"` |
| `mobile` | `string` | | `"9567838977"` |
| `photo` | `string` | URL or empty string | `""` |
| `role` | `string` | User role enum | `"candidate"` |
| `privilege` | `string` | Permission level | `"user"` |
| `pod_id` | `string (UUID)` | FK to Pod | `"07835570-ebaa-4388-a087-cbe8dc1e4aa3"` |
| `marketing_candidate_email` | `string` | | `"ramsankarharikrishnan@gmail.com"` |
| `created_at` | `string (ISO 8601)` | With timezone | `"2026-01-08T06:34:52.903082Z"` |
| `updated_at` | `string (ISO 8601)` | With timezone | `"2026-01-08T16:51:37.838985Z"` |
| `candidate_profile` | `CandidateProfile \| null` | Populated when `role=candidate` | See below |
| `consultant_profile` | `object \| null` | Populated when `role=consultant` | `null` (schema unknown) |
| `alumni_profile` | `object \| null` | Populated when `role=alumni` | `null` (schema unknown) |
| `instructor_profile` | `object \| null` | Populated when `role=instructor` | `null` (schema unknown) |
| `pod` | `Pod` | Embedded Pod object | See Pod model |

### CandidateProfile

Nested under `User.candidate_profile`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | `string (UUID)` | Back-reference to User.id | `"0341f5a2-ded5-4d91-ac9e-1ed62bc2cf5a"` |
| `visa_status` | `string \| null` | Immigration status | `"F1 OPT"` |
| `resume_url` | `string \| null` | Google Docs URL | `"https://docs.google.com/document/d/..."` |
| `resume_plain_text` | `string \| null` | Full resume text | (long multi-line string) |
| `secondary_email` | `string \| null` | | `null` |
| `whatsapp_group_link` | `string \| null` | | `null` |
| `dob` | `string \| null` | Date of birth | `null` |
| `sponsorship_required` | `boolean \| null` | | `null` |
| `open_to_relocate` | `boolean \| null` | | `null` |
| `graduation_date` | `string \| null` | | `null` |
| `university_id` | `int` | FK to University | `160` |
| `job_titles` | `string[]` | Target job titles | `["Software Developer", "Software Engineer"]` |
| `skills` | `string[]` | Technical skills | `["Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "Bash/Shell"]` |
| `years_of_experience` | `int` | | `4` |
| `linkedin_url` | `string \| null` | | `"http://linkedin.com/in/ram-harikrishnan/"` |
| `location` | `string` | Can be empty string | `""` |
| `expected_salary_min` | `int \| null` | | `90000` |
| `expected_salary_max` | `int \| null` | | `110000` |
| `offer_stage` | `string \| null` | | `null` |
| `parents_number` | `string \| null` | | `null` |
| `university` | `University` | Embedded University | See University model |
| `instructors` | `Instructor[]` | Assigned instructors | See Instructor model |

### University

Nested under `CandidateProfile.university`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `int` | Primary key | `160` |
| `school_name` | `string` | | `"Arizona State University"` |
| `website` | `string` | | `"http://asu.edu"` |
| `city` | `string` | | `"Tempe"` |
| `state` | `string` | | `"AZ"` |

### Instructor

Nested under `CandidateProfile.instructors[]`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user_id` | `string (UUID)` | | `"1a1d8106-4cf8-4fa0-8364-f800f31ba111"` |
| `first_name` | `string` | | `"Prem"` |
| `last_name` | `string` | | `"Upadhyay"` |

### Pod

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | `string (UUID)` | No | Primary key | `"07835570-ebaa-4388-a087-cbe8dc1e4aa3"` |
| `pod_name` | `string` | No | Cohort name | `"Dev_0010"`, `"Data_0033"`, `"PM/BA_001"` |
| `candidate_onboarded_date` | `string (ISO 8601)` | Yes | No timezone | `"2026-01-15T00:00:00"` |
| `candidate_end_date` | `string (ISO 8601)` | Yes | No timezone | `"2026-03-15T00:00:00"` |
| `meeting_url` | `string` | Yes | Google Meet URL | `"https://meet.google.com/axp-vhtv-qck?authuser=0"` |
| `resume_format` | `string` | Yes | Always null in data | `null` |
| `current_audit_cycle_id` | `string (UUID)` | Yes | | `"d5252f24-ad98-4829-b399-1f02249298ba"` |
| `audited_at` | `string (ISO 8601)` | Yes | With timezone (`Z`) | `"2026-02-25T08:26:03.861715Z"` |

### Job

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | `int` | No | Primary key | `1169980` |
| `source` | `string` | No | Job source enum | `"LinkedinExtension"` |
| `scraped_by` | `string` | No | Email or `"NA"` | `"poojac.wynisco@gmail.com"`, `"NA"` |
| `job_url` | `string` | No | Original listing URL | `"https://www.linkedin.com/jobs/view/4376745304"` |
| `job_title` | `string` | No | | `"Business Intelligence Specialist"` |
| `state` | `string` | No | Can be empty | `"New York, NY"`, `"Remote"`, `""` |
| `city` | `string` | No | Can be empty | `"New York, NY"`, `""` |
| `location` | `string` | Yes | Always null in observed data | `null` |
| `job_description` | `string` | No | Full HTML/text, can be empty | (long text) |
| `recruiter_info_avaiable` | `boolean` | No | **Typo in API** (missing 'l') | `false` |
| `notes` | `string` | No | Can be empty | `""` |
| `salary` | `string` | Yes | | `null` |
| `experience` | `int` | Yes | Years of experience | `null`, `5`, `3` |
| `contact_id` | `int` | Yes | FK to Contact | `null` |
| `employer` | `Employer` | No | Embedded Employer | See Employer model |
| `contact` | `Contact` | Yes | Always null in observed data | `null` |
| `tags` | `Tag[]` | No | Always empty in observed data | `[]` |
| `created_at` | `string (ISO 8601)` | No | No timezone | `"2026-02-25T20:43:12.014951"` |
| `updated_at` | `string (ISO 8601)` | No | No timezone | `"2026-02-25T20:43:12.014954"` |

### Employer

Nested under `Job.employer`.

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | `int` | No | Primary key | `10478` |
| `name` | `string` | No | Company name | `"Cloudera"` |
| `website` | `string` | Yes | | `"https://cloudera.com"`, `null` |
| `linkedin_url` | `string` | Yes | | `"https://www.linkedin.com/company/cloudera"` |
| `location` | `string` | Yes | | `"Santa Clara, CA"` |
| `do_not_apply` | `boolean` | No | Blacklisted employer | `false` |
| `referrel_available` | `boolean` | No | **Typo in API** (should be "referral") | `false` |
| `likely_defense` | `boolean` | No | Defense contractor flag | `false` |
| `h1b_filed` | `boolean` | No | Has filed H1B | `true` |
| `everified` | `boolean` | No | E-Verify enrolled | `true` |
| `recent_international_hires` | `boolean` | No | | `true` |
| `career_url` | `string` | Yes | Careers page URL | `null` |
| `company_size` | `string` | Yes | | `"1001-5000"` |
| `industry` | `string` | Yes | Comma-separated | `"Sales, Business Development, And Consulting"` |
| `summary` | `string` | Yes | Company/role summary | (long text) |
| `last_modified` | `string (ISO 8601)` | No | No timezone | `"2025-11-20T07:03:28.928032"` |

### MyJob (Application Record)

Returned by `GET /api/v1/myjobs/filter`. Represents a job application made on behalf of a candidate.

| Field | Type | Nullable | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | `int` | No | Primary key | `1958269` |
| `original_job_id` | `int` | No | FK to Job.id | `1168129` |
| `applied_by` | `string` | No | Staff email, can be `""` | `"gauri.m@wynisco.com"` |
| `submitted_for` | `string` | No | Candidate email | `"ramsankarharikrishnan@gmail.com"` |
| `status` | `string` | No | Application status enum | `"Applied"` |
| `applied_at` | `string (ISO 8601)` | Yes | When applied | `"2026-02-25T20:26:14.546158"` |
| `resume_link` | `string` | Yes | Google Docs edit URL | `"https://docs.google.com/document/d/.../edit"` |
| `resume_link_pdf` | `string` | Yes | PDF export URL | `"https://docs.google.com/document/d/.../export?format=pdf"` |
| `scraped_by` | `string` | No | Staff who scraped the job | `"gauri.m@wynisco.com"` |
| `pod_id` | `string (UUID)` | No | FK to Pod | `"07835570-ebaa-4388-a087-cbe8dc1e4aa3"` |
| `myjobsnotes` | `string` | Yes | Notes, can be `""` | `""` |
| `current_interview_status` | `string` | Yes | Always null in observed data | `null` |
| `created_at` | `string (ISO 8601)` | No | | `"2026-02-25T18:11:55.422415"` |
| `updated_at` | `string (ISO 8601)` | No | | `"2026-02-25T20:26:14.547045"` |
| `pod` | `Pod` | No | Embedded Pod object | See Pod model |
| `job` | `Job` | No | Full embedded Job (with employer, contact, tags) | See Job model |

### Contact (Schema Unknown)

Referenced by `Job.contact_id` and `Job.contact`. All observed values are `null`. Structure not captured in the HAR.

### Tag (Schema Unknown)

Referenced by `Job.tags`. All observed values are `[]`. Individual tag object structure not captured in the HAR.

---

## Confirmed Endpoints

### 1. `GET /api/v1/auth/me`

Returns the authenticated user's full profile.

**Request:**
```
GET /api/v1/auth/me
Host: backend-dot-student-marketing-operations.el.r.appspot.com
Content-Type: application/json
```

**Response:** `200 OK` (13,870 bytes, 299ms)

```jsonc
{
  "id": "0341f5a2-ded5-4d91-ac9e-1ed62bc2cf5a",
  "email": "ramsankarharikrishnan@gmail.com",
  "first_name": "Ram",
  "last_name": "Harikrishnan",
  "mobile": "9567838977",
  "photo": "",
  "role": "candidate",
  "privilege": "user",
  "pod_id": "07835570-ebaa-4388-a087-cbe8dc1e4aa3",
  "marketing_candidate_email": "ramsankarharikrishnan@gmail.com",
  "created_at": "2026-01-08T06:34:52.903082Z",
  "updated_at": "2026-01-08T16:51:37.838985Z",
  "candidate_profile": {
    "user_id": "0341f5a2-ded5-4d91-ac9e-1ed62bc2cf5a",
    "visa_status": "F1 OPT",
    "resume_url": "https://docs.google.com/document/d/...",
    "resume_plain_text": "...",
    "secondary_email": null,
    "whatsapp_group_link": null,
    "dob": null,
    "sponsorship_required": null,
    "open_to_relocate": null,
    "graduation_date": null,
    "university_id": 160,
    "job_titles": ["Software Developer", "Software Engineer"],
    "skills": ["Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "Bash/Shell"],
    "years_of_experience": 4,
    "linkedin_url": "http://linkedin.com/in/ram-harikrishnan/",
    "location": "",
    "expected_salary_min": 90000,
    "expected_salary_max": 110000,
    "offer_stage": null,
    "parents_number": null,
    "university": {
      "id": 160,
      "school_name": "Arizona State University",
      "website": "http://asu.edu",
      "city": "Tempe",
      "state": "AZ"
    },
    "instructors": [
      { "user_id": "1a1d8106-4cf8-4fa0-8364-f800f31ba111", "first_name": "Prem", "last_name": "Upadhyay" },
      { "user_id": "9116019c-5c67-4326-aa5f-52113941e526", "first_name": "Vrutik", "last_name": "Adani" }
    ]
  },
  "consultant_profile": null,
  "alumni_profile": null,
  "instructor_profile": null,
  "pod": {
    "id": "07835570-ebaa-4388-a087-cbe8dc1e4aa3",
    "pod_name": "Dev_0010",
    "candidate_onboarded_date": "2026-01-15T00:00:00",
    "candidate_end_date": "2026-03-15T00:00:00",
    "meeting_url": "https://meet.google.com/axp-vhtv-qck?authuser=0",
    "resume_format": null,
    "current_audit_cycle_id": "d5252f24-ad98-4829-b399-1f02249298ba",
    "audited_at": "2026-02-25T08:26:03.861715Z"
  }
}
```

---

### 2. `GET /api/v1/pods/`

List all pods (cohorts). Paginated.

> **Warning:** Requesting `/api/v1/pods` (no trailing slash) returns a `307 Temporary Redirect` to `/api/v1/pods/`. Always include the trailing slash.

**Request:**
```
GET /api/v1/pods/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `size` | int | 100 | Items per page |

**Response:** `200 OK` (18,727 bytes, 274ms)

```jsonc
{
  "pods": [
    {
      "id": "f6cd3c61-3e81-4cb1-93f0-91b9b57bf78c",
      "pod_name": "Data_0033",
      "candidate_onboarded_date": "2026-02-25T00:00:00",
      "candidate_end_date": "2026-04-15T00:00:00",
      "meeting_url": "https://meet.google.com/xfg-upsb-tbg?authuser=0",
      "resume_format": null,
      "current_audit_cycle_id": null,
      "audited_at": null
    },
    {
      "id": "4c799b72-396d-41c0-82ca-fced294b3394",
      "pod_name": "Data_0030",
      "candidate_onboarded_date": "2026-02-24T00:00:00",
      "candidate_end_date": "2026-04-23T00:00:00",
      "meeting_url": "https://meet.google.com/ytj-ohch-vvn",
      "resume_format": null,
      "current_audit_cycle_id": "d5252f24-ad98-4829-b399-1f02249298ba",
      "audited_at": "2026-02-25T08:58:09.871961Z"
    }
    // ... 58 total pods
  ],
  "total": 58,
  "page": 1,
  "size": 100,
  "total_pages": 1
}
```

**Observed pod name patterns:** `Data_NNNN`, `Dev_NNNN`, `DEV_NNN`, `PM/BA_NNN`, `QA_NNN`, `UI/UX_NN`, `FN_NNN`, `SC_NNN`, `Salesforce-NNN`, `CS_NNN`, `DA_NNNN`, `Core_POD`, `training_pod`

---

### 3. `GET /api/v1/jobs/`

List all jobs. Paginated.

**Request:**
```
GET /api/v1/jobs/?page=1&size=100
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `size` | int | 100 | Items per page |

**Response:** `200 OK` (199,536 bytes, 624ms)

```jsonc
{
  "jobs": [
    {
      "id": 1169980,
      "source": "LinkedinExtension",
      "scraped_by": "NA",
      "job_url": "https://www.linkedin.com/jobs/view/4376745304",
      "job_title": "Business Intelligence Specialist, Office of Innovation",
      "state": "Campus, IL",
      "city": "Campus, IL",
      "location": null,
      "job_description": "About the job\n...",
      "recruiter_info_avaiable": false,    // Note: typo in field name
      "notes": "",
      "salary": null,
      "experience": null,
      "contact_id": null,
      "employer": {
        "id": 34964,
        "name": "University of Cincinnati",
        "website": null,
        "linkedin_url": null,
        "location": "Cincinnati, OH",
        "do_not_apply": false,
        "referrel_available": false,       // Note: typo in field name
        "likely_defense": false,
        "h1b_filed": false,
        "everified": false,
        "recent_international_hires": false,
        "career_url": null,
        "company_size": null,
        "industry": "Universities And Colleges, Educational Institutions, Educational Organizations",
        "summary": "...",
        "last_modified": "2025-11-20T09:59:17.984962"
      },
      "contact": null,
      "tags": [],
      "created_at": "2026-02-25T20:43:12.014951",
      "updated_at": "2026-02-25T20:43:12.014954"
    }
    // ... up to 100 per page
  ],
  "total": 13336,
  "page": 1,
  "size": 100,
  "total_pages": 134
}
```

**Sample Employer with rich data (Cloudera):**
```json
{
  "id": 10478,
  "name": "Cloudera",
  "website": "https://cloudera.com",
  "linkedin_url": "https://www.linkedin.com/company/cloudera",
  "location": "Santa Clara, CA",
  "do_not_apply": false,
  "referrel_available": false,
  "likely_defense": false,
  "h1b_filed": true,
  "everified": true,
  "recent_international_hires": true,
  "career_url": null,
  "company_size": "1001-5000",
  "industry": "Sales, Business Development, And Consulting",
  "summary": "Our Mission Is To Make Data And Analytics Easy And Accessible, For Everyone...",
  "last_modified": "2025-11-20T07:03:28.928032"
}
```

---

### 4. `GET /api/v1/myjobs/filter`

Filter job applications by pod. Paginated. **Response may be base64-encoded** (see [Quirks](#quirks--notes)).

**Request:**
```
GET /api/v1/myjobs/filter?pod_id=07835570-ebaa-4388-a087-cbe8dc1e4aa3&size=1000&page=1
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pod_id` | string (UUID) | Yes | — | Filter by pod ID |
| `page` | int | No | 1 | Page number (1-indexed) |
| `size` | int | No | — | Items per page |

**Response:** `200 OK` (2,243,030 bytes, 1,535ms)

```jsonc
{
  "myjobs": [
    {
      "id": 1958269,
      "original_job_id": 1168129,
      "applied_by": "gauri.m@wynisco.com",
      "submitted_for": "ramsankarharikrishnan@gmail.com",
      "status": "Applied",
      "applied_at": "2026-02-25T20:26:14.546158",
      "resume_link": "https://docs.google.com/document/d/.../edit?tab=t.0",
      "resume_link_pdf": "https://docs.google.com/document/d/.../export?format=pdf",
      "scraped_by": "gauri.m@wynisco.com",
      "pod_id": "07835570-ebaa-4388-a087-cbe8dc1e4aa3",
      "myjobsnotes": "",
      "current_interview_status": null,
      "created_at": "2026-02-25T18:11:55.422415",
      "updated_at": "2026-02-25T20:26:14.547045",
      "pod": {
        "id": "07835570-ebaa-4388-a087-cbe8dc1e4aa3",
        "pod_name": "Dev_0010",
        "candidate_onboarded_date": "2026-01-15T00:00:00",
        "candidate_end_date": "2026-03-15T00:00:00",
        "meeting_url": "https://meet.google.com/axp-vhtv-qck?authuser=0",
        "resume_format": null,
        "current_audit_cycle_id": "d5252f24-ad98-4829-b399-1f02249298ba",
        "audited_at": "2026-02-25T08:26:03.861715Z"
      },
      "job": {
        "id": 1168129,
        "source": "LinkedinExtension",
        "scraped_by": "adityapawar@wynisco.com",
        "job_url": "https://www.linkedin.com/jobs/view/4377425210",
        "job_title": "Senior Software Engineer - ML Platform",
        "state": "Palo Alto, CA",
        "city": "Palo Alto, CA",
        "location": null,
        "job_description": "...",
        "recruiter_info_avaiable": false,
        "notes": "",
        "salary": null,
        "experience": null,
        "contact_id": null,
        "employer": {
          "id": 60596,
          "name": "Latitude AI",
          "website": null,
          "linkedin_url": null,
          "location": null,
          "do_not_apply": false,
          "referrel_available": false,
          "likely_defense": false,
          "h1b_filed": false,
          "everified": false,
          "recent_international_hires": false,
          "career_url": null,
          "company_size": null,
          "industry": null,
          "summary": null,
          "last_modified": "2025-09-05T15:46:18.745789"
        },
        "contact": null,
        "tags": [],
        "created_at": "2026-02-25T04:08:29.175959",
        "updated_at": "2026-02-25T04:08:29.175962"
      }
    }
    // ... up to 1000 per page
  ],
  "total": 8657,
  "page": 1,
  "size": 1000,
  "total_pages": 9
}
```

**Status distribution (from 1000-record sample):**

| Status | Count |
|--------|-------|
| Applied | 595 |
| Not Applicable | 343 |
| Pending | 45 |
| Expired | 17 |

**Applied-by staff distribution:**

| Staff Email | Count |
|-------------|-------|
| gauri.m@wynisco.com | 293 |
| snehal.wynisco@gmail.com | 259 |
| sakshiid.wynisco@gmail.com | 227 |
| rehan@wynisco.com | 174 |
| (empty string) | 43 |
| supriya.wynisco@gmail.com | 4 |

---

## Inferred Endpoints

> These endpoints are **NOT confirmed** — they are reasonable guesses based on data models and standard REST patterns.

### Authentication

#### `POST /api/v1/auth/login`

Login or signup. Expected request body:

```jsonc
{
  "email": "user@example.com",
  "password": "..."
}
```

Expected to set an httpOnly cookie for session auth.

#### `POST /api/v1/auth/logout`

Logout / clear session cookie.

---

### MyJobs (Applications)

#### `POST /api/v1/myjobs/`

Create a new job application record.

```jsonc
// Probable request body
{
  "original_job_id": 1168129,
  "submitted_for": "candidate@gmail.com",
  "status": "Pending",
  "pod_id": "07835570-ebaa-4388-a087-cbe8dc1e4aa3",
  "resume_link": "https://docs.google.com/document/d/.../edit",
  "myjobsnotes": ""
}
```

#### `PUT /api/v1/myjobs/{id}` or `PATCH /api/v1/myjobs/{id}`

Update application status or details.

```jsonc
// Probable request body
{
  "status": "Applied",          // Applied | Not Applicable | Pending | Expired
  "applied_at": "2026-02-25T20:26:14.546158",
  "resume_link": "...",
  "resume_link_pdf": "...",
  "myjobsnotes": "..."
}
```

#### `DELETE /api/v1/myjobs/{id}`

Delete an application record.

---

### Jobs

#### `GET /api/v1/jobs/{id}`

Get a single job by ID.

```
GET /api/v1/jobs/1169980
```

Expected to return a single `Job` object (same schema as items in the list response).

#### `POST /api/v1/jobs/`

Create a new job listing (used by scrapers / extensions).

#### `PUT /api/v1/jobs/{id}`

Update a job listing.

---

### Employers

#### `GET /api/v1/employers/`

List employers. Likely paginated with the same `page`/`size` pattern.

#### `GET /api/v1/employers/{id}`

Get a single employer by ID.

---

### Contacts

#### `GET /api/v1/contacts/`

List contacts. Referenced by `Job.contact_id`.

#### `GET /api/v1/contacts/{id}`

Get a single contact by ID.

---

### Pods

#### `POST /api/v1/pods/`

Create a new pod.

#### `PUT /api/v1/pods/{id}`

Update a pod.

#### `DELETE /api/v1/pods/{id}`

Delete a pod.

---

### Candidate Profile

#### `PUT /api/v1/auth/me` or `PATCH /api/v1/users/{id}`

Update user profile / candidate profile fields.

---

## Enums & Known Values

### `role` (User)

| Value | Confirmed | Notes |
|-------|-----------|-------|
| `candidate` | Yes | Observed in HAR |
| `instructor` | Inferred | Has `instructor_profile` sub-object |
| `consultant` | Inferred | Has `consultant_profile` sub-object |
| `alumni` | Inferred | Has `alumni_profile` sub-object |

### `privilege` (User)

| Value | Confirmed |
|-------|-----------|
| `user` | Yes |
| `admin` | Inferred |

### `status` (MyJob)

| Value | Confirmed | Sample Count |
|-------|-----------|-------------|
| `Applied` | Yes | 595 |
| `Not Applicable` | Yes | 343 |
| `Pending` | Yes | 45 |
| `Expired` | Yes | 17 |

### `source` (Job)

| Value | Confirmed |
|-------|-----------|
| `LinkedinExtension` | Yes |
| `HiringCafe` | Yes |
| `Jobright` | Yes |
| `SimplyHired` | Yes |
| `Glassdoor` | Yes |
| `SimplyHiredExtension` | Yes |
| `Others` | Yes |

### `visa_status` (CandidateProfile)

| Value | Confirmed |
|-------|-----------|
| `F1 OPT` | Yes |
| `H1B` | Inferred |
| `GC` | Inferred |
| `Citizen` | Inferred |

### `company_size` (Employer)

Observed value: `"1001-5000"`. Likely uses standard range brackets.

---

## Pagination

All paginated endpoints use a consistent envelope:

```jsonc
{
  "<collection>": [...],  // "pods", "jobs", or "myjobs"
  "total": 13336,         // Total records matching the query
  "page": 1,              // Current page (1-indexed)
  "size": 100,            // Requested page size
  "total_pages": 134      // ceil(total / size)
}
```

| Endpoint | Collection Key | Observed Total | Page Size Used |
|----------|---------------|----------------|----------------|
| `/pods/` | `pods` | 58 | 100 |
| `/jobs/` | `jobs` | 13,336 | 100 |
| `/myjobs/filter` | `myjobs` | 8,657 | 1,000 |

---

## Quirks & Notes

### 1. Trailing Slash Redirect

`GET /api/v1/pods` (without trailing slash) returns a **307 Temporary Redirect** to `/api/v1/pods/`. This adds an unnecessary round trip (~264ms). Always include the trailing slash on collection endpoints.

### 2. Base64-Encoded Response on `/myjobs/filter`

The HAR shows the `/myjobs/filter` response with `content.encoding: "base64"`. This could be:
- **Server behavior:** The server actually base64-encodes the JSON response body
- **HAR artifact:** Chrome DevTools sometimes base64-encodes large response bodies in HAR exports

The raw body starts with `eyJteWpvYnMiOlt7Im9yaWdpbmFs...` which decodes to `{"myjobs":[{"original_...`. Direct API testing would confirm which case applies.

### 3. Field Name Typos

| Field | Location | Should Be |
|-------|----------|-----------|
| `recruiter_info_avaiable` | Job | `recruiter_info_available` |
| `referrel_available` | Employer | `referral_available` |

These are the actual API field names — clients must use the misspelled versions.

### 4. Massive Payload Duplication

Each `MyJob` in the `/myjobs/filter` response embeds the **full** `Job` object including the complete `job_description` text and full `Employer` object. A single page of 1,000 records produces a ~2.2 MB response. The full dataset (8,657 records across 9 pages) would be ~19.5 MB.

### 5. Inconsistent Null vs Empty String

Some fields use `null` for absent values, others use `""` (empty string). Examples:
- `notes`: `""` (empty string)
- `salary`: `null`
- `website`: sometimes `null`, sometimes `""`

### 6. Inconsistent Datetime Formats

Some datetimes include timezone info (`Z` suffix), others are naive:
- **With timezone:** `"2026-02-25T08:26:03.861715Z"` (`audited_at`, `created_at` on User)
- **Without timezone:** `"2026-01-15T00:00:00"` (`candidate_onboarded_date`, Job timestamps)

### 7. Unused / Always-Null Fields

Several fields exist in the schema but had no populated values in the observed data:
- `Job.location` — always `null` (location info is in `state` and `city` instead)
- `Job.contact` / `Job.contact_id` — always `null`
- `Job.tags` — always `[]`
- `MyJob.current_interview_status` — always `null` (even for 595 "Applied" records)
- `Pod.resume_format` — always `null`

### 8. No Visible Auth Tokens

No `Authorization` header or `cookie` header appears in the HAR. Authentication is likely via httpOnly cookies that Chrome's HAR export strips. The `access-control-allow-credentials: true` response header confirms cookie-based cross-origin auth.

### 9. `city` and `state` Overlap

Job `city` and `state` fields often contain the same value (e.g., both set to `"Campus, IL"` or `"Palo Alto, CA"`). The `location` field is always `null`. The location logic appears inconsistent.

### 10. HAR Capture Summary

| # | Method | Endpoint | Status | Size | Time |
|---|--------|----------|--------|------|------|
| 1 | GET | `/api/v1/pods` | 307 | 0 B | 264ms |
| 2 | GET | `/api/v1/auth/me` | 200 | 13,870 B | 299ms |
| 3 | GET | `/api/v1/pods/` | 200 | 18,727 B | 274ms |
| 4 | GET | `/api/v1/jobs/?page=1&size=100` | 200 | 199,536 B | 624ms |
| 5 | GET | `/api/v1/myjobs/filter?pod_id=...&size=1000&page=1` | 200 | 2,243,030 B | 1,535ms |
