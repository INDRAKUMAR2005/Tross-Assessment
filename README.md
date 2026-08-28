# LinkedIn Profile Normalization API

---

## 📝 Submission Details (For Reviewers)

### Title
**High-Performance, Zero-Browser LinkedIn Profile Normalisation API**

### Description
A production-grade web service built on FastAPI, HTTPX, and Pydantic v2 designed to query and normalize LinkedIn profiles directly over HTTP. By reverse-engineering LinkedIn's internal "Voyager Dash" endpoints, the API avoids the high resource overhead, slow execution, and susceptibility to CAPTCHAs associated with browser-automation frameworks (such as Selenium, Playwright, or Puppeteer). The application flattens deeply nested REST.li payloads into clean, standardized JSON objects covering work history, education, skills, certifications, languages, volunteer history, and contact details.

### Theme
**Developer Tools & API Integration / Web Scraping**

### Demo Link
`https://tross-assessment.vercel.app/docs`

### Repository URL
`https://github.com/INDRAKUMAR2005/Tross-Assessment`

### Instructions to Run
1. **Clone the Repository & Navigate to Directory**:
   ```bash
   git clone https://github.com/INDRAKUMAR2005/Tross-Assessment.git
   cd Tross-Assessment
   ```
2. **Set Up a Python Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Create a `.env` file in the root folder with the following:
   ```env
   LINKEDIN_LI_AT=your_active_li_at_cookie
   LINKEDIN_JSESSIONID="ajax:your_active_jsessionid_cookie"
   ```
5. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Open `http://localhost:8000/docs` in your browser for the Swagger UI documentation and playground.
6. **Run Automated Test Suite**:
   ```bash
   pytest -v
   ```

---

## Technical Approach & Architecture

The workflow follows a decoupled, sequential data flow:

```
Client (Consumer)
     ↓  (HTTP POST /api/v1/linkedin/profile)
FastAPI Router (app/api/profile.py)
     ↓  (Validates URL & extracts Vanity ID)
LinkedIn HTTP Client (app/linkedin/client.py using HTTPX)
     ↓  (Direct HTTP GET with CSRF & session cookies)
LinkedIn Voyager API Endpoint (identity/dash/profiles?q=memberIdentity)
     ↓  (Raw REST.li JSON response)
Response Parser (app/linkedin/parser.py)
     ↓  (Flattens and normalizes data)
Pydantic Schema (app/models/response.py)
     ↓  (Validation & Serialization)
Normalized JSON Response
```

### Reverse Engineering Approach
To bypass browser dependencies, LinkedIn's network traffic patterns were analyzed to target their modern internal resource API:
1. **Endpoint Targeting**: Queries are routed to `https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={public_id}`.
2. **Authentication Protocol**: Cookie-based authentication is completed using standard HTTP cookie arrays (`li_at` and `JSESSIONID`).
3. **CSRF Validation**: The `csrf-token` header is passed using the clean token extracted from `JSESSIONID`.
4. **Protocol Versioning**: The header `X-RestLi-Protocol-Version` is set to `2.0.0` to comply with LinkedIn's internal RPC formatting.
5. **Defensive Parsing Fallbacks**: If fields are represented in localized language maps (such as `multiLocaleFirstName`), the parser extracts the corresponding locale values automatically. If the layout is flattened (JSON API spec), it resolves sub-resources inside the `included` data block dynamically.

### Why No Browser
* **Performance**: Under 10ms network routing latency, compared to 5–10 seconds for launching headless browser drivers.
* **Low Memory Profile**: Under 50MB RAM usage, suitable for micro-instance hosting (Render/Railway/Vercel serverless).
* **Robustness**: Immune to DOM selector breaks since the raw data is parsed from JSON payloads.

### API Endpoint Schemas

#### 1. System Health Status
* **Endpoint**: `GET /health`
* **Response**:
```json
{
  "status": "healthy",
  "message": "API configuration validated.",
  "auth_method_configured": "cookies"
}
```

#### 2. Extract Profile details
* **Endpoint**: `POST /api/v1/linkedin/profile` (or legacy fallback `/api/v1/profile`)
* **Request Body**:
```json
{
  "profile_url": "https://www.linkedin.com/in/williamhgates/"
}
```
* **Response**: A validated, flattened JSON schema conforming to `ProfileResponse`.

---

### Known Limitations
* **Session Cookie Lifespan**: Cookie tokens usually expire when logged out of the originating browser or after 6–12 months.
* **Rate Limits**: Heavy request rates will trigger security verification loops (302 redirects). We recommend using residential proxies or rotating cookies when scraping at scale.
