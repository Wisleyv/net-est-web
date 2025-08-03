# Componente de Autoria para Frontend

## Arquivo: src/components/AboutCredits.jsx

```jsx
import React, { useState } from 'react';
import './AboutCredits.css';

const AboutCredits = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleModal = () => setIsOpen(!isOpen);

  return (
    <>
      {/* Link discreto para abrir modal */}
      <button 
        className="credits-link"
        onClick={toggleModal}
        aria-label="Sobre o projeto e créditos"
      >
        ℹ️ Sobre
      </button>

      {/* Modal com informações */}
      {isOpen && (
        <div className="credits-modal-overlay" onClick={toggleModal}>
          <div className="credits-modal" onClick={(e) => e.stopPropagation()}>
            <div className="credits-header">
              <h2>NET-EST</h2>
              <p className="credits-subtitle">
                Sistema de Análise de Tradução Intralinguística
              </p>
              <button 
                className="credits-close"
                onClick={toggleModal}
                aria-label="Fechar"
              >
                ×
              </button>
            </div>

            <div className="credits-content">
              <section className="credits-section">
                <h3>Equipe de Desenvolvimento</h3>
                
                <div className="credit-item">
                  <h4>Coordenação Acadêmica</h4>
                  <p><strong>Profa. Dra. Janine Pimentel</strong></p>
                  <p>PIPGLA/UFRJ e Politécnico de Leiria (Portugal)</p>
                  <p>Coordenadora do Núcleo de Estudos de Tradução</p>
                </div>

                <div className="credit-item">
                  <h4>Desenvolvimento Técnico</h4>
                  <p><strong>Wisley Vilela</strong></p>
                  <p>Doutorando em Estudos da Tradução - PIPGLA/UFRJ</p>
                  <p>Desenvolvedor Principal e Arquiteto de Sistema</p>
                </div>

                <div className="credit-item">
                  <h4>Especialização Linguística</h4>
                  <p><strong>Luanny Matos de Lima</strong></p>
                  <p>Mestranda PPGLEN/UFRJ</p>
                  <p>Especialista em Análise de Simplificação Textual</p>
                </div>

                <div className="credit-item">
                  <h4>Agentes Técnicos de IA</h4>
                  <p>Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash</p>
                  <p>Mediados por GitHub Copilot</p>
                </div>
              </section>

              <section className="credits-section">
                <h3>Instituições</h3>
                <p><strong>Núcleo de Estudos de Tradução - UFRJ</strong></p>
                <p><strong>Politécnico de Leiria (Portugal)</strong></p>
              </section>

              <section className="credits-section">
                <h3>Tecnologia</h3>
                <p>Sistema desenvolvido com Python, FastAPI, React e modelos de linguagem BERTimbau</p>
                <p><strong>Licença:</strong> MIT License</p>
                <p><strong>Código:</strong> <a href="https://github.com/[repositorio]" target="_blank" rel="noopener noreferrer">GitHub</a></p>
              </section>

              <section className="credits-section">
                <h3>Citação Acadêmica</h3>
                <div className="citation-box">
                  <p>
                    Vilela, W., Pimentel, J., & Lima, L. M. (2025). NET-EST: Sistema de Análise 
                    Computacional para Estratégias de Simplificação em Tradução Intralingual. 
                    Núcleo de Estudos de Tradução, UFRJ.
                  </p>
                </div>
              </section>
            </div>

            <div className="credits-footer">
              <p>Versão 1.0 | Julho 2025</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AboutCredits;
```

## Arquivo: src/components/AboutCredits.css

```css
/* Link discreto no header ou footer */
.credits-link {
  background: none;
  border: none;
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.credits-link:hover {
  background-color: #f0f0f0;
  color: #333;
}

/* Modal overlay */
.credits-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

/* Modal principal */
.credits-modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  max-height: 80vh;
  width: 100%;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
}

/* Header do modal */
.credits-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px 12px 0 0;
  position: relative;
}

.credits-header h2 {
  margin: 0 0 5px 0;
  font-size: 1.8rem;
  font-weight: bold;
}

.credits-subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 0.95rem;
}

.credits-close {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.credits-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Conteúdo do modal */
.credits-content {
  padding: 20px;
}

.credits-section {
  margin-bottom: 25px;
}

.credits-section h3 {
  color: #333;
  font-size: 1.2rem;
  margin-bottom: 15px;
  border-left: 4px solid #667eea;
  padding-left: 12px;
}

.credit-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.credit-item h4 {
  margin: 0 0 8px 0;
  color: #667eea;
  font-size: 1rem;
  font-weight: 600;
}

.credit-item p {
  margin: 4px 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.credit-item p:first-of-type {
  font-weight: 500;
  color: #333;
}

/* Caixa de citação */
.citation-box {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #495057;
}

/* Footer do modal */
.credits-footer {
  background-color: #f8f9fa;
  padding: 15px 20px;
  border-top: 1px solid #e9ecef;
  text-align: center;
  color: #666;
  font-size: 0.85rem;
  border-radius: 0 0 12px 12px;
}

/* Links */
.credits-content a {
  color: #667eea;
  text-decoration: none;
}

.credits-content a:hover {
  text-decoration: underline;
}

/* Responsividade */
@media (max-width: 768px) {
  .credits-modal {
    margin: 10px;
    max-height: 90vh;
  }
  
  .credits-header {
    padding: 15px;
  }
  
  .credits-content {
    padding: 15px;
  }
  
  .credit-item {
    padding: 12px;
  }
}
```

## Uso no App Principal

```jsx
// src/App.jsx
import React from 'react';
import AboutCredits from './components/AboutCredits';

function App() {
  return (
    <div className="app">
      {/* Header com link discreto */}
      <header className="app-header">
        <h1>NET-EST</h1>
        <div className="header-actions">
          <AboutCredits />
        </div>
      </header>

      {/* Resto da aplicação */}
      <main>
        {/* Conteúdo principal */}
      </main>

      {/* Footer alternativo */}
      <footer className="app-footer">
        <p>© 2025 Núcleo de Estudos de Tradução - UFRJ</p>
        <AboutCredits />
      </footer>
    </div>
  );
}

export default App;
```

## Integração Alternativa - Página Estática

Para uma abordagem menos invasiva, você pode criar uma rota `/about` com informações completas:

```jsx
// src/pages/About.jsx
import React from 'react';

const About = () => {
  return (
    <div className="about-page">
      <div className="container">
        <h1>Sobre o NET-EST</h1>
        
        {/* Conteúdo similar ao modal, mas como página completa */}
        
        <nav className="about-nav">
          <a href="/">← Voltar ao Sistema</a>
        </nav>
      </div>
    </div>
  );
};

export default About;
```

## Considerações de UX

1. **Posicionamento:** Link discreto no header ou footer
2. **Acessibilidade:** Componente acessível via teclado
3. **Performance:** Carregamento sob demanda
4. **Mobile:** Responsivo para todos os dispositivos
5. **Não Invasivo:** Não interfere no fluxo principal do usuário
