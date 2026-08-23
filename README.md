# AI-Powered Job Application Tracker

An AI-powered job application automation platform that extracts job information from a job posting URL, analyzes the job description using Google Gemini, evaluates the job against a candidate's technical profile, and automatically stores the structured information in Google Sheets.

The project combines **Python, Flask, Playwright, Google Gemini API, and Google Sheets API** to create a simple end-to-end job analysis and tracking workflow.

---

## 📌 Project Overview

Managing multiple job applications manually can become difficult when job descriptions, skills, application status, links, follow-up dates, and interview information are stored across different places.

This project automates the initial job-analysis and tracking process.

Instead of manually copying a job description into a spreadsheet, the user can provide a job URL through a local web interface.

The application then:

1. Opens the job URL using Playwright.
2. Extracts the visible job-page content.
3. Sends the relevant content to Google Gemini.
4. Extracts structured job information.
5. Compares the requirements with the candidate's technical profile.
6. Calculates a skills-match assessment.
7. Checks whether the job already exists in Google Sheets.
8. Adds a new record or updates an existing record.
9. Displays the extracted information in the web UI.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      User / Browser   │
                    │                      │
                    │   Enter Job URL       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Flask Web App   │
                    │                      │
                    │  REST API Endpoint   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Playwright     │
                    │                      │
                    │ Open Job URL         │
                    │ Render JS             │
                    │ Extract Page Content │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Google Gemini     │
                    │                      │
                    │ JD Extraction        │
                    │ Skill Analysis       │
                    │ Resume Matching       │
                    └──────────┬───────────┘
                               │
                         Structured JSON
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Google Sheets     │
                    │                      │
                    │ Job Applications     │
                    │ Add / Update Row     │
                    └──────────────────────┘
```

---

## ✨ Key Features

### 1. Job URL Processing

The user only needs to provide a job posting URL.

Example:

```text
https://example.com/jobs/software-engineer
```

The backend validates the URL and sends it to Playwright.

---

### 2. Browser Automation with Playwright

Playwright is used to open dynamic career websites where the job description may be loaded through JavaScript.

The application:

* Launches Chromium
* Opens the job URL
* Waits for page rendering
* Scrolls the page to trigger lazy-loaded content
* Extracts the page title
* Extracts visible page text
* Closes the browser

This approach supports many modern career portals better than simple HTTP requests.

---

### 3. AI-Based Job Description Analysis

The extracted job content is sent to Google Gemini.

Gemini is instructed to return structured JSON rather than unstructured text.

Example:

```json
{
  "company": "ACI",
  "job_title": "Software Engineer",
  "location": "Not Mentioned",
  "work_mode": "Standard Work Environment",
  "experience": "3+ years",
  "required_skills": [
    "Java",
    "Microservices",
    "REST APIs",
    "Docker",
    "Kubernetes"
  ],
  "preferred_skills": [
    "RAG",
    "MCP",
    "Multi-Agent Systems"
  ],
  "skills_match": "High",
  "match_percentage": 90
}
```

---

## 🤖 AI Skill Matching

The application maintains a candidate technical profile.

Example:

```text
Java
Spring Boot
Spring MVC
Hibernate
JPA
Microservices
REST APIs
Kafka
RabbitMQ
SQL
Oracle
PostgreSQL
Docker
Kubernetes
OpenShift
AWS
ServiceNow
JUnit
Mockito
GitLab CI/CD
```

Gemini compares the job requirements against this profile.

The output includes:

* Skills Match
* Match Percentage
* Matching Skills
* Missing Skills
* Recommendation

Example:

```json
{
  "skills_match": "High",
  "match_percentage": 90,
  "matching_skills": [
    "Java",
    "Spring Boot",
    "Microservices",
    "REST APIs",
    "Docker",
    "Kubernetes"
  ],
  "missing_skills": [
    "LLM Architecture"
  ],
  "recommendation": "Strong match. Recommended to apply."
}
```

---

## 📊 Google Sheets Integration

Instead of automating the Google Sheets UI with Playwright, the project uses the **Google Sheets API**.

This provides a more reliable approach for spreadsheet operations.

The application reads the first-row headers dynamically and maps extracted information to the appropriate columns.

Current sheet:

```text
Job Applications
```

Current columns:

| Column                         | Purpose                                |
| ------------------------------ | -------------------------------------- |
| Applied Date                   | Date record was created                |
| Company                        | Company name                           |
| Job Title                      | Job title                              |
| Job Location                   | Job location                           |
| Source                         | Job source                             |
| Job Link                       | Original job URL                       |
| Job Description / Requirements | Extracted JD and requirements          |
| Skills Match                   | High / Medium / Low                    |
| Applied Status                 | Application status                     |
| Actual Status                  | Current hiring status                  |
| Next Follow-up                 | Follow-up date                         |
| Notes                          | AI analysis and additional information |

---

## 🔎 Duplicate Detection

Before adding a new record, the application checks the `Job Link` column.

Example:

```text
Job URL
   ↓
