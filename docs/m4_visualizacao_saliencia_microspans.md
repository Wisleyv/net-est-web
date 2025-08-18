# M4 – Visualização de Saliência & Micro-Spans (Design / Plano de Implementação)

Status: Planejado  
Data do Documento: 2025-08-10  
Responsável Primário: Wisley Vilela  
Revisores: Vilela, W.  

## 1. Contexto & Motivação
Com a conclusão dos Marcos M1–M3 (alinhamento hierárquico e cálculo de saliência com cache + LRU), o próximo passo é tornar a saliência e futuras unidades menores ("micro-spans") visíveis e manipuláveis na interface. Isso facilita: (a) interpretação rápida de trechos mais informativos, (b) suporte a análise qualitativa por especialistas, (c) preparação de dados de treinamento e (d) refinamento futuro das estratégias de simplificação.

## 2. Objetivos
### 2.1 Funcionais
1. Exibir intensidade de saliência por sentença (e futuramente por micro-span) com representação visual intuitiva (heatmap / gradiente / barra lateral).
2. Permitir alternar visualização (ligar/desligar) sem refazer toda a análise (usar dados já retornados se presentes).
3. Preparar estrutura de dados para micro-spans (sub‑sentenças curtas baseadas em n-gramas significativos ou deltas léxicos entre origem e destino).
4. Fornecer API com flags para solicitar: (a) visualização de saliência, (b) micro-spans, (c) modo de renderização preferido.
5. Instrumentar métricas (tempo de geração de micro-spans, número médio por sentença, cache hit-rate saliência).

### 2.2 Não Funcionais
1. Impacto de latência adicional < 120 ms em textos médios (≤ 3k caracteres) quando micro-spans estiverem desativados.
2. Custo incremental de memória previsível (limite configurável para micro-spans por sentença, ex.: máx. 12).
3. Fácil rollback via feature flags.
4. Código modular e testável (≥ 85% cobertura nova lógica núcleo).

## 3. Escopo
Incluído: visualização em nível de sentença (já temos saliência), criação de extrator protótipo de micro-spans (heurístico), integração front-end inicial (gradiente + tooltip), ampliação de modelo de resposta hierárquica.  
Excluído (futuro): modelagem ML dedicada de micro-spans, edição manual granular, persistência histórica de micro-spans.

## 4. Definições
Micro-span: trecho contínuo curto (3–8 tokens) intra-sentença com alta densidade semântica ou relevância diferencial (ex.: termos técnicos, sintagmas núcleo, divergência entre origem e destino).  
Salience Heatmap: Camada visual que colore sentença de acordo com peso normalizado.

## 5. User Stories (Resumo)
1. Como pesquisador quero visualizar rapidamente quais sentenças são mais salientes para priorizar revisão humana.  
2. Como linguista quero destacar subtrechos (micro-spans) com termos-chave para análise qualitativa.  
3. Como desenvolvedor quero desativar micro-spans sem alterar retorno de saliência de sentenças para benchmarking.  
4. Como usuário quero alternar o modo de visualização (gradiente / barras laterais) para preferências pessoais.  
5. Como analista quero exportar dados incluindo micro-spans para estudos quantitativos.

## 6. Métricas de Sucesso
| Métrica | Meta Inicial |
|---------|--------------|
| Latência extra média micro-spans | < 120 ms |
| Cobertura testes novos | ≥ 85% |
| Precisão heurística (sobre amostra rotulada manual) | ≥ 0.60 F1 inicial |
| Cache hit-rate saliência (textos repetidos) | ≥ 70% em cenários de uso interno |

## 7. Arquitetura Técnica (Visão Resumida)
### Backend
Camada adicional: `MicroSpanExtractor` (heurística) chamada após cálculo de saliência quando flag `include_micro_spans` ativa. Resultado integrado em cada `SentenceNode` como `micro_spans: List[MicroSpan]`.

### Frontend
Novo componente opcional de visualização: `SentenceSalienceHeatmap` + integração em `ComparativeResultsDisplay` ou novo painel de “Camadas”.  
Feature flags via estado global (Zustand) + query param (para experimentos).  
Tooltip / overlay para listar micro-spans com pesos relativos.

## 8. Modelo de Dados (Proposta)
Extensão de `SentenceNode`:
```jsonc
{
  "text": "...",
  "salience": 0.73,
  "micro_spans": [
    { "text": "termo técnico", "weight": 0.82, "start": 15, "end": 28, "method": "heuristic-ngram" }
  ]
}
```
Estrutura `MicroSpan` (Pydantic): `text: str; weight: float; start: int; end: int; method: str`.

### 8.1 Exemplo Real de Resposta (Recortado) com `micro_spans` (hierarchy_version 1.2)
```json
{
  "hierarchical_analysis": {
    "hierarchy_version": "1.2",
    "source_paragraphs": [
      {
        "paragraph_id": "p-src-0",
        "sentences": [
          {
            "sentence_id": "s-src-0-0",
            "text": "A complexa arquitetura modular permite extensibilidade robusta e manutenção eficiente do sistema.",
            "salience": 0.94,
            "micro_spans": [
              { "span_id": "ms-2-18", "text": "complexa arquitetura", "start": 2, "end": 21, "salience": 1.0, "method": "ngram-basic", "strategies": [] },
              { "span_id": "ms-32-52", "text": "extensibilidade robusta", "start": 32, "end": 55, "salience": 0.83, "method": "ngram-basic", "strategies": [] }
            ]
          }
        ]
      }
    ],
    "target_paragraphs": [
      { "paragraph_id": "p-tgt-0", "sentences": [] }
    ],
    "metadata": { "alignment_mode": "semantic_paragraph + sentence_cosine" }
  }
}
```
Nota: pesos e offsets ilustrativos; valores reais podem variar conforme heurística. Campo `micro_spans` ausente quando flag desativada (retrocompatibilidade).

