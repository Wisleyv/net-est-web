---

## Análise de cobertura: proposta vs implementação atual

A proposta organiza o sistema em 6 módulos (Módulos 1 a 6). Abaixo avalio cada um em termos de implementação detectada no código, testes e documentação.

1. MÓDULO 1 — Pré-processador e Tratamento de Entrada

- Proposta: handlers de arquivo (.txt, .md, .docx, .odt, .pdf), validação de volume (limite ~2000 palavras), outputs `source_text` e `target_text`.
- Implementação encontrada:
  - Há infraestrutura de leitura/entrada no backend e utilitários (ver `backend/src/...`), suporte a quickstart e scripts para iniciar o backend.
  - Não vi um único utilitário monolítico “textract-like” explicitamente documentado, mas o pré-processamento (handlers) existe como componentes menores (e testes indicam processamento de inputs em pipelines).
  - Conclusão: Parcialmente implementado — núcleo do fluxo está presente; cobertura de formatos pesados (pdf/odt) não verificada/confirmada automaticamente. Validação de volume (mensagem avisando textos longos) está documentada como recomendação; não encontrei checagem explícita nos trechos lidos, mas pode estar implementada no pré-processador.

2. MÓDULO 2 — Alinhador Semântico Discursivo

- Proposta: segmentação por parágrafo, vetorização (SentenceTransformer BERTimbau), matriz de similaridade, aligned_pairs / unaligned_source_indices.
- Implementação encontrada:
  - Arquivos e modelos para alinhamento: semantic_alignment_service.py e modelos semantic_alignment.py.
  - Evidências de uso de aligned_pairs e unaligned_source_indices (várias ocorrências no backend).
  - Conclusão: Implementado (alinhador de parágrafos e saída `alignment_data` presente).

3. MÓDULO 3 — Extrator de Features e Classificador

- Proposta: `classify_all` que consome `alignment_data` + `user_config`, aplica heurísticas ponderadas, evita gerar `PRO+`.
- Implementação encontrada:
  - feature_extraction_service.py (processa aligned_pairs, unaligned paragraphs, aplica heurísticas).
  - Há estruturas de tag_config / user_config e logs que indicam extração de features e geração de anotações.
  - Conclusão: Implementado (heurísticas e pipeline de extração/classificação presentes). Algumas funcionalidades avançadas (amostragem de 5 termos, spaCy+TF-IDF) podem estar parcialmente implementadas ou opcionais. A regra “never produce PRO+” está documentada na proposta; é provável que regras do motor sigam essa política (a revisão manual seria necessária para confirmar política exata).

4. MÓDULO 4 — Gerador de Saída e Interface do Usuário (UI)

- Proposta: UI com duas colunas (source/target), realces por cor, tags editáveis (menu), tooltip, tabela de análise e edição (HITL).
- Implementação encontrada:
  - Frontend React com componentes: `ComparativeResultsDisplay.jsx`, `StrategyDetailPanel.jsx`, `FeedbackCollection.jsx`, stores (Zustand) como useAnnotationStore.js.
  - Realce/markers no DOM, interações de accept/modify/reject; side-panel com detalhes.
  - E2E Playwright specs e unit tests para marker rendering/feedback behavior.
  - Conclusão: Implementado. O UI atual suporta realce, edição via painel e mecanismo de feedback. Observação: o usuário reportou regressões no mapeamento de texto e edição de ranges; isso indica a implementação existe porém algumas regressões/bugs recentes afetaram usabilidade (por exemplo, seleção direta na UI e ajuste de ranges foram afetados e precisam restauro/refatoração).

5. MÓDULO 5 — Coletor de Feedback e Banco de Conhecimento

- Proposta: `POST /api/feedback` (ou endpoints /api/v1/annotations with audit), persistência (SQLite/FS), registro de correções para ML.
- Implementação encontrada:
  - API de anotações: annotations.py — rota `/api/v1/annotations` e endpoints de export (`/export`, search, audit).
  - Repositórios dual-write / fallback FS/SQLite estão na base (docs sobre dual-write, repository_migration_notes.md). Tests and fixtures existem para persistência (isolated_repo).
  - Export CLI e endpoint `/api/v1/annotations/export` implementados e testados.
  - Conclusão: Implementado (persistência, export, endpoints de feedback/anotação e audit trail presentes). Bom nível de cobertura.

