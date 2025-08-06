import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Select Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Title', 0, 1, 'C')

    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

def create_simple_pdf(output_path):
    # Create instance of FPDF class
    pdf = PDF()
    # Add a page
    pdf.add_page()
    # Set font
    pdf.set_font('Arial', 'B', 16)
    # Add a cell
    pdf.cell(40, 10, 'Hello World!')
    # Output the PDF
    pdf.output(output_path)

if __name__ == "__main__":
    output_path = os.path.join(os.getcwd(), "simple_pdf.pdf")
    create_simple_pdf(output_path)

"""
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
"""