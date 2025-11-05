# Resume Screening API Integration Guide

## API Base URL

For local development:
```
http://localhost:5000
```

For production, replace with your deployed API URL:
```
https://your-api-domain.com
```

## Quick Start

### 1. Verify API Status
Test the health endpoint:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
    "status": "healthy",
    "service": "Resume Screening API"
}
```

You should see:
```json
{"status": "healthy", "service": "Resume Screening API"}
```

### 2. Authentication Flow

1. Redirect users to the login endpoint:
```javascript
window.location.href = 'http://localhost:5000/auth/google';
```

2. After successful authentication, users will be redirected to your frontend application with an HTTP-only cookie for session management.

3. Access protected endpoints with the session cookie:
```javascript
// The cookie is automatically included in requests
fetch('http://localhost:5000/screen_resume', {
    method: 'POST',
    credentials: 'include',  // Important for cookies
    body: formData
});
```

### 3. Interactive API Documentation
Access the Swagger UI documentation:
```
http://localhost:5000/docs
```

## Frontend Integration Examples

### Simple HTML Form
```html
<!DOCTYPE html>
<html>
<head>
    <title>Resume Screener</title>
</head>
<body>
    <h1>Resume Screening Tool</h1>
    
    <form id="resumeForm">
        <div>
            <label for="resumeFile">Upload Resume:</label>
            <input type="file" id="resumeFile" accept=".pdf,.docx,.txt" required>
        </div>
        
        <div>
            <label for="jobDescription">Job Description:</label>
            <textarea id="jobDescription" rows="8" cols="50" 
                placeholder="Enter job requirements, skills needed, experience level..." required></textarea>
        </div>
        
        <button type="submit">Screen Resume</button>
    </form>
    
    <div id="results" style="margin-top: 20px;"></div>
    
    <script>
        document.getElementById('resumeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const resumeFile = document.getElementById('resumeFile').files[0];
            const jobDescription = document.getElementById('jobDescription').value;
            
            formData.append('resume_file', resumeFile);
            formData.append('jd_text', jobDescription);
            
            try {
                // Replace with your actual Replit URL
                const response = await fetch('https://your-repl-name--your-username.replit.dev/screen_resume', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                // Display results
                document.getElementById('results').innerHTML = `
                    <h3>Screening Results</h3>
                    <p><strong>Overall Match: ${result.overall_match_percentage}%</strong></p>
                    <p>Skills Score: ${result.breakdown.skills_score}%</p>
                    <p>Experience Score: ${result.breakdown.experience_score}%</p>
                    <p>Education Score: ${result.breakdown.education_score}%</p>
                    <p>Semantic Score: ${result.breakdown.semantic_score}%</p>
                    <p><em>${result.message}</em></p>
                `;
            } catch (error) {
                document.getElementById('results').innerHTML = `
                    <p style="color: red;">Error: ${error.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
```

### React Hook Example
```jsx
import { useState } from 'react';

const useResumeScreener = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Replace with your actual Replit URL
  const API_BASE_URL = 'https://your-repl-name--your-username.replit.dev';
  
  const screenResume = async (resumeFile, jobDescriptionText) => {
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    formData.append('jd_text', jobDescriptionText);
    
    try {
      const response = await fetch(`${API_BASE_URL}/screen_resume`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to screen resume');
      }
      
      const result = await response.json();
      setResults(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { screenResume, loading, results, error };
};

export default useResumeScreener;
```

## 📱 Mobile App Integration

### React Native Example
```javascript
const screenResume = async (resumeUri, jobDescription) => {
  const formData = new FormData();
  
  formData.append('resume_file', {
    uri: resumeUri,
    type: 'application/pdf', // or appropriate mime type
    name: 'resume.pdf'
  });
  
  formData.append('jd_text', jobDescription);
  
  try {
    const response = await fetch('https://your-repl-name--your-username.replit.dev/screen_resume', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return await response.json();
  } catch (error) {
    console.error('Resume screening failed:', error);
    throw error;
  }
};
```

## 🔧 Backend Integration

### Express.js Middleware
```javascript
const multer = require('multer');
const FormData = require('form-data');
const fetch = require('node-fetch');

const upload = multer({ dest: 'uploads/' });

app.post('/api/screen-resume', upload.single('resume'), async (req, res) => {
  try {
    const formData = new FormData();
    formData.append('resume_file', fs.createReadStream(req.file.path));
    formData.append('jd_text', req.body.jobDescription);
    
    const response = await fetch('https://your-repl-name--your-username.replit.dev/screen_resume', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## 🎯 Expected Response Format

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

## 🚨 Error Handling

Common error responses:
```json
// Missing required fields
{
  "detail": "Either jd_file or jd_text must be provided"
}

// Unsupported file type
{
  "detail": "Unsupported file type. Please upload PDF (.pdf), Word Documents (.docx), or Text files (.txt)"
}

// Server error
{
  "detail": "An error occurred while processing the request: [error details]"
}
```

## 📊 Integrating Results into Your UI

### Progress Bar Example
```css
.score-bar {
  width: 100%;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.score-fill {
  height: 20px;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.excellent { background-color: #4CAF50; }
.good { background-color: #8BC34A; }
.fair { background-color: #FFC107; }
.limited { background-color: #FF9800; }
.poor { background-color: #F44336; }
```

```javascript
function displayScore(score) {
  const scoreBar = document.querySelector('.score-fill');
  scoreBar.style.width = score + '%';
  
  if (score >= 80) scoreBar.className = 'score-fill excellent';
  else if (score >= 60) scoreBar.className = 'score-fill good';
  else if (score >= 40) scoreBar.className = 'score-fill fair';
  else if (score >= 20) scoreBar.className = 'score-fill limited';
  else scoreBar.className = 'score-fill poor';
}
```

## 🎉 You're Ready to Go!

1. Replace `your-repl-name--your-username.replit.dev` with your actual Replit URL
2. Test the health endpoint to make sure your API is running
3. Use any of the code examples above to integrate with your frontend
4. Check the interactive docs at `/docs` for detailed API information

Happy coding! 🚀