Search existing Job Link
   ↓
 ┌───────────────┐
 │ Already exists│
 └───────┬───────┘
         │
       Update

OR

 ┌───────────────┐
 │ Doesn't exist │
 └───────┬───────┘
         │
       Add Row
```

This prevents duplicate job records when the same URL is analyzed multiple times.

---

## 🧩 Technology Stack

### Backend

* Python
* Flask

### Browser Automation

* Playwright
* Chromium

### AI

* Google Gemini API
* `google-genai`

### Spreadsheet

* Google Sheets API
* gspread
* Google Authentication

### Frontend

* HTML
* CSS
* JavaScript

### Configuration

* Python `.env`
* Google Service Account

---

## 📁 Project Structure

```text
Job App Tracker/
│
├── app.py
│
├── job_processor.py
│
├── requirements.txt
│
├── .env
│
├── service_account.json
│
└── templates/
    └── index.html
```

### `app.py`

Flask application entry point.

Responsibilities:

* Start Flask server
* Render frontend
* Receive job URL
* Expose `/api/analyze`
* Return JSON response

---

### `job_processor.py`

Contains the core automation logic.

Responsibilities:

* Playwright job-page extraction
* Content cleanup
* Gemini analysis
* JSON parsing
* Google Sheets authentication
* Duplicate detection
* Spreadsheet update

---

### `index.html`

Frontend application.

Responsibilities:

* Job URL input
* Analyze button
* Loading state
* Error handling
* Job result display
* Skill visualization
* Google Sheets update status

---

### `.env`

Stores configuration values and secrets.

Example:

```text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
SPREADSHEET_ID=YOUR_GOOGLE_SHEET_ID
GOOGLE_CREDENTIALS_FILE=service_account.json
WORKSHEET_NAME=Job Applications
```

Secrets should never be committed to source control.

---

## ⚙️ Prerequisites

Install the following:

* Python 3.11+
* Google Cloud account
* Google Sheets
* Gemini API access
* Chromium-compatible environment

Verify Python:

```powershell
python --version
```

---

## 🚀 Installation

### Step 1 — Clone or create the project

```powershell
cd "E:\Automation Platform\Job App Tracker"
```

---

### Step 2 — Create virtual environment

Recommended:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\activate
```

---

### Step 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

---

### Step 4 — Install Playwright Chromium

```powershell
python -m playwright install chromium
```

---

## 🔐 Google Sheets Configuration

The application uses a Google Service Account.

### Create Google Cloud Project

Create a Google Cloud project and enable:

* Google Sheets API
* Google Drive API

Create a Service Account and generate a JSON key.

Store the downloaded file as:

```text
service_account.json
```

---

### Share the Google Sheet

The Google Sheet must be shared with the service-account email.

Example:

```text
job-automation@project-id.iam.gserviceaccount.com
```

Permission:

```text
Editor
```

The spreadsheet must be a native Google Sheet, not an `.xlsx` Office document.

---

## 🔑 Gemini Configuration

Create/configure your Gemini API access and put the key in `.env`:

```text
GEMINI_API_KEY=YOUR_API_KEY
```

Do not expose the key in:

* HTML
* JavaScript
* GitHub
* screenshots
* public repositories

---

## ▶️ Run the Application

Start Flask:

```powershell
python app.py
```

Expected output:

```text
* Running on http://127.0.0.1:5000
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🔄 End-to-End Execution Flow

When the user enters:

```text
https://example.com/job/123
```

the following happens:

### Step 1 — Frontend

JavaScript sends:

```http
POST /api/analyze
```

with:

```json
{
  "url": "https://example.com/job/123"
}
```

### Step 2 — Flask

Flask receives the request and calls:

```python
process_job(url)
```

### Step 3 — Playwright

Playwright:

```text
Launch Chromium
      ↓
Open URL
      ↓
Wait for JavaScript
      ↓
Scroll page
      ↓
Extract visible text
```

### Step 4 — Content Processing

The extracted page content is cleaned:

```text
HTML/page content
       ↓
Remove excessive whitespace
       ↓
Normalize text
       ↓
Prepare AI input
```

### Step 5 — Gemini

Gemini receives:

```text
Candidate Profile
+
Job URL
+
Page Title
+
Job Content
```

and returns structured JSON.

### Step 6 — Validation

Python parses the Gemini response using:

```python
json.loads()
```

If Gemini returns a Markdown JSON block, the wrapper is removed before parsing.

### Step 7 — Duplicate Check

The application searches the `Job Link` column.

```text
Existing URL?
   │
   ├── Yes → Update existing row
   │
   └── No  → Add new row
```

### Step 8 — Google Sheets

The structured information is mapped against the existing spreadsheet headers.

The new row is inserted using:

```python
worksheet.append_row()
```

### Step 9 — Frontend Response

The backend returns:

```json
{
  "success": true,
  "job": {},
  "sheet": {
    "action": "added",
    "row": 6
  }
}
```

The frontend displays the result.

---

## 🧪 Example

Input:

```text
https://ebwg.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/19229
```

Possible output:

```text
Company
ACI

