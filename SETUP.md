# NET-EST Environment Setup Guide

## Quick Setup Summary

The NET-EST system now includes a **Hybrid ML Strategy Detection** implementation with academic-grade accuracy for text simplification analysis.

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.11+ (recommended 3.11)
- **Node.js**: 18+ for frontend development
- **Memory**: 4GB+ RAM (for ML models)
- **Storage**: 2GB+ free space

### Required Dependencies

#### Core ML Libraries
```bash
# Sentence transformers for semantic analysis
pip install sentence-transformers==2.7.0

# spaCy for Portuguese linguistic analysis
pip install spacy==3.7.4
python -m spacy download pt_core_news_sm

# PyTorch (automatically installed with sentence-transformers)
pip install torch>=2.0.0
```

#### Backend Dependencies
```bash
# Install all backend requirements
pip install -r backend/requirements.txt
```

#### Frontend Dependencies
```bash
# Install frontend packages
cd frontend
npm install
```

## 🚀 Installation Steps

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Portuguese spaCy model
python -m spacy download pt_core_news_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('pt_core_news_sm'); print('✅ spaCy OK')"
python -c "from sentence_transformers import SentenceTransformer; print('✅ SentenceTransformers OK')"
```

### 2. Start Backend Server
```bash
# From backend directory
python start_server.py
# Server will be available at http://localhost:8000
```

### 3. Frontend Setup (Optional)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend will be available at http://localhost:3000
```

## 🧪 Testing the Installation

### Quick API Test
```bash
curl -X GET "http://localhost:8000/api/v1/health"
# Expected response: {"status": "healthy", "timestamp": "..."}
```

### Strategy Detection Test
```python
import requests

# Test strategy detection
response = requests.post("http://localhost:8000/api/v1/semantic-alignment", json={
    "source_text": "Python é uma linguagem de programação versátil e fácil de aprender.",
    "target_text": "Python é uma linguagem simples e fácil de aprender."
})

print(response.json())
# Should return detected strategies like ["SL+"]
```

## 🔍 Current Implementation Features

### ✅ Implemented (Step 1-3)
- **Lightweight ML Model**: paraphrase-multilingual-MiniLM-L12-v2 (118MB)
- **Portuguese Language Support**: spaCy pt_core_news_sm
- **Length-Aware Thresholds**: Adaptive confidence for 65%+ text reductions
- **Academic Rigor**: Evidence-based strategy classification
- **Performance Optimized**: 2-8 seconds (vs previous timeouts)
- **Strategy Detection**: SL+, RP+, RF+, MOD+, OM-, PRO+

### 🎯 Accuracy Metrics
- **Heavy Reduction (65%+)**: Detects RF+ (Global Rewriting)
- **Moderate Reduction (30-65%)**: Detects SL+ (Lexical) + RP+ (Syntactic)
- **Light Editing (<30%)**: Detects SL+ (Lexical Simplification)
- **Semantic Preservation**: Minimum 65-80% similarity (adaptive)

## 🐛 Troubleshooting

### Common Issues

#### "spaCy model not found"
```bash
python -m spacy download pt_core_news_sm
```

#### "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers==2.7.0
```

#### "CUDA out of memory" (if using GPU)
```python
# Force CPU usage
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
```

#### Performance Issues
- Ensure you have 4GB+ RAM available
- Texts are automatically truncated to 50k characters
- Use shorter texts for faster processing

## 📁 Project Structure

```
net/
├── backend/                 # Python/FastAPI backend
│   ├── src/
│   │   ├── services/
│   │   │   ├── strategy_detector.py     # Core ML detection
│   │   │   └── text_input_service.py    # Text processing
│   │   ├── api/             # API endpoints
│   │   └── models/          # Data models
│   ├── requirements.txt     # Python dependencies
│   └── start_server.py      # Server startup
├── frontend/                # React frontend
└── docs/                   # Documentation
```

## 🔄 Next Development Steps

1. **Interface Enhancement**: Advanced analysis visualization
2. **Human Validation**: Expert review integration
3. **Continuous Learning**: Model improvement pipeline
4. **Report Export**: Detailed analysis reports

---

✅ **Environment ready for NET-EST development and testing!**
