import re
import io
import spacy
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
from docx import Document
from models import ResumeData, JobDescriptionData

# Try to import magic with fallback
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


class ResumeParser:
    def __init__(self):
        self.nlp = None
        self._initialize_spacy()
    
    def _initialize_spacy(self):
        """Initialize spaCy model with fallback handling"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Try to download the model if it's not available
            try:
                import spacy
                import spacy.cli
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                # If all fails, create a basic nlp pipeline
                import spacy
                self.nlp = spacy.blank("en")

    def parse_resume(self, file: UploadFile) -> ResumeData:
        """Parse resume file and extract key information"""
        try:
            content = file.file.read()
            
            # Determine file type using magic if available, otherwise use extension
            if HAS_MAGIC and magic:
                file_type = magic.from_buffer(content, mime=True)
                is_pdf = 'pdf' in file_type
                is_word = 'word' in file_type or 'document' in file_type
                is_text = 'text' in file_type
            else:
                # Fallback to extension-based detection
                filename_lower = (file.filename or "").lower()
                is_pdf = filename_lower.endswith('.pdf')
                is_word = filename_lower.endswith('.docx')  # Only support .docx, not .doc
                is_text = filename_lower.endswith('.txt')
            
            # Also check file extension as backup
            if file.filename:
                filename_lower = file.filename.lower()
                if filename_lower.endswith('.pdf'):
                    is_pdf = True
                elif filename_lower.endswith('.docx'):
                    is_word = True
                elif filename_lower.endswith('.txt'):
                    is_text = True
            
            if is_pdf:
                text = self._extract_text_from_pdf(content)
            elif is_word:
                text = self._extract_text_from_docx(content)
            elif is_text:
                text = content.decode('utf-8')
            else:
                supported_types = "PDF (.pdf), Word Documents (.docx), or Text files (.txt)"
                raise HTTPException(status_code=400, detail=f"Unsupported file type. Please upload {supported_types}")
            
            cleaned_text = self._preprocess_text(text)
            
            skills = self._extract_skills(cleaned_text)
            experience_years = self._extract_experience_years(cleaned_text)
            education = self._extract_education(cleaned_text)
            
            return ResumeData(
                skills=skills,
                experience_years=experience_years,
                education=education,
                full_text=cleaned_text
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

    def parse_job_description(self, file: UploadFile) -> JobDescriptionData:
        """Parse job description from file or text"""
        try:
            if file:
                # jd_text = text
                content = file.file.read()
            # elif file:
            #     content = file.file.read()
                
                # Use same file type detection as resume parsing
                if HAS_MAGIC and magic:
                    file_type = magic.from_buffer(content, mime=True)
                    is_pdf = 'pdf' in file_type
                    is_word = 'word' in file_type or 'document' in file_type
                    is_text = 'text' in file_type
                else:
                    filename_lower = (file.filename or "").lower()
                    is_pdf = filename_lower.endswith('.pdf')
                    is_word = filename_lower.endswith('.docx')
                    is_text = filename_lower.endswith('.txt')
                
                # Also check file extension as backup
                if file.filename:
                    filename_lower = file.filename.lower()
                    if filename_lower.endswith('.pdf'):
                        is_pdf = True
                    elif filename_lower.endswith('.docx'):
                        is_word = True
                    elif filename_lower.endswith('.txt'):
                        is_text = True
                
                if is_pdf:
                    jd_text = self._extract_text_from_pdf(content)
                elif is_word:
                    jd_text = self._extract_text_from_docx(content)
                elif is_text:
                    jd_text = content.decode('utf-8')
                else:
                    supported_types = "PDF (.pdf), Word Documents (.docx), or Text files (.txt)"
                    raise HTTPException(status_code=400, detail=f"Unsupported file type. Please upload {supported_types}")
            else:
                raise HTTPException(status_code=400, detail="Either file or text must be provided")
            
            cleaned_text = self._preprocess_text(jd_text)
            
            required_skills = self._extract_skills(cleaned_text)
            required_experience_years = self._extract_required_experience_years(cleaned_text)
            education_requirements = self._extract_education_requirements(cleaned_text)
            
            return JobDescriptionData(
                required_skills=required_skills,
                required_experience_years=required_experience_years,
                education_requirements=education_requirements,
                full_text=cleaned_text
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file"""
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()  # type: ignore
        doc.close()
        return text

    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file"""
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\(\)\-\+\#]', ' ', text)
        
        return text.strip()

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using NLP and pattern matching"""
        doc = self.nlp(text)
        
        # Common technical skills patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala)\b',
            r'\b(?:react|angular|vue|node\.?js|express|django|flask|spring|laravel)\b',
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|terraform)\b',
            r'\b(?:machine learning|artificial intelligence|data science|deep learning)\b',
            r'\b(?:agile|scrum|devops|ci\/cd|microservices|rest api|graphql)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind|jquery|typescript)\b',
            r'\b(?:linux|windows|unix|macos|bash|powershell|sql|nosql)\b'
        ]
        
        skills = set()
        
        # Extract using regex patterns
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([match.lower().strip() for match in matches])
        
        # Extract using spaCy NER for organizations and technologies
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'GPE'] and len(ent.text) > 2:
                    # Filter for technology-related entities
                    tech_keywords = ['software', 'framework', 'library', 'database', 'cloud', 'api']
                    context = text[max(0, ent.start_char-50):ent.end_char+50].lower()
                    if any(keyword in context for keyword in tech_keywords):
                        skills.add(ent.text.lower().strip())
        
        # Extract skills from skills section
        skills_section_match = re.search(r'(?:skills?|technical skills?|core competencies):?\s*([^\n]*(?:\n[^\n]*)*?)(?:\n\s*\n|\n[A-Z]|\Z)', text, re.IGNORECASE)
        if skills_section_match:
            skills_text = skills_section_match.group(1)
            # Split by common separators
            skill_items = re.split(r'[,;|\n•·\-\*]', skills_text)
            for item in skill_items:
                item = item.strip()
                if len(item) > 2 and len(item) < 30:  # Reasonable skill length
                    skills.add(item.lower())
        
        return list(skills)

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from resume"""
        # Pattern to match experience years
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?field',
            r'over\s*(\d+)\s*years?',
            r'more than\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches if match.isdigit()])
        
        # Return the maximum years found
        return max(years) if years else None

    def _extract_required_experience_years(self, text: str) -> Optional[int]:
        """Extract required years of experience from job description"""
        patterns = [
            r'(?:minimum|at least|requires?)\s*(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience\s*(?:required|needed|preferred)',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry|role)',
            r'must have\s*(\d+)\+?\s*years?',
            r'(\d+)\+\s*years?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches if match.isdigit()])
        
        return max(years) if years else None

    def _extract_education(self, text: str) -> List[str]:
        """Extract education information from resume"""
        education = []
        
        # Extract education section
        education_section_match = re.search(r'(?:education|academic background|qualifications):?\s*([^\n]*(?:\n[^\n]*)*?)(?:\n\s*\n|\n[A-Z]|\Z)', text, re.IGNORECASE)
        if education_section_match:
            education_text = education_section_match.group(1)
            
            # Extract degree patterns
            degree_patterns = [
                r'\b(?:bachelor|master|phd|doctorate|associate|diploma|certificate|b\.?s\.?|m\.?s\.?|m\.?a\.?|b\.?a\.?|m\.?b\.?a\.?|ph\.?d\.?)\b[^.\n]*',
                r'\b(?:degree|certification|certificate)\s+in\s+[^.\n]*'
            ]
            
            for pattern in degree_patterns:
                matches = re.findall(pattern, education_text, re.IGNORECASE)
                education.extend([match.strip() for match in matches])
        
        # Use spaCy to extract educational institutions
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG'] and any(keyword in ent.text.lower() for keyword in ['university', 'college', 'institute', 'school']):
                    education.append(ent.text.strip())
        
        return list(set(education))

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements from job description"""
        education_requirements = []
        
        # Extract education-related text
        education_patterns = [
            r'(?:education|qualifications|requirements)[:\s]*([^\n]*(?:\n[^\n]*)*?)(?:\n\s*\n|\n[A-Z]|\Z)',
            r'(?:bachelor|master|phd|doctorate|degree|diploma|certificate)[^.\n]*',
            r'(?:required|preferred)\s*(?:education|qualification)[^.\n]*'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 0:
                    education_requirements.append(match.strip())
        
        return list(set(education_requirements))