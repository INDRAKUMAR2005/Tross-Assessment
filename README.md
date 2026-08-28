# LinkedIn Profile API

A production-quality Python service built using FastAPI, HTTPX, and Pydantic v2. This project implements a direct, reverse-engineered HTTP integration targeting LinkedIn's internal endpoints to retrieve and normalize public profiles as structured JSON without using any web browsers or UI automation tools.

## Project Overview

This repository contains the solution for the Tross hiring challenge. The system is designed to programmatically fetch LinkedIn user profiles by communicating directly over HTTP/HTTPS, bypassing standard browser-driven scrapers (e.g. Playwright, Selenium, or Puppeteer). This eliminates browser rendering overhead, reduces RAM utilization, and provides high-performance data normalization.

## System Architecture

The workflow follows a decoupled, sequential data flow:

```
Client (Consumer)
     ↓  (HTTP POST /api/v1/linkedin/profile)
FastAPI Router (app/api/profile.py)
     ↓  (Validates URL & extracts Vanity ID)
LinkedIn HTTP Client (app/linkedin/client.py using HTTPX)
     ↓  (Direct HTTP GET with CSRF & session cookies)
LinkedIn Voyager API Endpoint (identity/profiles/...)
     ↓  (Raw REST.li JSON response)
Response Parser (app/linkedin/parser.py)
     ↓  (Flattens and normalizes data)
Pydantic Schema (app/models/response.py)
     ↓  (Validation & Serialization)
Normalized JSON Response
```

## Reverse Engineering Approach

To achieve programmatic data extraction without browser automation, the HTTP communications of LinkedIn's frontend web application were mapped using network analysis tools:

1. **Endpoint Discovery**: The relevant profile endpoints were identified by monitoring request patterns under the network inspection panel. The primary resource views are located under LinkedIn's private Voyager REST API layer:
   * Profile Details: `https://www.linkedin.com/voyager/api/identity/profiles/{public_id}/profileView`
   * Contact Details: `https://www.linkedin.com/voyager/api/identity/profiles/{public_id}/profileContactInfo`
2. **HTTP Method**: Standard `GET` operations are used to fetch the data.
3. **Required Parameters**: No query parameters are mandatory. The request URL contains the profile's public vanity identifier (e.g. `williamhgates`) as a path parameter.
4. **Required Headers**: The endpoint expects the following headers to pass system checks:
   * `Csrf-Token`: Must match the CSRF value contained within the active session cookies.
   * `X-RestLi-Protocol-Version`: Configured to `2.0.0` to comply with LinkedIn's Rest.li interface.
   * `User-Agent`: Mimics a standard modern desktop browser.
5. **Authentication**: Cookie-based authentication is utilized. The HTTP client attaches the `li_at` (session token) and `JSESSIONID` (CSRF token) values directly to the HTTP cookie headers.
6. **Response Structure**: The raw JSON payload consists of nested structures containing properties for profiles, positions, academic history, endorsements, certifications, and languages.
7. **Response Parsing**: The parser traverses the nested raw dictionaries, flattens date objects (`startDate` / `endDate` containing year/month pairs), maps attributes to standard keys, and handles missing properties gracefully.
8. **Pagination Handling**: Profile subsections such as experience or education lists are retrieved in a single payload. If pagination is needed on larger lists, the client handles request sequences through secondary sub-resource queries.
9. **Error Handling**: Custom domain exception handlers map HTTP response codes to structured API responses:
   * `401 Unauthorized` -> `LINKEDIN_AUTH_FAILED`
   * `403 Forbidden` -> `LINKEDIN_ACCESS_DENIED`
   * `404 Not Found` -> `PROFILE_NOT_FOUND`
   * `429 Too Many Requests` -> `LINKEDIN_RATE_LIMITED`
   * Upstream schema changes -> `LINKEDIN_RESPONSE_CHANGED`

## Why No Browser

The implementation communicates directly with LinkedIn endpoints using HTTP requests and does not use Selenium, Playwright, Puppeteer, Chromium, or browser automation. 

By eliminating the browser environment entirely, the service achieves:
* Startup times under 1 second.
* Minimal memory footprint suitable for serverless functions.
* Clean machine-to-machine data ingestion.

## API Documentation

### 1. Health Status
* **Endpoint**: `GET /health`
* **Response**:
```json
{
  "status": "healthy",
  "message": "API configuration validated.",
  "auth_method_configured": "cookies"
}
```

