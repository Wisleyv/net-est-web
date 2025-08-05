# NET-EST System Architecture

This document describes the architecture, design decisions, and technical foundations of the NET-EST system for analyzing intralingual translation and text simplification strategies.

## Architectural Principles

1. **Discourse-First Analysis**: The system analyzes text at the paragraph level (rather than sentence level), reflecting the nature of text simplification.

2. **Human-in-the-Loop Design**: The system serves as an assistant to human experts, who maintain control over analysis and validation.

3. **Modular Architecture**: Components are designed to be independent and interchangeable, enabling easier maintenance and future upgrades.

4. **Feedback-Driven Evolution**: Manual corrections by users are captured as training data to improve the system over time.

5. **Transparency**: The system explains classification decisions by identifying the features that influenced the result.

## System Components

The NET-EST system consists of the following primary components:

### 1. Foundation Layer

The core infrastructure that supports all other modules, including:
- Project structure (backend/frontend)
- Configuration management
- API framework
- Authentication
- Logging
- Testing framework

### 2. Backend Components

#### 2.1 Text Input Module
- Handles direct text entry and file uploads
- Supports multiple file formats (.txt, .md, .docx, .pdf)
- Validates input and enforces size limits
- Converts all inputs to standardized text format

#### 2.2 Semantic Alignment
- Segments text into paragraphs
- Computes semantic similarity between source and target paragraphs
- Creates alignment pairs based on similarity scores
- Identifies unaligned paragraphs

#### 2.3 Feature Extraction & Classification
- Analyzes aligned paragraph pairs
- Extracts linguistic features (lexical, syntactic, discourse)
- Applies rule-based classification to identify simplification strategies
- Tags text with corresponding strategy markers

#### 2.4 Analytics
- Captures usage patterns
- Generates statistics on simplification strategies
- Provides performance metrics

### 3. Frontend Components

#### 3.1 User Interface
- Responsive, accessible design
- Input interfaces (text entry, file upload)
- Results visualization
- Interactive tag editing

#### 3.2 State Management
- Global state (Zustand)
- Server state (React Query)
- Component state (React hooks)

## Hybrid Analysis Approach

The system uses a hybrid approach combining:

1. **Neural Language Models**: For semantic similarity calculation (using SentenceTransformers with BERTimbau)
2. **Rule-Based Heuristics**: For classification of simplification strategies
3. **Statistical Analysis**: For feature extraction and quantitative measures

This hybrid approach balances performance with accuracy and allows for incremental improvements to each component.

## Data Flow

1. User submits source (original) and target (simplified) texts
2. System preprocesses and validates both texts
3. Semantic alignment identifies paragraph correspondences
4. Feature extraction analyzes aligned pairs
5. Classification engine applies tags based on detected strategies
6. User interface displays results with interactive editing capabilities
7. User feedback is captured for future improvements

## Deployment Architecture

The system is designed for deployment in the following environments:

### Development
- Local development environment
- Docker containers for consistent development experience
- Hot reloading for efficient development

### Testing & Staging
- Automated testing via GitHub Actions
- Integration testing in isolated environments
- Performance testing to ensure response time requirements

### Production
- Hugging Face Spaces (backend)
- Vercel (frontend)
- Connected via secure API endpoints

## Technical Stack

### Backend
- Python 3.11+
- FastAPI framework
- SentenceTransformers (BERTimbau)
- Pydantic for data validation
- pytest for testing

### Frontend
- React 18+
- Vite for build tooling
- Zustand for state management
- React Query for API integration
- CSS Modules for styling

## Future Architectural Considerations

1. **Machine Learning Classification**: Replacing rule-based classification with ML models trained on user feedback
2. **Scalability Improvements**: Optimizing for larger text processing
3. **Database Integration**: Adding persistent storage for user feedback and analysis results
4. **Advanced Visualization**: Enhanced UI for displaying complex relationships between texts

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
