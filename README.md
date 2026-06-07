# ALwrity LinkedIn Share Tool

A lightweight FastAPI-based LinkedIn publishing engine that supports:
- OAuth 2.0 authorization via a local browser callback
- automatic retrieval of a LinkedIn access token and author URN
- background CLI publishing using `.env`-backed credentials
- direct REST forwarding to LinkedIn UGC posts

---

## Features

- `GET /login`: redirects the user to LinkedIn OAuth consent
- `GET /callback`: receives LinkedIn authorization code, exchanges it for an access token, and fetches author URN
- `POST /cli-publish`: publishes text content using `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_AUTHOR_URN` from `.env`
- `POST /publish`: legacy route for manual payload publishing with explicit `Authorization` header

---

## Requirements

- Python 3.10+ (or Python 3.11/3.12)
- `fastapi`
- `uvicorn`
- `requests`
- `python-dotenv`


## Installation

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install fastapi uvicorn requests python-dotenv
```

---

## Configuration

Copy or create a `.env` file in the project root with the following values:

```env
LINKEDIN_CLIENT_ID="your_client_id"
LINKEDIN_CLIENT_SECRET="your_client_secret"
LINKEDIN_REDIRECT_URI="http://127.0.0.1:8000/callback"
LINKEDIN_ACCESS_TOKEN=""
LINKEDIN_AUTHOR_URN=""
```

### LinkedIn app setup

1. Open the LinkedIn Developer Dashboard and select your app.
2. Add the `Share on LinkedIn` product to enable `w_member_social`.
3. In OAuth 2.0 settings, add the redirect URL exactly as:

```text
http://127.0.0.1:8000/callback
```

4. Keep the `Client ID` and `Client Secret` available for `.env`.

> Important: Do not commit actual secrets or access tokens into source control.

---

## Running the API

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

Open `http://127.0.0.1:8000` in your browser.

---

## OAuth Authorization Workflow

1. Visit `http://127.0.0.1:8000`
2. Click `Connect LinkedIn Profile`
3. LinkedIn will prompt for consent
4. After approval, LinkedIn redirects to `/callback`
5. The app exchanges the temporary code for an access token and displays:
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_AUTHOR_URN`

Copy those values and store them in your `.env` file.

---

## Publishing Content

### Background CLI publishing

Use this route once `.env` has `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_AUTHOR_URN` populated:

```bash
curl -X POST http://127.0.0.1:8000/cli-publish \
  -H "Content-Type: application/json" \
  -d '{"text_content": "Hello LinkedIn from ALwrity!"}'
```

This route is the recommended production-style flow for local automation.

### Manual publish with Authorization header

If you want to explicitly provide the Bearer token at request time, use `/publish`:

```bash
curl -X POST http://127.0.0.1:8000/publish \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"author_urn": "urn:li:person:<YOUR_ID>", "text_content": "Hello LinkedIn!"}'
```

---

## Endpoint Summary

- `GET /` - Home page with OAuth connect button
- `GET /login` - Redirects to LinkedIn authorization
- `GET /callback` - Handles redirect callback and token exchange
- `POST /cli-publish` - Publishes text using `.env` credentials
- `POST /publish` - Publishes text using manual Bearer header

---

## Notes and Best Practices

- Keep the `.env` file secret and never commit it.
- The retrieved access token is valid for a limited period (LinkedIn often returns 60 days).
- If the token expires, repeat the OAuth flow via `/login`.
- This tool currently supports only text-only posts (`shareMediaCategory": "NONE"`).

---

## Troubleshooting

- `500 Missing configuration` on `/login`: verify `LINKEDIN_CLIENT_ID` and `LINKEDIN_REDIRECT_URI` are set.
- `Token Exchange Failed` on `/callback`: confirm the redirect URL in LinkedIn app settings matches `.env` exactly.
- `Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN` on `/cli-publish`: update your `.env` with the values returned from `/callback`.

---

## License

This repository is released under the terms of the MIT License.