6. MÓDULO 6 — Gerador de Relatórios

- Proposta: exportação (Markdown/CSV/JSONL), pandoc/pypandoc integration.
- Implementação encontrada:
  - Ferramenta CLI de export (`python -m src.tools.export`) e suporte a JSONL/CSV, com fields `explanation` e flags de scope (gold/raw/both).
  - Tests para export e documentação em ONBOARDING.md.
  - Conclusão: Implementado (export pipeline e CLI prontos).

---

## Itens transversais e infraestrutura

- Testes: há testes unitários e E2E (Playwright) e fixtures (isolated_repo). Arquitetura de E2E documentada e integrada.
- Feature flags: `enableFeedbackActions` gateia controles de edição; mecanismo documentado e testado.
- Hospedagem & deploy: propostas para Hugging Face Spaces (backend) e Vercel (frontend) documentadas.
- Observability / logs: apontado como próximo passo (Phase 4f) - ainda há espaço para instrumentação adicional (structlog, métricas).
- Documentação: ampla documentação e notas (ONBOARDING.md, NEXT_STEPS.md, docs/HITL_PHASE4_PLAN.md). READMEs atualizados recentemente (p.ex. README.md em 2025-09-11).

---

## Conclusão da análise: quanto foi alcançado e o que falta

Proposta original: pipeline completa, modular, HITL, feedback persistente e export para ML. Comparando com o repositório:

O que já está implementado (conforme proposta)

- Módulos 2, 3, 4, 5 e 6 — componentes fundamentais implementados:
  - Alinhamento semântico (parágrafo → aligned_pairs / unaligned indices).
  - Extração de features e heurísticas de classificação.
  - Interface interativa (realce, painel de detalhes, ações HITL).
  - Persistência (FS + SQLite), export com escopos (gold/raw), CLI de export.
  - Testes unitários e E2E (Playwright) cobrindo flows principais.
- Infraestrutura de desenvolvimento e recomendações de deploy documentadas.
- Mecanismos de feedback e audit implementados e testados.

O que está parcial ou ausente / precisa de atenção

- Módulo 1 (cobertura de formatos e UX de upload): suporte básico existe, mas a cobertura completa de todos formatos (PDF/ODT/complexos) precisa verificação e testes automatizados; a checagem/aviso de volume (2000 palavras) não teve confirmação completa no código lido.
- UX de interação direta no texto (melhorias sugeridas): embora a UI ofereça criação/edição via painel e criação por seleção (documentado), o time reportou regressões recentes:
  - "Text mapping" (mapear trechos onde estratégias ocorrem) — regressão detectada: esta funcionalidade voltou a apresentar falhas; precisa de correção.
  - "Range modification" (ajustar highlight span) — disponível como fluxo via painel, mas comportamento está instável/regredido.
  - Experiência inline (seleção direta + atribuição/edição minimalista) — é uma melhoria desejada (planejada) que ainda não está completamente madura; implementar fluxo inline simplificado é roadmap futuro.
- Observability, performance tuning e relatórios avançados (Phase 4f): planejados, alguns itens ainda pendentes (instrumentação de timing, métricas de erro, tuning para sessões muito grandes).
- Bulk operations e UX refinements (multi-aceitar/rejeitar) — apontados como pendentes.

Risco/Prioridade (sugestão)

- Alta prioridade: Restaurar/estabilizar text mapping e range modification (faça regressions tests e E2E específicos para seleção e ajuste de spans).
- Alta prioridade: Validar Módulo 1 para inputs PDF/ODT se o projeto requer ingestão desses formatos; adicionar testes de integração.
- Média prioridade: UX inline (seleção → tag) — melhorar pós estabilização.
- Média/baixa: Observability e performance (importante, mas não crítico para experimentos iniciais).

---