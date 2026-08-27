# LinkedIn Profile Scraper API

A professional, self-hosted API that accepts a LinkedIn profile URL and returns structured profile information as clean JSON. This API reverse-engineers LinkedIn's internal "Voyager" API endpoints using cookie-based authentication, bypassing complex browser-automation systems (like Puppeteer/Selenium) and returning clean data directly from LinkedIn's internal GraphQL/REST services.

## Features
* **URL Parsing**: Automatically extracts LinkedIn profile public IDs from standard URLs.
* **Rich Structure**: Returns name, headline, location, about, experience, education, skills, certifications, languages, projects, volunteer work, honors, and contact details.
* **Authentication Security**: Uses active session cookies (`li_at` and `JSESSIONID`) configured securely via environment variables to keep your credentials safe.
* **Fast & Lightweight**: Built on **FastAPI** with **Pydantic** data models. No headless browser overhead.
* **Auto-generated Documentation**: Interactive API testing playground available out-of-the-box (Swagger & Redoc).

---

## 🛠️ Local Setup & Installation

### Prerequisites
* Python 3.10 or higher
* An active LinkedIn account (to obtain session cookies)

### 1. Clone & Set Up Directory
Create a virtual environment and install the required Python packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (Command Prompt)
venv\Scripts\activate.bat
# On Windows (PowerShell)
.\venv\Scripts\activate.ps1
# On Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Open `.env` and configure:
1. Open a desktop web browser (Chrome, Firefox, Safari), log in to [LinkedIn](https://www.linkedin.com).
2. Open Developer Tools (press **F12** or **right-click -> Inspect**).
3. Navigate to the **Application** tab (Chrome) or **Storage** tab (Firefox).
4. Under **Cookies**, select `https://www.linkedin.com`.
5. Copy values for:
   * `li_at`: The main session token (a long string beginning with `AQED...`).
   * `JSESSIONID`: The CSRF token (looks like `"ajax:xxxxxxxxxxxxxxxxx"`). Keep the double quotes in your `.env` value.
6. Paste them into your `.env` file.

### 3. Run the Server
Start the development server using:

```bash
uvicorn main:app --reload
```

By default, the server runs on `http://localhost:8000`. 
Open `http://localhost:8000/docs` in your browser to view the interactive API documentation.

---

## 📖 API Documentation

### 1. Health Check
* **Endpoint**: `GET /health`
* **Description**: Verifies if the backend credentials/cookies are successfully loaded.
* **Response**:
```json
{
  "status": "healthy",
  "message": "API is configured and ready.",
  "auth_method_configured": "cookies"
}
```

### 2. Scrape LinkedIn Profile
* **Endpoint**: `POST /api/v1/profile`
* **Request Content-Type**: `application/json`
* **Request Body**:
```json
{
  "profile_url": "https://www.linkedin.com/in/williamhgates/"
}
```
* **Response Example (Clean & Structured JSON)**:
```json
{
  "public_id": "williamhgates",
  "urn_id": "ACoAAA8WYHgB-AW9gDq...",
  "first_name": "Bill",
  "last_name": "Gates",
  "full_name": "Bill Gates",
  "headline": "Co-chair, Bill & Melinda Gates Foundation",
  "location": "Seattle, Washington, United States",
  "about": "Co-chair of the Bill & Melinda Gates Foundation...",
  "profile_image_url": "https://media.licdn.com/dms/image/v2/...",
  "experience": [
    {
      "company_name": "Bill & Melinda Gates Foundation",
      "company_logo_url": "https://media.licdn.com/dms/image/...",
      "title": "Co-chair",
      "location": "Seattle, WA",
      "description": "Working together to build a world where every person has the chance to live a healthy, productive life.",
      "time_period": {
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
      "school_name": "Harvard University",
      "school_logo_url": "https://media.licdn.com/dms/image/...",
      "degree": "Honorary Doctor of Laws",
      "field_of_study": null,
      "description": null,
      "time_period": {
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
    },
    {
      "name": "Software Development"
    }
  ],
  "certifications": [],
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

---

## 🚀 Public HTTPS Deployment

You can deploy this API publicly over HTTPS using cloud hosting platforms like **Vercel**, **Render**, or **Railway**.

### Option A: Vercel (Fastest & Serverless)
Vercel supports Python serverless functions natively. We have pre-configured a `vercel.json` file in the root.
1. Push this repository to GitHub.
2. Sign up on [Vercel](https://vercel.com) and create a **New Project**.
3. Import your GitHub repository.
4. Vercel will automatically read the `vercel.json` configuration and select the Python runtime.
5. In the **Environment Variables** section, add your credentials:
   * `LINKEDIN_LI_AT` = *[your_li_at_cookie]*
   * `LINKEDIN_JSESSIONID` = *[your_jsessionid_cookie]*
6. Click **Deploy**. Vercel will deploy your API serverless and generate a public `https://[project-name].vercel.app` URL.

### Option B: Render
1. Push this repository to GitHub.
2. Sign up on [Render](https://render.com) and create a new **Web Service**.
3. Link your GitHub repository.
4. Select **Python 3** as the runtime.
5. Configure the build and start commands:
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add the following **Environment Variables** in the Render settings:
   * `LINKEDIN_LI_AT` = *[your_li_at_cookie]*
   * `LINKEDIN_JSESSIONID` = *[your_jsessionid_cookie]*
7. Click **Deploy**. Render automatically provisions a public HTTPS endpoint.

### Option C: Railway
1. Sign up on [Railway.app](https://railway.app).
2. Create a new project and select **Deploy from GitHub**.
3. Link this repository.
4. Under **Variables**, add your environment variables (`LINKEDIN_LI_AT` and `LINKEDIN_JSESSIONID`).
5. Railway will automatically detect the Python environment and run it. Go to service Settings and generate a public Domain (HTTPS).

---

## 🔍 Technical Approach & Architecture

1. **Undocumented API Mapping**: This API directly targets LinkedIn’s private `voyager/api` endpoints (specifically `/identity/profiles/{public_id}/profileView` and `/identity/profiles/{public_id}/profileContactInfo`). This is the same API used by LinkedIn's official frontend application.
2. **Cookie Auth Integration**: Rather than utilizing unstable browser logging sequences which trigger CAPTCHAs, we bind session cookies directly to the request headers. The `csrf-token` header is derived from `JSESSIONID` (by removing surrounding double-quotes), matching LinkedIn's custom security design.
3. **Data Normalization**: Voyager responses are deeply nested Rest.li structures. The API flattens dates, experience records, logos, and language arrays into standard, predictable JSON structures using Pydantic validation.

---

## ⚠️ Limitations & Notes

* **Cookie Expiry**: LinkedIn session cookies (`li_at`) usually expire in about 6-12 months, or immediately if you manually log out of LinkedIn from the browser where the cookie was captured. If the API returns a authentication error, update your environment variables with new active cookies.
* **Rate Limits**: LinkedIn tracks scraping requests closely. Running this API at high frequencies (e.g., thousands of requests a day on a single cookie set) will trigger safety checkpoints (such as temporary account holds or 429 requests). We recommend limiting requests, adding random delays between consecutive queries, or rotating account cookies if scraping at scale.
* **Contact Information**: Details such as email and phone numbers are only returned if the account associated with the backend cookies is a **1st-degree connection** of the profile being requested. For other users, contact details are hidden by LinkedIn's default privacy rules.
* **Disclaimer**: This tool is for educational purposes. Automated web scraping of LinkedIn violates LinkedIn's Terms of Service. Use it responsibly and at your own risk.
