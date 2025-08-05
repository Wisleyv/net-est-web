import os
import unittest

from fpdf import FPDF

from app import app, db
from app.models import User, Post

# Configure test PDF generation
class PDFTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the test client and database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

        # Create a test user and post
        self.user = User(username='testuser', email='testuser@example.com')
        db.session.add(self.user)
        db.session.commit()
        self.post = Post(title='Test Post', content='This is a test post.', author=self.user)
        db.session.add(self.post)
        db.session.commit()

    def tearDown(self):
        # Clean up the database
        db.session.remove()
        db.drop_all()

    def test_generate_pdf(self):
        # Test PDF generation
        response = self.app.get('/generate_pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
        # Check if the PDF contains the test post content
        self.assertIn(b'Test Post', response.data)
        self.assertIn(b'This is a test post.', response.data)

if __name__ == '__main__':
    unittest.main()

"""
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
"""