### 2. Extract Profile
* **Endpoint**: `POST /api/v1/linkedin/profile` (or fallback `/api/v1/profile`)
* **Headers**: `Content-Type: application/json`
* **Request Body**:
```json
{
  "profile_url": "https://www.linkedin.com/in/williamhgates/"
}
```

## Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/linkedin/profile" \
     -H "Content-Type: application/json" \
     -d '{"profile_url": "https://www.linkedin.com/in/williamhgates/"}'
```

## Example Response

```json
{
  "public_id": "williamhgates",
  "urn_id": "ACoAAA8WYHgB-AW9gDq...",
  "firstName": "Bill",
  "lastName": "Gates",
  "full_name": "Bill Gates",
  "headline": "Co-chair, Bill & Melinda Gates Foundation",
  "geoLocationName": "Seattle, Washington, United States",
  "summary": "Co-chair of the Bill & Melinda Gates Foundation...",
  "displayPictureUrl": "https://media.licdn.com/dms/image/v2/...",
  "experience": [
    {
      "companyName": "Bill & Melinda Gates Foundation",
      "companyLogoUrl": "https://media.licdn.com/dms/image/...",
      "title": "Co-chair",
      "locationName": "Seattle, WA",
      "description": "Working together to build a world where every person has the chance to live a healthy, productive life.",
      "timePeriod": {
        "startDate": {
          "year": 2000,
          "month": 1
        },
        "endDate": null
      }
    }
  ],
  "education": [
    {
      "schoolName": "Harvard University",
      "schoolLogoUrl": "https://media.licdn.com/dms/image/...",
      "degreeName": "Honorary Doctor of Laws",
      "fieldOfStudy": null,
      "description": null,
      "timePeriod": {
        "startDate": {
          "year": 1973
        },
        "endDate": {
          "year": 1975
        }
      }
    }
  ],
  "skills": [
    {
      "name": "Philanthropy"
    }
  ],
  "certifications": [
    {
      "name": "Certified Professional Scraper",
      "authority": "Scraper Corp",
      "licenseNumber": "CPS-12345",
      "timePeriod": {
        "startDate": {
          "year": 2020,
          "month": 5
        },
        "endDate": null
      },
      "url": "https://cert.example.com/cps-12345"
    }
  ],
  "languages": [
    {
      "name": "English",
      "proficiency": "Native or bilingual proficiency"
    }
  ],
  "projects": [],
  "volunteer": [],
  "honors": [],
  "contact_info": {
    "email": "bill.gates@example.com",
    "phone_numbers": [],
    "websites": [
      "https://www.gatesnotes.com"
    ],
    "twitter": [],
    "birthdate": "1955-10-28"
  }
}
```

## Setup and Installation

1. **Clone project and initialize Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Settings**:
Copy `.env.example` to `.env` and fill in your active session credentials extracted from your browser inspector tab.

4. **Launch Local Server**:
```bash
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description | Example |
| :--- | :--- | :--- |
| `LINKEDIN_LI_AT` | Active session authentication cookie value | `AQED...` |
| `LINKEDIN_JSESSIONID` | CSRF token key value | `"ajax:XXXXXXXX"` |
| `API_KEY_ENABLED` | Set `true` to enable X-API-Key route security | `false` |
| `API_KEY` | Header key value matching `X-API-Key` | `secret-token` |

## Testing

The project uses `pytest` for unit and integration testing. Real HTTP connections are mocked using static response fixtures to ensure fast, deterministic offline testing:

```bash
python -m pytest -v
```

## Deployment

### Render Blueprint
This project is configured with a `render.yaml` specification for zero-config deployments. Simply push your code, import the service, and populate environment variables.

### Railway / Vercel
Deploy using the native Python runtime. Set your start command to:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Known Limitations

* **Cookie Expiry**: The `li_at` cookie expires dynamically when you log out from your web browser sessions or after a duration determined by LinkedIn (typically 6-12 months).
* **Rate Limiting**: Query frequencies are subject to LinkedIn rate limits. Running at excessive velocities may trigger temporary session suspension or require solving CAPTCHAs via web browser logins.
* **Response Changes**: Undocumented internal APIs may change formats. The app handles this using a defensive parser that reports `LINKEDIN_RESPONSE_CHANGED` warnings when structural mismatches are detected.
* **Privacy Restrictions**: Private profiles and certain contact information may only be accessible depending on the 1st-degree connection status of the authenticated session.

## Security

Private configuration keys, CSRF headers, and cookies must be stored strictly in the `.env` file. They are ignored by Git through `.gitignore` and must never be committed to shared repositories.
