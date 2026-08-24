import os

# Force Playwright to use the browsers installed with the Python package
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

import json
import re
from datetime import datetime

import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIG
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "service_account.json"
)

WORKSHEET_NAME = os.getenv(
    "WORKSHEET_NAME",
    "Job Applications"
)

GEMINI_MODEL = "gemini-3.6-flash"


# ============================================================
# RESUME PROFILE
# ============================================================

RESUME_PROFILE = """
Java Backend Developer with 3+ years of experience.

Core skills:

Java,
Java 11,
Java 17,
Java 21,
Spring Core,
Spring MVC,
Spring Boot,
Hibernate,
JPA,
Microservices,
REST APIs,
SOAP APIs,
Spring Security,
JWT,
OpenFeign,
Kafka,
RabbitMQ,
SQL,
Oracle,
MySQL,
PostgreSQL,
Docker,
Kubernetes,
OpenShift,
Git,
GitLab CI/CD,
AWS,
ServiceNow,
Microsoft Graph APIs,
JUnit,
Mockito.

Additional skills:

Python,
Playwright,
Selenium,
PowerShell,
React,
Next.js,
Neo4j,
Redis.

Experience includes enterprise backend development,
microservices, REST APIs, integrations,
ITSM/ServiceNow, alert management,
notification services and automation.
"""


# ============================================================
# PLAYWRIGHT
# ============================================================

