---
name: "M4: Visualização de Saliência & Micro-Spans"
about: Acompanhar progresso do Marco 4 (visualização de saliência e micro-spans)
title: "M4: Visualização de Saliência & Micro-Spans"
labels: [enhancement, milestone-m4]
assignees: []
---

## 🔍 Contexto
Implementar visualização de saliência (gradient / barra lateral) e infraestrutura inicial de micro-spans heurísticos conforme design.

Design Doc: `docs/m4_visualizacao_saliencia_microspans.md`

## 🎯 Objetivo
Entregar camada visual de saliência por sentença e extrator heurístico inicial de micro-spans com flags desativados por padrão.

## ✅ Critérios de Aceite
- Flags backend (`include_visual_salience`, `include_micro_spans`) funcionam e preservam retrocompatibilidade.
- Resposta hierárquica inclui `micro_spans` apenas quando solicitado.
- Visualização de saliência pode ser alternada sem nova chamada (re-uso de dados carregados).
- Cobertura de testes nova ≥ 85% nos módulos adicionados.
- Overhead médio < 120 ms (textos médios) quando micro-spans ativos.

## 🗂 Escopo
Inclui: heurística ngram básica, cache LRU micro-spans, UI gradiente, tooltip micro-spans.  
Exclui: modelo ML dedicado, feedback granular, edição manual de micro-spans.

## 📦 Entregáveis
- `micro_span_extractor.py`
- Atualização dos modelos (Pydantic) para `micro_spans`
- Ajustes em `comparative_analysis_service` (integração condicional)
- Componentes frontend (heatmap / tooltip)
- Testes (unitários + integração)
- Métricas simples (logging tempo e contagem)

## 🧪 Plano de Testes (Resumo)
- Unit: geração top-K, não overlap, normalização pesos
- Integration API: flags on/off
- Performance: benchmark sintético (tempo adicional)
- Snapshot: saída estável para corpus pequeno

## 📋 Checklist
- [ ] Backend: flags em `AnalysisOptions`
- [ ] Backend: modelo `MicroSpan` + extensão `SentenceNode`
- [ ] Backend: extrator heurístico ngram
- [ ] Backend: cache LRU micro-spans (`MICRO_SPAN_CACHE_MAX`)
- [ ] Backend: integração no build hierárquico
- [ ] Backend: testes unitários extrator
- [ ] Backend: testes API flags
- [ ] Backend: benchmarks leves (log) 
- [ ] Frontend: estado global flags (Zustand)
- [ ] Frontend: componente gradient sentenças
- [ ] Frontend: tooltip micro-spans
- [ ] Frontend: toggle visual + fallback acessível
- [ ] Docs: atualizar README (status M4 em progresso)
- [ ] Docs: adicionar exemplos JSON com micro-spans
- [ ] QA: revisão de acessibilidade (contraste)

## ⏱ Métricas a Coletar
| Métrica | Meta |
|---------|------|
| Overhead médio micro-spans | < 120 ms |
| Cache hit-rate micro-spans | ≥ 60% em reprocessamentos |
| Cobertura testes módulo | ≥ 85% |

## 🧭 Riscos & Mitigações
| Risco | Mitigação |
|-------|-----------|
| Latência excessiva | Limitar K, cache, lazy compute |
| Poluição visual | Toggle claro + modo reduzido |
| Heurística fraca | Iterar com corpus anotado | 
| Conflitos CSS | Escopo via módulos / prefixos |

## 🗓 Fases
1. Infra / Flags / Modelos
2. Heurística & Testes
3. Integração & Cache
4. Visualização & Tooltip
5. Acessibilidade & Métricas
6. Refino / Documentação final

## 📝 Notas / Log de Progresso
Adicionar atualizações curtas (data + resultado) aqui.

---
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
