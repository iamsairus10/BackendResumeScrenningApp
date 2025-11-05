# Resume Screening API

A FastAPI-based application that leverages AI and NLP to analyze resumes against job descriptions, providing detailed match scores and insights for recruitment processes.

## Features

- 📄 Multi-format support (PDF, DOCX, TXT)
- 🔍 Advanced NLP-based analysis
- 🔐 Google OAuth authentication
- 📊 Detailed match scoring
- 🚀 High-performance API
- 📱 CORS support for frontend integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iamsairus10/BackendResumeScrenningApp.git
cd BackendResumeScrenningApp
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Set up Google OAuth credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Google OAuth2 API
   - Create OAuth 2.0 credentials (OAuth client ID)
   - Set the authorized redirect URI to `http://localhost:5000/callback`
   - Add your credentials to the `.env` file:
     ```
     GOOGLE_CLIENT_ID=your_client_id_here
     GOOGLE_CLIENT_SECRET=your_client_secret_here
     SECRET_KEY=your_secure_secret_key_here
     ```

## Running the Server

1. Start the server:
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

2. Access the application:
   - API documentation: `http://localhost:5000/docs`
   - Alternative API docs: `http://localhost:5000/redoc`
   - Health check: `http://localhost:5000/health`

## API Endpoints

### Authentication Endpoints
- `GET /auth/google` - Initiate Google OAuth login
- `GET /callback` - OAuth callback handler
- `GET /user` - Get current user information
- `GET /signout` - Sign out the current user

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint
- `POST /screen_resume` - Resume screening endpoint
  - Parameters:
    - `resume_file` (required): Resume file (PDF, DOCX, or TXT)
    - `jd_file` (required): Job description file (PDF, DOCX, or TXT)

## API Response Format

### Successful Response
```json
{
    "overall_match_percentage": 75.5,
    "breakdown": {
        "skills_match": 80.0,
        "experience_match": 70.0,
        "education_match": 85.0,
        "semantic_similarity": 67.0
    },
    "message": "Good match! This candidate has several relevant qualifications."
}
```

## Security

- Google OAuth 2.0 authentication
- Domain-restricted access (configurable)
- Secure session management
- HTTP-only cookies
- JWT token-based API protection

## Technical Stack

- **Framework**: FastAPI
- **Authentication**: Google OAuth 2.0, JWT
- **Document Processing**: PyMuPDF, python-docx
- **NLP**: spaCy, scikit-learn
- **File Handling**: python-magic, python-multipart

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI framework
- spaCy NLP library
- Google OAuth 2.0
- All other open-source contributors
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