# Resume Screening API

## Overview

This is a FastAPI-based resume screening system that analyzes resumes against job descriptions using NLP and machine learning techniques. The API calculates percentage match scores based on skills, experience, education, and semantic similarity between documents. It supports multiple file formats (PDF, DOCX, text) and provides detailed scoring breakdowns to help with recruitment decisions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### API Framework
- **FastAPI**: Chosen for its automatic API documentation, type validation with Pydantic, and high performance
- **CORS Middleware**: Configured to allow cross-origin requests for frontend integration
- **Dependency Injection**: Used for managing ResumeParser and MatchingEngine instances

### Document Processing Pipeline
- **Multi-format Support**: Handles PDF (PyMuPDF), DOCX (python-docx), and plain text files
- **Magic Library**: Used for MIME type detection with graceful fallback to file extensions
- **Text Extraction**: Modular approach with format-specific parsers

### NLP and Matching Engine
- **spaCy Integration**: For text processing and NLP tasks with fallback handling for missing models
- **TF-IDF Vectorization**: Uses scikit-learn for semantic similarity calculations
- **Weighted Scoring System**: 
  - Skills matching: 40%
  - Experience matching: 30%
  - Education matching: 20%
  - Semantic similarity: 10%

### Data Models
- **Pydantic Models**: Strict type validation for all API inputs and outputs
- **Structured Data Extraction**: Separate models for resume data, job description data, and scoring responses

### Error Handling
- **Graceful Degradation**: Fallback mechanisms for missing dependencies (spaCy models, magic library)
- **File Type Validation**: Multiple validation layers for uploaded files
- **HTTP Exception Handling**: Proper error responses for invalid inputs

## External Dependencies

### Core Framework
- **FastAPI**: Web framework for API development
- **Uvicorn**: ASGI server for running the FastAPI application

### Document Processing
- **PyMuPDF (fitz)**: PDF text extraction and processing
- **python-docx**: Microsoft Word document parsing
- **python-magic**: MIME type detection for uploaded files

### NLP and Machine Learning
- **spaCy**: Natural language processing and text analysis
- **scikit-learn**: TF-IDF vectorization and cosine similarity calculations
- **NumPy**: Numerical computations for scoring algorithms

### Utilities
- **python-multipart**: Form data and file upload handling
- **Pydantic**: Data validation and serialization

### Development Dependencies
- Standard Python libraries for text processing (re, io) and type hints (typing)