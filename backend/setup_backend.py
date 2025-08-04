#!/usr/bin/env python3
"""
NET-EST Backend Setup Script
Ensures all dependencies including SpaCy Portuguese model are properly installed
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 NET-EST Backend Setup")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider creating a virtual environment: python -m venv venv")
        print("   And activating it: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
        print()
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install SpaCy Portuguese model
    if not run_command("python -m spacy download pt_core_news_sm", "Installing Portuguese SpaCy model"):
        return False
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    
    try:
        import spacy
        nlp = spacy.load("pt_core_news_sm")
        print("✅ Portuguese SpaCy model verified")
    except Exception as e:
        print(f"❌ SpaCy model verification failed: {e}")
        return False
    
    try:
        from src.services.feature_extraction_service import FeatureExtractionService
        service = FeatureExtractionService()
        if service.nlp is not None:
            print("✅ Feature extraction service verified")
        else:
            print("❌ Feature extraction service initialization failed")
            return False
    except Exception as e:
        print(f"❌ Service verification failed: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("   NET-EST backend is ready for use with full linguistic analysis capabilities")
    print("\n📋 Next steps:")
    print("   1. Start the server: python -m uvicorn src.main:app --reload")
    print("   2. Access API docs: http://localhost:8000/docs")
    print("   3. Test feature extraction: /api/v1/feature-extraction/health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
