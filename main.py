import os
import requests
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load all configurations directly from your .env file
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

app = FastAPI(title="ALwrity LinkedIn Sharing Engine")

# =====================================================================
# DATA SCHEMA DEFINITIONS (Pydantic Models)
# =====================================================================

class LinkedInPostRequest(BaseModel):
    """Schema for standard manual header requests"""
    author_urn: str
    text_content: str

class SimplePostRequest(BaseModel):
    """New schema: Expects only raw text since credentials live in the .env background"""
    text_content: str


# =====================================================================
# INTERACTIVE BROWSER INTERFACES (OAuth Authentication Lifecycle)
# =====================================================================

# 1. LANDING ROOT: Direct home user interface
@app.get("/", response_class=HTMLResponse)
def home_dashboard():
    return """
    <html>
        <head><title>ALwrity Engine</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f6f9;">
            <h2>🚀 Welcome to ALwrity LinkedIn Tool</h2>
            <p>Click below to authorize your account without manual URL copying.</p>
            <a href="/login" style="background-color: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; margin-top: 20px;">
                Connect LinkedIn Profile
            </a>
        </body>
    </html>
    """

# 2. LOGIN ROUTE: Relays user authentication to LinkedIn platform instances
@app.get("/login")
def login_via_linkedin():
    if not CLIENT_ID or not REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Missing configuration environment variables.")
        
    linkedin_auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=w_member_social,openid,profile"
    )
    return RedirectResponse(url=linkedin_auth_url)

# 3. INTERCEPTOR CALLBACK: Captures authentication parameters automatically out of the air
@app.get("/callback", response_class=HTMLResponse)
def linkedin_callback(code: str = Query(None), error: str = Query(None)):
    if error:
        return f"<h3 style='color:red;'>Authentication Error: {error}</h3>"
    if not code:
        return "<h3>Error: No background code caught from redirect parameter.</h3>"

    # Swap the short-lived authorization code parameter for your permanent authorization access key
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        token_response = requests.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if token_response.status_code != 200:
            return f"<h3>Backend Token Swap Failure: {token_response.text}</h3>"
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # Query identity profile properties to fetch your user account URN
        user_response = requests.get(
            "https://api.linkedin.com/v2/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_id = user_response.json().get("sub", "UNKNOWN_ID")
        author_urn = f"urn:li:person:{user_id}"

        # Present the dashboard success landing layout to the user
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 650px; margin: 60px auto; padding: 30px; border: 1px solid #e1e4e8; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <h2 style="color: #28a745; margin-bottom: 5px;">✅ Connection Successful!</h2>
                <p style="color:#586069; margin-top:0;">Your FastAPI backend caught the code parameter and exchanged it successfully.</p>
                <hr style="border: 0; border-top: 1px solid #e1e4e8; margin: 20px 0;">
                
                <div style="margin-bottom: 20px;">
                    <label style="font-weight: bold; display: block; margin-bottom: 5px; color: #24292e;">Your Permanent Token (Valid for 2 Months):</label>
                    <textarea style="width:100%; height:80px; padding:10px; font-family:monospace; border:1px solid #cbd5e0; border-radius:6px; background:#f7fafc;" readonly>{access_token}</textarea>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="font-weight: bold; display: block; margin-bottom: 5px; color: #24292e;">Your Ready-to-Use Author URN:</label>
                    <input type="text" style="width:100%; padding:10px; font-family:monospace; border:1px solid #cbd5e0; border-radius:6px; background:#f7fafc;" value="{author_urn}" readonly />
                </div>
                
                <div style="background-color: #ebf8ff; border-left: 4px solid #3182ce; padding: 12px; border-radius: 4px;">
                    <p style="margin: 0; font-size: 14px; color: #2b6cb0; font-weight:500;">
                        💡 <b>Ready for PowerShell:</b> Save these exact values directly into your <b>.env</b> file right now to unlock automated one-command publishing!
                    </p>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return f"<h3 style='color:red;'>Internal Engine Exception: {str(e)}</h3>"


# =====================================================================
# BACKGROUND PUBLISHING API ROUTE ENGINE
# =====================================================================

@app.post("/cli-publish")
def cli_publish_to_linkedin(post_data: SimplePostRequest):
    """
    Automated publishing handler. Fetches your 2-month keys directly 
    out of the .env environment background context variables.
    """
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")
    
    if not token or not author_urn:
        raise HTTPException(
            status_code=500, 
            detail="Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN in your .env file configurations."
        )
        
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_data.text_content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return {"status": "Success", "message": "Post successfully published using background .env configurations!"}


@app.post("/publish")
def publish_to_linkedin(post_data: LinkedInPostRequest, authorization: str = Header(...)):
    """Legacy route: Handshakes raw payloads requiring explicit manual header injection"""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": authorization,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": post_data.author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_data.text_content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"status": "Success", "message": "Post published to LinkedIn!"}