## 9. API & Flags
Novos campos em `AnalysisOptions` (proposta):
* `include_visual_salience: bool` (default false – evita custo front-end se não usado)
* `include_micro_spans: bool` (default false)
* `micro_span_mode: Literal["ngram-basic","diff-align"]` (futuro; start com `ngram-basic`)
* `salience_visual_mode: Literal["gradient","bar","none"]` (front-end hint)

Backward compatibility: Se não enviados, comportamento atual mantido.

## 10. Algoritmo Inicial de Micro-Spans (Heurístico)
Pipeline `ngram-basic`:
1. Tokenizar sentença (reutilizar tokenização existente ou fallback regex).
2. Gerar n-grams (n=2..4) filtrando stopwords em extremidades.
3. Atribuir score = média dos pesos de tokens (derivados de frequência ou reciclar normalização já calculada) × fator posição (centralidade) × fator raridade (idf simulado por corpus leve ou contagem inversa local).  
4. Deduplicar overlaps mantendo maior peso.  
5. Selecionar top-K (K configurável; default 5).  
6. Normalizar pesos localmente (max=1.0).

Futuro `diff-align`: usar diferenças lexicais entre origem/destino (palavras inseridas/removidas) para boost de peso.

## 11. Estratégia de Cache & Performance
Reutilizar hash por sentença (já usado para saliência) como chave parcial de micro-span; armazenar micro-spans em dicionário paralelo (LRU pequeno, ex. 256 entradas) para evitar recomputo em reanálises.  
Config env: `MICRO_SPAN_CACHE_MAX`.

## 12. Plano de Implementação (Fases Incrementais)
1. Infra Flags & Modelos (backend + frontend toggles)
2. Heurística `ngram-basic` + testes unitários isolados
3. Integração na construção hierárquica (somente se flag ativa)
4. Camada visual (gradiente por sentença) – reutilizar saliência existente
5. UI micro-spans (tooltip / popover ao passar mouse em sentença)
6. Ajustes de acessibilidade (contraste / modo alto contraste)
7. Métricas & logging leve (tempo, contagem, cache hit)
8. Refino heurístico (overlap, limites, ruído)

## 13. Testes (Plano)
| Tipo | Objetivo |
|------|----------|
| Unit – MicroSpanExtractor | Geração estável top-K, sem overlaps inválidos |
| Unit – Normalização | Max weight = 1.0; preserva ordem decrescente |
| Unit – Flags | Desativado => nenhum campo `micro_spans` presente |
| Integration – API | Retorno inclui micro-spans quando flag ativa |
| Performance | Tempo médio extra < limite alvo |
| Snapshot (pequeno corpus) | Regressão qualitativa controlada |

## 14. Riscos & Mitigações
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Poluição visual | Usuário se distrai | Toggle claro + modo compacto |
| Latência excessiva | UX prejudicada | Limitar K + cache + métricas |
| Overfitting heurístico | Baixa generalização | Corpus diverso de teste |
| Conflito de estilos CSS | Layout quebrado | Escopo CSS (BEM ou módulo) |

## 15. Cronograma (estimativa)
Semana 1: Flags + modelo + heurística base  
Semana 2: Integração + testes + cache micro-spans  
Semana 3: Visualização gradient + tooltip + acessibilidade  
Semana 4: Refino heurístico + métricas + documentação final  

## 16. Checklist de Tarefas
- [ ] Backend: adicionar flags em modelos (`AnalysisOptions`)
- [ ] Backend: implementar `micro_span_extractor.py`
- [ ] Backend: integrar chamada condicional na montagem hierárquica
- [ ] Backend: adicionar cache LRU micro-spans
- [ ] Backend: testes unitários extrator
- [ ] Backend: testes integração API
- [ ] Frontend: estado global (flags + modo visual)
- [ ] Frontend: componente gradient por sentença
- [ ] Frontend: tooltip micro-spans
- [ ] Frontend: acessibilidade (contraste / modo off)
- [ ] Observabilidade: logs & métricas mínimas
- [ ] Docs: atualizar README (link M4 em progresso)
- [ ] Docs: guia de micro-spans (futuro M5+ para ML)

## 17. Estratégia de Lançamento
1. Merge inicial com flags default false.  
2. Ativar em ambiente de teste / branch de demonstração.  
3. Coletar feedback qualitativo.  
4. Ajustar heurística; depois marcar como “Beta” no README.  

## 18. Guia para Abrir Issue de Rastreamento
Criar issue no GitHub com título: `M4: Visualização de Saliência & Micro-Spans`.  
Corpo sugerido (markdown):
```markdown
## M4 – Visualização de Saliência & Micro-Spans

Design Doc: docs/m4_visualizacao_saliencia_microspans.md

### Objetivo
Implementar visualização de saliência + estrutura inicial de micro-spans.

### Checklist
- [ ] Flags / modelos backend
- [ ] MicroSpanExtractor heurístico
- [ ] Integração hierárquica condicional
- [ ] Cache micro-spans
- [ ] API tests
- [ ] UI gradient sentenças
- [ ] Tooltip micro-spans
- [ ] Acessibilidade
- [ ] Métricas & logs
- [ ] Documentação atualizada

### Notas
Adicionar comentários aqui conforme progresso.
```

## 19. Futuras Extensões
* Micro-spans baseados em alinhamento lexical diferencial.
* Weighting híbrido (freq × embedding similarity).
* Feedback humano para reclassificação / ajuste de pesos.

---
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
