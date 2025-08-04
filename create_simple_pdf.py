#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar PDF simplificado em português para testar análise comparativa
"""

from fpdf import FPDF

class SimplePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Lei de Responsabilidade Fiscal - Versão Simplificada', 0, 1, 'C')
        self.ln(10)

def create_simple_pdf():
    pdf = SimplePDF()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12)
    
    # Título
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Lei que Controla os Gastos Públicos', 0, 1, 'C')
    pdf.ln(5)
    
    # Texto simplificado
    texto_simples = [
        "A Lei de Responsabilidade Fiscal é uma lei importante criada em 2000. Ela ajuda a controlar como o governo gasta o dinheiro público no Brasil.",
        
        "Esta lei tem regras básicas:",
        "• O governo deve planejar seus gastos",
        "• Deve mostrar para a população como gasta",
        "• Não pode gastar mais do que arrecada",
        "• Tem limites para contratar funcionários",
        "• Não pode se endividar demais",
        
        "O objetivo é evitar que o governo gaste mal o dinheiro dos impostos. Para isso funcionar bem, os funcionários públicos precisam ser treinados.",
        
        "A lei protege o dinheiro dos brasileiros e ajuda o país a ter contas organizadas."
    ]
    
    pdf.set_font('Helvetica', '', 11)
    for linha in texto_simples:
        if linha.startswith('•'):
            pdf.cell(10, 6, '', 0, 0)  # Indentação para bullet points
            pdf.cell(0, 6, linha.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
        else:
            pdf.cell(0, 6, linha.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
        pdf.ln(2)
    
    # Salva o PDF
    pdf.output('teste_lei_simplificada.pdf')
    print("PDF simplificado criado: teste_lei_simplificada.pdf")

if __name__ == "__main__":
    create_simple_pdf()
