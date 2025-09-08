# NET-EST - Sistema de Análise de Estratégias de Simplificação Textual

Sistema de análise computacional para estratégias de simplificação em tradução intralingual desenvolvido pelo Núcleo de Estudos de Tradução da UFRJ em parceria com o Politécnico de Leiria.

## 🎯 Sobre o Projeto

O NET-EST é uma ferramenta de análise linguística computacional que identifica e classifica estratégias de simplificação textual em traduções intralinguais. O sistema opera em nível discursivo (parágrafos), permitindo validação humana e aprendizado contínuo.

##  Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Git

### Instalação e Execução

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python start_optimized.py
```

**Frontend:**
```bash
cd frontend
npm ci
npm run dev
```

Acesse a aplicação em: http://localhost:3000

## 📚 Documentação

Consulte nossa documentação estruturada para mais informações:

- [Documentação Central](./DOCUMENTATION.md) - Hub com links para toda a documentação
- [Arquitetura](./ARCHITECTURE.md) - Visão detalhada da arquitetura do sistema
- [Guia de Desenvolvimento](./DEVELOPMENT.md) - Instruções para desenvolvedores
- [Recursos de Desenvolvimento](./DEVELOPMENT_RESOURCES.md) - Guias de solução de problemas e recursos
- [Migração e Persistência (FS/SQLite)](./docs/repository_migration_notes.md) - Modos de persistência, dual-write, fallback, migração e rollback
- [HITL Plan (Phase 4)](./docs/HITL_PHASE4_PLAN.md) - Notas das fases 4b–4d e flags

## 📊 Módulos do Sistema

1. **Pré-processador** - Entrada de texto e arquivos
2. **Alinhador Semântico** - Correspondência entre textos
3. **Extrator/Classificador** - Identificação de estratégias
4. **UI Interativa** - Interface de análise e edição
5. **Coletor de Feedback** - Aprendizado contínuo
6. **Gerador de Relatórios** - Exportação de resultados

##  Equipe

- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)
- **Agentes IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash

## 🏢 Instituições

- **Núcleo de Estudos de Tradução - UFRJ**
- **Politécnico de Leiria (PT)**

##  Links Úteis

- [Documentação da API](http://localhost:8000/docs) (após executar backend)
- [Repositório GitHub](https://github.com/Wisleyv/net-est-web)
- [Issues e Sugestões](https://github.com/Wisleyv/net-est-web/issues)

## ✅ NEXT STEPS (Phase 4)

- 4e: Alinhar esquema de exportação para ML/gold datasets (campos consistentes, versionamento de schema)
- 4f: Acessibilidade (ARIA, navegação teclado) + testes E2E
- Opcional: Toolbar global de exportação, toasts de confirmação, paginação da timeline

## � Demos / Example scripts

Demo and example scripts (non-tests) are available in the `demos/` directory at the repository root. These are not collected by pytest and are intended for manual, human-in-the-loop experimentation and demonstration.

Examples:
- `demos/test_confidence_demo.py` — Full demonstration of the Confidence & Weighting Engine (M5).


## �📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
