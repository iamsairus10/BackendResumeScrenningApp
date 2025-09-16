from typing import Dict, List, Set, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import ResumeData, JobDescriptionData, MatchScoreBreakdown


class MatchingEngine:
    """Engine for calculating match scores between resumes and job descriptions"""
    
    def __init__(self):
        self.weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'semantic': 0.1
        }
    
    def calculate_match_score(self, resume_data: ResumeData, jd_data: JobDescriptionData) -> Dict:
        """
        Calculate comprehensive match score between resume and job description
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
            
        Returns:
            Dictionary containing overall score and breakdown
        """
        try:
            # Calculate individual scores
            skills_score = self._calculate_skills_score(resume_data.skills, jd_data.required_skills)
            experience_score = self._calculate_experience_score(
                resume_data.experience_years, 
                jd_data.required_experience_years
            )
            education_score = self._calculate_education_score(
                resume_data.education, 
                jd_data.education_requirements
            )
            semantic_score = self._calculate_semantic_score(
                resume_data.full_text, 
                jd_data.full_text
            )
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * self.weights['skills'] +
                experience_score * self.weights['experience'] +
                education_score * self.weights['education'] +
                semantic_score * self.weights['semantic']
            )
            
            breakdown = MatchScoreBreakdown(
                skills_score=round(skills_score * 100, 2),
                experience_score=round(experience_score * 100, 2),
                education_score=round(education_score * 100, 2),
                semantic_score=round(semantic_score * 100, 2)
            )
            
            return {
                'overall_score': round(overall_score * 100, 2),
                'breakdown': breakdown
            }
            
        except Exception as e:
            # Return default scores if calculation fails
            breakdown = MatchScoreBreakdown(
                skills_score=0.0,
                experience_score=0.0,
                education_score=0.0,
                semantic_score=0.0
            )
            return {
                'overall_score': 0.0,
                'breakdown': breakdown
            }
    
    def _calculate_skills_score(self, resume_skills: List[str], required_skills: List[str]) -> float:
        """
        Calculate Jaccard similarity score for skills matching
        
        Args:
            resume_skills: List of skills from resume
            required_skills: List of required skills from job description
            
        Returns:
            Jaccard similarity score (0.0 to 1.0)
        """
        if not resume_skills or not required_skills:
            return 0.0
        
        # Convert to lowercase sets for case-insensitive comparison
        resume_set = set(skill.lower().strip() for skill in resume_skills)
        required_set = set(skill.lower().strip() for skill in required_skills)
        
        # Calculate Jaccard similarity
        intersection = len(resume_set.intersection(required_set))
        union = len(resume_set.union(required_set))
        
        if union == 0:
            return 0.0
        
        jaccard_score = intersection / union
        
        # Also calculate overlap ratio (how many required skills are present)
        overlap_ratio = intersection / len(required_set) if required_set else 0.0
        
        # Use weighted average of Jaccard and overlap ratio
        final_score = (jaccard_score * 0.3) + (overlap_ratio * 0.7)
        
        return min(final_score, 1.0)
    
    def _calculate_experience_score(self, resume_years: Optional[int], required_years: Optional[int]) -> float:
        """
        Calculate experience score based on years comparison
        
        Args:
            resume_years: Years of experience from resume
            required_years: Required years from job description
            
        Returns:
            Experience score (0.0 to 1.0)
        """
        if required_years is None:
            return 0.8  # Default score when no requirement specified
        
        if resume_years is None:
            return 0.0  # No experience information found
        
        if resume_years >= required_years:
            return 1.0  # Meets or exceeds requirement
        
        # Proportional scoring for less experience
        ratio = resume_years / required_years
        
        # Apply a more forgiving curve for close matches
        if ratio >= 0.8:
            return 0.9
        elif ratio >= 0.6:
            return 0.7
        elif ratio >= 0.4:
            return 0.5
        elif ratio >= 0.2:
            return 0.3
        else:
            return 0.1
    
    def _calculate_education_score(self, resume_education: List[str], required_education: List[str]) -> float:
        """
        Calculate education score based on keyword matching
        
        Args:
            resume_education: Education information from resume
            required_education: Education requirements from job description
            
        Returns:
            Education score (0.0 to 1.0)
        """
        if not required_education:
            return 0.8  # Default score when no requirement specified
        
        if not resume_education:
            return 0.0  # No education information found
        
        # Convert to lowercase for comparison
        resume_text = ' '.join(resume_education).lower()
        
        # Common education keywords
        education_keywords = {
            'bachelor': ['bachelor', 'b.s', 'b.a', 'bs', 'ba', 'undergraduate'],
            'master': ['master', 'm.s', 'm.a', 'ms', 'ma', 'mba', 'graduate'],
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
            'associate': ['associate', 'associates'],
            'diploma': ['diploma', 'certificate', 'certification'],
            'degree': ['degree']
        }
        
        matches = 0
        total_requirements = 0
        
        for requirement in required_education:
            requirement_lower = requirement.lower()
            total_requirements += 1
            
            # Check for direct keyword matches
            requirement_matched = False
            for edu_type, keywords in education_keywords.items():
                if any(keyword in requirement_lower for keyword in keywords):
                    if any(keyword in resume_text for keyword in keywords):
                        matches += 1
                        requirement_matched = True
                        break
            
            # If no keyword match, check for general text similarity
            if not requirement_matched:
                requirement_words = set(requirement_lower.split())
                resume_words = set(resume_text.split())
                
                # Calculate word overlap
                word_overlap = len(requirement_words.intersection(resume_words))
                overlap_ratio = word_overlap / len(requirement_words) if requirement_words else 0
                
                if overlap_ratio > 0.3:  # At least 30% word overlap
                    matches += 0.5  # Partial match
        
        if total_requirements == 0:
            return 0.8
        
        score = matches / total_requirements
        return min(score, 1.0)
    
    def _calculate_semantic_score(self, resume_text: str, jd_text: str) -> float:
        """
        Calculate semantic similarity using TF-IDF and cosine similarity
        
        Args:
            resume_text: Full resume text
            jd_text: Full job description text
            
        Returns:
            Semantic similarity score (0.0 to 1.0)
        """
        if not resume_text or not jd_text:
            return 0.0
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9
            )
            
            # Fit and transform texts
            documents = [resume_text, jd_text]
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = similarity_matrix[0][0]
            
            # Ensure score is in valid range
            return max(0.0, min(1.0, similarity_score))
            
        except Exception as e:
            # Return default score if calculation fails
            return 0.0