Job Title
Software Engineer

Experience
3+ years

Skills Match
High

Match Percentage
90%

Matching Skills
Java
Microservices
REST APIs
Docker
Kubernetes
AWS
CI/CD

Missing Skills
LLM Architecture

Google Sheets
Job added successfully - Row 6
```

---

## 🛡️ Error Handling

The application handles several common failures:

### Invalid URL

```text
Please provide a valid HTTP/HTTPS URL.
```

### Page extraction failure

```text
Unable to extract job page.
```

### Gemini failure

The backend returns the Gemini/API exception instead of silently failing.

### Invalid Gemini JSON

The parser attempts to extract the JSON object if Gemini returns additional formatting.

### Google Sheets permission failure

The application reports the Google API error.

Common cause:

```text
Service account does not have access
```

Solution:

Share the Google Sheet with the service-account email as Editor.

---

## ⚠️ Known Limitations

Different job portals have different page structures.

Potential challenges include:

* Login-required job pages
* CAPTCHA
* Anti-bot protection
* Cloudflare
* Content loaded inside iframes
* Job descriptions loaded dynamically
* Infinite scrolling
* Location information stored in metadata instead of visible text
* Portals that require authentication

The current implementation extracts visible page content rather than using portal-specific selectors for every career platform.

---

## 💰 API and Cost Considerations

### Google Sheets API

The project uses the Google Sheets API instead of browser-based spreadsheet automation.

This avoids:

* Opening Google Sheets with Playwright
* Clicking cells
* Waiting for UI elements
* UI synchronization issues

Google API usage is subject to Google's quotas and policies.

### Gemini API

Gemini usage depends on the selected model and applicable API pricing/limits.

Because the full job-page content may be sent to Gemini, token usage should be considered when processing many jobs.

Potential optimization:

```text
Full Web Page
      ↓
Extract only relevant JD section
      ↓
Send smaller input to Gemini
```

This can reduce unnecessary model input and improve extraction quality.

---

## 🔒 Security Considerations

Never commit:

```text
service_account.json
.env
API keys
private keys
```

Recommended `.gitignore`:

```text
.env
service_account.json
.venv/
__pycache__/
*.pyc
```

If a credential is accidentally exposed, revoke/rotate it immediately.

---

## 🔮 Future Enhancements

Possible next iterations:

### 1. Live Processing Status

```text
✓ URL received
✓ Job page opened
✓ JD extracted
✓ Gemini analysis completed
✓ Skills matched
✓ Google Sheet updated
✓ Completed
```

### 2. Better Job Content Extraction

Use website-specific extraction strategies for:

* Workday
* Oracle
* iCIMS
* LinkedIn
* Greenhouse
* Lever
* Indeed

### 3. Resume Matching

Upload a resume and dynamically compare:

```text
Resume
   +
Job Description
   ↓
Gemini
   ↓
Match Score
Missing Skills
Resume Recommendations
```

### 4. Application Tracking Dashboard

Add:

```text
Total Applications
Applications This Month
Interview Scheduled
Rejected
Offers
Pending Follow-up
High Match Jobs
```

### 5. Authentication

Add user authentication before exposing the application outside localhost.

### 6. Background Processing

For larger workloads:

```text
Flask
  ↓
Task Queue
  ↓
Playwright Worker
  ↓
Gemini
  ↓
Google Sheets
```

### 7. Containerization

Package the application using Docker.

Potential deployment:

```text
Docker
   ↓
Cloud VM / AWS
   ↓
Flask
   ↓
Playwright
   ↓
Gemini
   ↓
Google Sheets
```

---

## 📈 Future Architecture

```text
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Web Frontend   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Flask / API    │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │  Playwright  │      │ Task Queue   │
          └──────┬───────┘      └──────┬───────┘
                 │                     │
                 └──────────┬──────────┘
                            ▼
                   ┌─────────────────┐
                   │  Gemini AI      │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Structured JSON │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Google Sheets   │
                   └─────────────────┘
```

---

## 🎯 Engineering Goals

This project demonstrates practical implementation of:

* AI-assisted automation
* Browser automation
* REST API development
* Structured LLM output
* Prompt engineering
* Resume/job matching
* Google API integration
* Cloud service authentication
* Duplicate detection
* Data normalization
* Frontend/backend integration
* Error handling
* Configuration management
* Secure credential handling

---

## 📌 Disclaimer

This project is intended for personal job-search organization and automation.

Users should respect the terms of service, robots policies, authentication requirements, rate limits, and anti-automation policies of individual job portals.

The project does not attempt to bypass CAPTCHA, authentication controls, or other security mechanisms.

---

## 👨‍💻 Project Status

**Current Version:** Local MVP

**Current workflow:**

```text
Job URL
   ↓
Playwright
   ↓
Gemini
   ↓
Skill Match
   ↓
Google Sheets
   ↓
Web UI Result
```

The project can be extended into a complete job-search management platform with dashboards, resume optimization, interview tracking, follow-up automation, and analytics.
