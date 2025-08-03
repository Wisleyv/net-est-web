# NET-EST - Sistema de Análise de Tradução Intralinguística

Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual desenvolvido pelo Núcleo de Estudos de Tradução da UFRJ em parceria com o Politécnico de Leiria.

## 🎯 Sobre o Projeto

O NET-EST é uma ferramenta de análise linguística computacional que identifica e classifica estratégias de simplificação textual em traduções intralinguais. O sistema opera em nível discursivo, permitindo validação humana e aprendizado contínuo.

## 🏗️ Status Atual - Foundation Layer

✅ **IMPLEMENTADO:**
- Estrutura completa do projeto (backend/frontend)
- API FastAPI com health checks funcionais
- Interface React com comunicação estabelecida
- Sistema de logging estruturado
- Testes automatizados configurados
- CI/CD pipelines funcionais
- Documentação técnica completa

🚧 **EM DESENVOLVIMENTO:**
- Intervenção 2.1.2: Interface de entrada de texto
- Processamento de arquivos (.txt, .md, .docx, .pdf)
- Alinhamento semântico com BERTimbau
- Interface interativa de análise

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Git

### Instalação

**1. Clonar o repositório:**
```bash
git clone <repository-url>
cd net-est
```

**2. Configurar Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

**3. Configurar Frontend:**
```bash
cd ../frontend
npm install
cp .env.example .env
```

### Execução

**Backend (Terminal 1):**
```bash
cd backend
python src/main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

Acesse: http://localhost:3000

## 🏛️ Arquitetura

### Backend (Python/FastAPI)
- **Framework:** FastAPI com Pydantic
- **Logging:** Estruturado com structlog
- **Testes:** pytest com cobertura
- **Containerização:** Docker ready

### Frontend (React)
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios com interceptors
- **Estado:** React hooks

### Infraestrutura
- **CI/CD:** GitHub Actions
- **Deploy:** Hugging Face Spaces (backend) + Vercel (frontend)
- **Banco:** SQLite → PostgreSQL (futuro)

## 📊 Módulos do Sistema

1. **Pré-processador** - Entrada de texto e arquivos
2. **Alinhador Semântico** - Correspondência entre textos
3. **Extrator/Classificador** - Identificação de estratégias
4. **UI Interativa** - Interface de análise e edição
5. **Coletor de Feedback** - Aprendizado contínuo
6. **Gerador de Relatórios** - Exportação de resultados

## 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v --cov=src

# Frontend
cd frontend
npm run test
```

## 📝 Documentação

- [Arquitetura do Sistema](docs/proposta_arquitetura_algoritmo.md)
- [Plano de Desenvolvimento](docs/plano_desenvolvimento_NET.md)
- [Especificação Foundation Layer](docs/intervencao_2.1.1_foundation_layer.md)
- [Créditos e Autoria](docs/AUTORIA_E_CREDITOS.md)

## 👥 Equipe

- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Analista de Sistemas/Desenvolvedor Principal:** Wisley Vilela (Doutorando em Linguistica Aplicada PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda em Linguística Aplicada PIPGLA/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 4, ChatGPT-4o, Gemini 2.5 Pro

## 🏢 Instituições

- **Núcleo de Estudos de Tradução - UFRJ**
- **Politécnico de Leiria (PT)**

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links Úteis

- [Documentação da API](http://localhost:8000/docs) (após executar backend)
- [Repositório GitHub](https://github.com/Wisleyv/net-est-web)
- [Issues e Sugestões](https://github.com/Wisleyv/net-est-web/issues)

---

**Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - UFRJ**

## Autoria e Créditos

**Projeto:** NET-EST - Sistema de Análise de Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**
- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

**Apoio:** CAPES (via bolsa de doutorado)

**Licença:** MIT License | **Status:** Em Desenvolvimento

---

## Visão Geral

O NET-EST é uma ferramenta de análise linguística computacional desenvolvida para identificar e classificar estratégias de simplificação textual em traduções intralinguísticas, em língua portuguesa. O sistema opera no nível do discurso (parágrafos) e implementa interação humana no circuito, permitindo validação e correção das análises automáticas.

### Características Principais

- **Análise Discursiva:** Foco no nível do parágrafo, não da sentença
- **Alinhamento Semântico:** Usa BERTimbau para matching de conteúdo
- **Human-in-the-Loop:** Controle humano sobre validação e correções
- **Modular:** Arquitetura flexível e intercambiável
- **Evolução por Feedback:** Aprendizado contínuo através de correções

## Tecnologias

### Backend
- **Python 3.9+**
- **FastAPI** - API REST moderna e documentada
- **SentenceTransformers** - Embeddings com BERTimbau
- **spaCy** - Processamento de linguagem natural
- **SQLite/PostgreSQL** - Persistência de dados

### Frontend
- **React/Vue.js** - Interface de usuário interativa
- **Vite** - Build tool moderna
- **Axios** - Cliente HTTP

### Infraestrutura
- **Hugging Face Spaces** - Deploy do backend
- **Vercel/Netlify** - Deploy do frontend
- **Docker** - Containerização

## Estrutura do Projeto

```
net-est/
├── backend/           # API Python/FastAPI
├── frontend/          # Interface React/Vue
├── docs/              # Documentação completa
├── tests/             # Testes automatizados
└── README.md          # Este arquivo
```

## Quick Start

### Pré-requisitos
- Python 3.9+
- Node.js 16+
- Git

### Instalação Local

1. **Clone o repositório:**
```bash
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est
```

2. **Configure o backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

3. **Configure o frontend:**
```bash
cd frontend
npm install
npm run dev
```

4. **Acesse:** http://localhost:3000

## Documentação

### Para Desenvolvedores
- [Fase 1 - Implementação Técnica](./docs/fase1_implementacao_tecnica.md)
- [Plano de Desenvolvimento](./docs/plano_desenvolvimento_NET.md)
- [Proposta de Arquitetura](./docs/proposta_arquitetura_algoritmo.md)

### Para Pesquisadores
- [Autoria e Créditos Detalhados](./docs/AUTORIA_E_CREDITOS.md)
- [Metodologia Linguística](./docs/Tabela%20Simplificação%20Textual.md)

## Contribuições

### Acadêmicas
Contribuições de pesquisadores em linguística, tradução e processamento de linguagem natural são bem-vindas:
- Validação de metodologias
- Testes com corpora específicos
- Propostas de novas estratégias de análise

### Técnicas
- Report de bugs via GitHub Issues
- Pull requests com melhorias
- Propostas de otimização

## Citação

Se você usar o NET-EST em sua pesquisa, por favor cite:

```bibtex
@software{net_est_2025,
  title={NET-EST: Sistema de Análise de Estratégias de Simplificação em Tradução Intralingual},
  author={Vilela, Wisley and Pimentel, Janine and Lima, Luanny Matos},
  year={2025},
  institution={Núcleo de Estudos de Tradução, UFRJ},
  url={https://github.com/Wisleyv/net-est-web}
}
```

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE) - veja o arquivo LICENSE para detalhes.

## Contato

### Questões Acadêmicas

- **Profa. Dra. Janine Pimentel:** [janinepimentel@letras.ufrj.br](mailto:janinepimentel@letras.ufrj.br)
- **Núcleo de Estudos de Tradução:** [https://net.letras.ufrj.br/pesquisadores/](https://net.letras.ufrj.br/pesquisadores/)
- **Luanny Matos de Lima:** [lua.matoslima@letras.ufrj.br](mailto:lua.matoslima@letras.ufrj.br)

### Questões Técnicas

- **Wisley Vilela:** [wisley@wisley.net](mailto:wisley@wisley.net)
- **GitHub Issues:** [Issues do Projeto](https://github.com/Wisleyv/net-est-web/issues)

---

**Desenvolvido pelo Núcleo de Estudos de Tradução - UFRJ**
