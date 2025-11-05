from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
import uvicorn
import secrets
import os

from models import ScreeningResponse, MatchScoreBreakdown
from resume_parser import ResumeParser
from matching_engine import MatchingEngine
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware


# Initialize FastAPI app
app = FastAPI(
    title="Resume Screening API",
    description="API for screening resumes against job descriptions using NLP and machine learning",
    version="1.0.0"
)

def generate_mapping_id():
    print("Generating a 32 byte mapping id")
    """Generate a secure mapping ID."""
    return secrets.token_urlsafe(32)

app.add_middleware(
    SessionMiddleware,
    secret_key=generate_mapping_id(),
)
# Add CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
resume_parser = ResumeParser()
matching_engine = MatchingEngine()


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google OAuth Credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

ALLOWED_DOMAIN = ["latentview.com"]
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
# GOOGLE_REDIRECT_URI = "https://ctechbot-dev-dot-ctech-growthopscore.el.r.appspot.com/apidev/callback" #demo
GOOGLE_REDIRECT_URI = "http://localhost:5000/callback" #demo


COOKIE_NAME = "nirvana_mapping_id"
COOKIE_SECURE = False  # Set to True for HTTPS
COOKIE_HTTPONLY = True  # Prevent frontend JS access
# COOKIE_DOMAIN = "ctechbot-dev-dot-ctech-growthopscore.el.r.appspot.com"

COOKIE_DOMAIN = "localhost" #demo


oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
    authorize_params={'access_type': 'offline'},
    redirect_uri=GOOGLE_REDIRECT_URI
)

def get_resume_parser():
    """Dependency injection for resume parser"""
    return resume_parser

def get_matching_engine():
    """Dependency injection for matching engine"""
    return matching_engine


@app.get('/auth/google')
async def auth_google(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    print(f"Redirecting to Google with redirect_uri: {redirect_uri}")
    # return oauth.google.authorize_redirect(redirect_uri=redirect_uri, prompt="select_account", access_type="offline")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/callback')
async def callback(request: Request):
    print("Callback request args:")  # Debugging

    try:
        token = await oauth.google.authorize_access_token(request)
        # print("Token received:", token)  # Debugging
        id_token = token.get('id_token')
        # print("ID Token : ", id_token)
        user_info = token.get("userinfo")
        # print("User Info : ", user_info)
        expires_at = token.get('expires_at')
        # print("Expires At : ", expires_at)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch user info"
            )
            
        if user_info.get('hd') not in ALLOWED_DOMAIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access restricted to specific domain users"
            )
        
        user_id = user_info.get("email")
        print("User ID:", user_id)  # Debugging
        request.session['user_id'] = user_id  # Store in session
        print(request.session)
        # return jsonify({"message": "Login successful", "user_id": user_id})
        # return redirect("https://ctech-growthopscore.el.r.appspot.com")
        # Create a response object
        # Create a session mapping ID
        # Create a session mapping ID
        mapping_id = generate_mapping_id()
        # Store the mapping ID and user email in Flask session
        request.session[mapping_id] = id_token
        request.session['user_info'] = user_info
        request.session["name"] = user_info['name']
        request.session["email"] = user_info['email']
        request.session['expires_at'] = expires_at
        # response = make_response(redirect("https://ctechbot-dev-dot-ctech-growthopscore.el.r.appspot.com"))        
        # response = make_response(redirect("http://localhost:4200"))  
        response = RedirectResponse(url="http://localhost:4200")
      

        # Set a secure HTTP-only cookie (expires in 1 day)
        response.set_cookie(
            COOKIE_NAME,
            mapping_id,
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            domain=COOKIE_DOMAIN            
        )    
        print("Setting cookie:", response.headers.get("Set-Cookie"))

        return response

    except Exception as e:
        print(f"Error during Google OAuth callback: {e}")
        return "Authentication failed!", 401


@app.get('/user')
async def user(request: Request):
    print("User End point : Hitting User end point to fetch the user details stored in the session")
    user_info = request.session.get("user_info")
    
    if user_info:
        print("User End point : Session seems active")
        keys_to_filter = ['email', 'email_verified', 'family_name', 'given_name', 'hd', 'name', 'picture', 'sub']
        user_info_ui = {key: user_info.get(key) for key in keys_to_filter if key in user_info}
        return JSONResponse(user_info_ui)
    
    print("User End point : Session seems inactive, redirecting to the Signin page")
    response = RedirectResponse(
        url="http://localhost:4200/signin", 
        status_code=status.HTTP_401_UNAUTHORIZED
    )
    response.delete_cookie(
        COOKIE_NAME,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN
    )
    return response
    
@app.get("/signout")
async def logout(request: Request):
    print("Signout Endpoint : Clearing the session, redirecting to the SignIn page and clearing both session cookie and bnc mapping id cookie")
    request.session.clear()
    response = RedirectResponse(
        url="http://localhost:4200/signin",
        status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(
        COOKIE_NAME,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN
    )
    return response

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Resume Screening API",
        "version": "1.0.0",
        "endpoints": {
            "screen_resume": "/screen_resume",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Resume Screening API"}

@app.post("/screen_resume", response_model=ScreeningResponse)
async def screen_resume(
    resume_file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    jd_file: UploadFile = File(..., description="Job description file (PDF, DOCX, or TXT)"),
    # jd_text: Optional[str] = Form(None, description="Job description as text"),
    parser: ResumeParser = Depends(get_resume_parser),
    engine: MatchingEngine = Depends(get_matching_engine)
):
    """
    Screen a resume against a job description and return match scores
    
    Args:
        resume_file: Resume file upload (required)
        jd_file: Job description file upload (optional if jd_text provided)
        jd_text: Job description as text (optional if jd_file provided)
        
    Returns:
        ScreeningResponse with overall match percentage and detailed breakdown
    """
    try:
        # Validate inputs
        if not jd_file:
        # and not jd_text:
            raise HTTPException(
                status_code=400, 
                detail="jd_file must be provided"
            )
        
        # Parse resume
        resume_data = parser.parse_resume(resume_file)
        
        # Parse job description
        jd_data = parser.parse_job_description(file=jd_file)
        
        # Calculate match scores
        match_result = engine.calculate_match_score(resume_data, jd_data)
        
        # Determine message based on score
        overall_score = match_result['overall_score']
        if overall_score >= 80:
            message = "Excellent match! This candidate meets most of the job requirements."
        elif overall_score >= 60:
            message = "Good match! This candidate has several relevant qualifications."
        elif overall_score >= 40:
            message = "Fair match! This candidate has some relevant experience but may need additional training."
        elif overall_score >= 20:
            message = "Limited match! This candidate has minimal relevant qualifications."
        else:
            message = "Poor match! This candidate does not meet most of the job requirements."
        
        return ScreeningResponse(
            overall_match_percentage=overall_score,
            breakdown=match_result['breakdown'],
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing the request: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True,
        log_level="info"
    )