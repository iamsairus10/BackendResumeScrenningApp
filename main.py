from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from models import ScreeningResponse, MatchScoreBreakdown
from resume_parser import ResumeParser
from matching_engine import MatchingEngine

# Initialize FastAPI app
app = FastAPI(
    title="Resume Screening API",
    description="API for screening resumes against job descriptions using NLP and machine learning",
    version="1.0.0"
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

def get_resume_parser():
    """Dependency injection for resume parser"""
    return resume_parser

def get_matching_engine():
    """Dependency injection for matching engine"""
    return matching_engine

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