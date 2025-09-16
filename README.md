# Resume Screening API Documentation

A FastAPI-based system that analyzes resumes against job descriptions using AI and provides detailed match scores.

## 🚀 Getting Started

### Starting the Server

#### Option 1: Using Replit (Recommended)
The server should already be running automatically in Replit. You can see it in the "Webview" tab.

#### Option 2: Manual Start
If you need to start the server manually:

```bash
python main.py
```

The server will start on `http://0.0.0.0:5000`

#### Option 3: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Verifying the Server is Running

1. Check the "Console" tab in Replit for startup messages
2. Visit the API documentation at: `https://your-repl-url.replit.dev/docs`
3. Test the health endpoint: `https://your-repl-url.replit.dev/health`

## 📋 API Endpoints

### GET /
Returns basic API information and available endpoints.

### GET /health
Health check endpoint to verify the API is running.

### POST /screen_resume
Main endpoint for screening resumes against job descriptions.

**Parameters:**
- `resume_file` (required): Resume file (PDF, DOCX, or TXT)
- `jd_file` (optional): Job description file (PDF, DOCX, or TXT) 
- `jd_text` (optional): Job description as plain text

**Note:** Either `jd_file` or `jd_text` must be provided.

**Response:**
```json
{
  "overall_match_percentage": 75.5,
  "breakdown": {
    "skills_score": 80.0,
    "experience_score": 70.0,
    "education_score": 75.0,
    "semantic_score": 78.0
  },
  "message": "Good match! This candidate has several relevant qualifications."
}
```

## 🔧 Frontend Integration Guide

### For JavaScript/React Applications

#### Basic Example with Fetch API

```javascript
async function screenResume(resumeFile, jobDescriptionText) {
  const formData = new FormData();
  formData.append('resume_file', resumeFile);
  formData.append('jd_text', jobDescriptionText);
  
  try {
    const response = await fetch('https://your-repl-url.replit.dev/screen_resume', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const result = await response.json();
    console.log('Match Score:', result.overall_match_percentage);
    console.log('Breakdown:', result.breakdown);
    console.log('Message:', result.message);
    
    return result;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage example
const fileInput = document.getElementById('resumeFile');
const jobDescription = "Looking for a Python developer with 3+ years experience...";

screenResume(fileInput.files[0], jobDescription)
  .then(result => {
    // Display results to user
    document.getElementById('matchScore').textContent = result.overall_match_percentage + '%';
  })
  .catch(error => {
    // Handle errors
    alert('Error processing resume: ' + error.message);
  });
```

#### React Component Example

```jsx
import React, { useState } from 'react';

function ResumeScreener() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!resumeFile || !jobDescription) {
      alert('Please provide both resume file and job description');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    formData.append('jd_text', jobDescription);

    try {
      const response = await fetch('https://your-repl-url.replit.dev/screen_resume', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      setResults(result);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Resume File:</label>
          <input 
            type="file" 
            accept=".pdf,.docx,.txt"
            onChange={(e) => setResumeFile(e.target.files[0])}
          />
        </div>
        
        <div>
          <label>Job Description:</label>
          <textarea 
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={10}
            cols={50}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Screen Resume'}
        </button>
      </form>

      {results && (
        <div>
          <h3>Results</h3>
          <p><strong>Overall Match:</strong> {results.overall_match_percentage}%</p>
          <p><strong>Skills:</strong> {results.breakdown.skills_score}%</p>
          <p><strong>Experience:</strong> {results.breakdown.experience_score}%</p>
          <p><strong>Education:</strong> {results.breakdown.education_score}%</p>
          <p><strong>Semantic:</strong> {results.breakdown.semantic_score}%</p>
          <p><strong>Assessment:</strong> {results.message}</p>
        </div>
      )}
    </div>
  );
}

export default ResumeScreener;
```

### For Python Applications

```python
import requests

def screen_resume(resume_file_path, job_description_text, api_url):
    """
    Screen a resume against a job description
    """
    with open(resume_file_path, 'rb') as resume_file:
        files = {'resume_file': resume_file}
        data = {'jd_text': job_description_text}
        
        response = requests.post(f"{api_url}/screen_resume", files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.text}")

# Usage
api_url = "https://your-repl-url.replit.dev"
result = screen_resume("candidate_resume.pdf", "Job description text...", api_url)
print(f"Match Score: {result['overall_match_percentage']}%")
```

### For cURL/Testing

```bash
# Test with file upload
curl -X POST "https://your-repl-url.replit.dev/screen_resume" \
  -F "resume_file=@path/to/resume.pdf" \
  -F "jd_text=Looking for a Python developer with 3+ years experience in FastAPI..."

# Test health endpoint
curl "https://your-repl-url.replit.dev/health"
```

## 🔒 Important Notes for Frontend Developers

### CORS Configuration
The API is configured to accept requests from any origin (`*`) for development. For production, you should configure specific allowed origins.

### File Size Limits
- Recommended maximum file size: 10MB
- Supported formats: PDF, DOCX, TXT

### Error Handling
Always implement proper error handling in your frontend:

```javascript
// Example error handling
try {
  const response = await fetch('/screen_resume', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Unknown error occurred');
  }
  
  const result = await response.json();
  // Handle success
} catch (error) {
  // Handle different types of errors
  if (error.message.includes('Unsupported file type')) {
    alert('Please upload a PDF, DOCX, or TXT file');
  } else if (error.message.includes('file or text must be provided')) {
    alert('Please provide either a job description file or text');
  } else {
    alert('An error occurred: ' + error.message);
  }
}
```

### Response Interpretation

The API returns scores from 0-100:
- **80-100%**: Excellent match
- **60-79%**: Good match  
- **40-59%**: Fair match
- **20-39%**: Limited match
- **0-19%**: Poor match

Use these ranges to provide meaningful feedback to users in your interface.

## 📚 Interactive API Documentation

FastAPI automatically generates interactive documentation available at:
`https://your-repl-url.replit.dev/docs`

This provides a web interface where you can:
- See all available endpoints
- Test API calls directly
- View request/response schemas
- Download OpenAPI specifications

## 🐛 Troubleshooting

### Common Issues

1. **Server not starting**: Check the Console tab for error messages
2. **File upload fails**: Ensure file is under size limit and correct format
3. **CORS errors**: The API should handle cross-origin requests automatically
4. **Timeout errors**: Large files may take longer to process

### Getting Help

If you encounter issues:
1. Check the server logs in the Console tab
2. Test endpoints using the interactive documentation at `/docs`
3. Verify your file formats are supported (PDF, DOCX, TXT only)