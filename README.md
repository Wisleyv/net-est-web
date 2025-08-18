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

## 📊 Módulos do Sistema

1. **Pré-processador** - Entrada de texto e arquivos
2. **Alinhador Semântico** - Correspondência entre textos
3. **Extrator/Classificador** - Identificação de estratégias
4. **UI Interativa** - Interface de análise e edição
5. **Coletor de Feedback** - Aprendizado contínuo
6. **Gerador de Relatórios** - Exportação de resultados

## 🧭 Roadmap (Milestones Overview)

| Milestone | Focus | Status | Key Deliverables |
|-----------|-------|--------|------------------|
| M1 | Paragraph & Sentence Alignment | ✅ Done | Semantic alignment + enhanced Portuguese sentence splitter |
| M2 | Hierarchical Output (Paragraph → Sentence) | ✅ Done | Hierarchy model, local sentence salience normalization, control flags |
| M3 | Sentence Salience & Cache | ✅ Done | SalienceProvider (freq/KeyBERT/YAKE), include_salience & salience_method flags, LRU cache |
| M4 | Visualization & Micro-Spans | 🚧 In Progress | Salience heatmap / highlighting, lexical micro-spans ([Design](./docs/m4_visualizacao_saliencia_microspans.md)) |
| M5 | Human Feedback Loop | 🔜 Planned | Feedback endpoint, correction persistence |
| M6 | Advanced Analytics & Reporting | 🔜 Planned | Session metrics, structured export |

### M3 – Salience (Summary)

Delivered salience provider with:
* Default frequency-based method (Portuguese stopword aware).
* Optional KeyBERT / YAKE (when installed) selectable via `salience_method`.
* Request flags: `include_salience` and `salience_method` (per-request override).
* Per-paragraph normalization for intra-paragraph comparability.
* Deterministic hash-based caching + LRU (`SALIENCE_CACHE_MAX`) preventing unbounded growth.
* Tests: fallback behavior, flag control, cache reuse, LRU eviction.

Next recommended step (M4 start): implement sentence salience visualization (gradient / side bars) and scaffold micro-span extraction while retaining hierarchical compatibility.

### M4 – Visualization & Micro-Spans (Summary)

Status: In Progress. Backend flags (`include_visual_salience`, `include_micro_spans`, `micro_span_mode`, `salience_visual_mode`) implemented; heuristic `MicroSpanExtractor` (`ngram-basic`) integrated with hierarchy (version bump to 1.2 when active) and unit-tested. Next: frontend visualization (gradient / bars) and tooltip UI.

Immediate focus:
* Frontend gradient / bar visualization layer.
* Tooltip or popover listing micro-spans with normalized salience.
* Optional performance metrics (latency / cache hit-rate) logging.

Phase exit criteria (updated): backend integration complete (DONE), tests green (DONE), frontend visualization prototype (PENDING), documentation sample payload with micro_spans (PENDING).

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

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