def extract_job_page(url):

    print("Opening:", url)

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 900
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        )

        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            # Scroll for lazy loaded content
            for _ in range(5):

                page.mouse.wheel(
                    0,
                    1000
                )

                page.wait_for_timeout(
                    500
                )

            title = page.title()

            body_text = page.locator(
                "body"
            ).inner_text()

            print(
                "Extracted characters:",
                len(body_text)
            )

            return {
                "url": url,
                "title": title,
                "text": body_text
            }

        finally:

            browser.close()


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = re.sub(
        r"\r\n",
        "\n",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# GEMINI
# ============================================================

def analyze_job(job):

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=120000
        )
    )

    job_text = clean_text(
        job["text"]
    )

    prompt = f"""
You are an expert recruitment assistant.

Analyze this job posting and compare it with the candidate profile.

Return ONLY valid JSON.

Do not return markdown.
Do not return ```json.
Do not add explanations.

If information is unavailable use:
"Not Mentioned"

Return exactly:

{{
    "company": "",
    "job_title": "",
    "location": "",
    "work_mode": "",
    "job_type": "",
    "experience": "",
    "required_skills": [],
    "preferred_skills": [],
    "education": "",
    "responsibilities": [],
    "job_description": "",
    "skills_match": "",
    "matching_skills": [],
    "missing_skills": [],
    "match_percentage": 0,
    "recommendation": "",
    "notes": ""
}}

Skills Match must be:

High
Medium
Low

Candidate profile:

{RESUME_PROFILE}

Job URL:

{job["url"]}

Page title:

{job["title"]}

Job content:

{job_text}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return parse_json(
        response.text
    )


# ============================================================
# PARSE JSON
# ============================================================

def parse_json(text):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:

        return json.loads(
            text.strip()
        )

    except json.JSONDecodeError:

        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end >= 0:

            return json.loads(
                text[start:end + 1]
            )

        raise


# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================

def get_worksheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=scopes
    )

    client = gspread.authorize(
        credentials
    )

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    worksheet = spreadsheet.worksheet(
        WORKSHEET_NAME
    )

    return worksheet


# ============================================================
# DUPLICATE CHECK
# ============================================================

def find_existing_job(
    worksheet,
    job_url
):

    headers = worksheet.row_values(1)

    if "Job Link" not in headers:

        return None

    column = (
        headers.index("Job Link") + 1
    )

    urls = worksheet.col_values(
        column
    )

    for row_number, value in enumerate(
        urls,
        start=1
    ):

        if value.strip() == job_url.strip():

            return row_number

    return None


# ============================================================
# BUILD SHEET ROW
# ============================================================

def build_row(
    data,
    job_url
):

    applied_date = datetime.now().strftime(
        "%d-%b-%Y"
    )

    required = ", ".join(
        data.get(
            "required_skills",
            []
        )
    )

    preferred = ", ".join(
        data.get(
            "preferred_skills",
            []
        )
    )

    responsibilities = "\n".join(
        "- " + x
        for x in data.get(
            "responsibilities",
            []
        )
    )

    matching = ", ".join(
        data.get(
            "matching_skills",
            []
        )
    )

    missing = ", ".join(
        data.get(
            "missing_skills",
            []
        )
    )

    description = data.get(
        "job_description",
        ""
    )

    jd_cell = (
        f"Experience: "
        f"{data.get('experience', 'Not Mentioned')}\n\n"

        f"Education: "
        f"{data.get('education', 'Not Mentioned')}\n\n"

        f"Required Skills:\n"
        f"{required}\n\n"

        f"Preferred Skills:\n"
        f"{preferred}\n\n"

        f"Responsibilities:\n"
        f"{responsibilities}\n\n"

        f"Job Description:\n"
        f"{description}"
    )

    notes = (
        f"Match Percentage: "
        f"{data.get('match_percentage', 0)}%\n\n"

        f"Matching Skills:\n"
        f"{matching}\n\n"

        f"Missing Skills:\n"
        f"{missing}\n\n"

        f"Recommendation:\n"
        f"{data.get('recommendation', '')}\n\n"

        f"{data.get('notes', '')}"
    )

    return {

        "Applied Date":
            applied_date,

        "Company":
            data.get(
                "company",
                "Not Mentioned"
            ),

        "Job Title":
            data.get(
                "job_title",
                "Not Mentioned"
            ),

        "Job Location":
            data.get(
                "location",
                "Not Mentioned"
            ),

        "Source":
            "Job URL",

        "Job Link":
            job_url,

        "Job Description / Requirements":
            jd_cell,

        "Skills Match":
            data.get(
                "skills_match",
                "Not Mentioned"
            ),

        "Applied Status":
            "",

        "Actual Status":
            "Not Applied",

        "Next Follow-up":
            "",

        "Notes":
            notes
    }


# ============================================================
# WRITE TO GOOGLE SHEETS
# ============================================================

def save_to_google_sheet(
    data,
    job_url
):

    worksheet = get_worksheet()

    existing_row = find_existing_job(
        worksheet,
        job_url
    )

    row_data = build_row(
        data,
        job_url
    )

    headers = worksheet.row_values(
        1
    )

    row = []

    for header in headers:

        row.append(
            row_data.get(
                header,
                ""
            )
        )

    if existing_row:

        # Update existing row
        worksheet.update(
            f"A{existing_row}",
            [row],
            value_input_option="USER_ENTERED"
        )

        return {
            "action": "updated",
            "row": existing_row
        }

    else:

        # Add new row
        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED"
        )

        return {
            "action": "added",
            "row": len(
                worksheet.get_all_values()
            )
        }


# ============================================================
# MAIN PROCESS
# ============================================================

def process_job(url):

    if not url:

        raise ValueError(
            "Job URL is required."
        )

    if not url.startswith(
        ("http://", "https://")
    ):

        raise ValueError(
            "Please provide a valid HTTP/HTTPS URL."
        )

    # 1. Playwright
    print("STEP 1: Extracting job page...")

    job = extract_job_page(
        url
    )

    if not job:

        raise RuntimeError(
            "Unable to extract job page."
        )

    # 2. Gemini
    print(
        "STEP 2: Analyzing with Gemini..."
    )

    data = analyze_job(
        job
    )

    # 3. Google Sheets
    print(
        "STEP 3: Updating Google Sheets..."
    )

    sheet_result = save_to_google_sheet(
        data,
        url
    )

    print(
        "STEP 4: Completed."
    )

    return {
        "success": True,
        "job": data,
        "sheet": sheet_result
    }
