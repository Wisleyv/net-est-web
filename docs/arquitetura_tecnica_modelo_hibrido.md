# Arquitetura Técnica - Sistema de Detecção de Estratégias

## Visão Geral

O sistema NET-EST utiliza uma **arquitetura híbrida** para detecção de estratégias de simplificação textual, combinando análise semântica com modelos de linguagem leves e heurísticas linguísticas especializadas.

## Decisões Arquiteturais

### Escolha do Modelo de Linguagem

#### Contexto do Problema
O sistema inicialmente utilizava o modelo `neuralmind/bert-base-portuguese-cased` (~430MB) para análise semântica. Contudo, esta abordagem apresentou limitações críticas:

1. **Timeout de Performance**: Análises de textos longos (>2000 palavras) excediam o limite de 120 segundos
2. **Cold Start Penalty**: Primeira inicialização do modelo levava 30-60 segundos
3. **Consumo de Memória**: 430MB de RAM impactava a escalabilidade do sistema
4. **Complexidade Computacional**: Cálculos semânticos intensivos para textos extensos

#### Solução Implementada: Modelo Híbrido

**Modelo Adotado**: `paraphrase-multilingual-MiniLM-L12-v2`

**Justificativas Técnicas**:
- **Tamanho Otimizado**: 118MB (73% de redução em relação ao modelo anterior)
- **Performance**: 5-10x mais rápido para inferência
- **Suporte Multilíngue**: Inclui suporte nativo ao português (`pt`)
- **Acurácia Preservada**: 80-90% da precisão do modelo maior
- **Arquitetura Distilled**: Versão otimizada do BERT original

**Validação da Escolha**:
- **Downloads**: 172.6M (demonstra confiabilidade da comunidade)
- **Likes**: 954 (indicador de qualidade)
- **Licença**: Apache 2.0 (compatível com uso acadêmico)
- **Suporte**: Ativo pela Hugging Face/sentence-transformers

## Arquitetura de Detecção Híbrida

### Componentes do Sistema

#### 1. Extração de Features
O sistema extrai múltiplas dimensões de evidência:

```python
features = {
    'semantic_similarity': 0.917,        # Similaridade semântica ML
    'word_complexity_reduction': 0.293,  # Redução de complexidade lexical
    'vocabulary_overlap': 0.476,         # Sobreposição vocabular
    'sentence_count_ratio': 1.5,         # Razão de fragmentação
    'compression_ratio': 0.266,          # Taxa de compressão
    'length_ratio': 0.734                # Razão de tamanho
}
```

#### 2. Classificação Baseada em Evidências
Cada estratégia é detectada através de critérios múltiplos:

**Exemplo - SL+ (Adequação de Vocabulário)**:
```python
if (features['word_complexity_reduction'] > 0.15 and 
    features['semantic_similarity'] > 0.7):
    confidence = min(0.9, 
        features['word_complexity_reduction'] * 2 + 
        features['semantic_similarity'] * 0.5)
```

#### 3. Thresholds Acadêmicos
- **Alta Confiança**: ≥0.8 (para estratégias críticas como OM+)
- **Média Confiança**: ≥0.6 (para estratégias gerais)
- **Validação Semântica**: Obrigatória para todas as detecções

### Pipeline de Processamento

1. **Pré-processamento**: Limitação de texto (50k caracteres)
2. **Análise Semântica**: Cálculo de similaridade ML
3. **Extração de Features**: Múltiplas dimensões linguísticas
4. **Classificação Híbrida**: ML + heurísticas especializadas
5. **Filtragem Acadêmica**: Thresholds de confiança rigorosos

## Performance e Escalabilidade

### Métricas de Performance
- **Texto Curto (<500 chars)**: ~3-5 segundos
- **Texto Médio (500-2000 chars)**: ~8-15 segundos
- **Texto Longo (2000-5000 chars)**: ~15-30 segundos
- **Limite Máximo**: 50.000 caracteres

### Otimizações Implementadas
- **Model Caching**: Carregamento único na inicialização
- **Feature Engineering**: Cálculos otimizados para português
- **Early Stopping**: Evita processamento desnecessário
- **Memory Management**: Gestão eficiente de embeddings

## Validação Acadêmica

### Critérios de Qualidade
- **Precision**: Redução de falsos positivos através de thresholds rigorosos
- **Recall**: Manutenção de detecção de estratégias relevantes
- **Explainability**: Scores de confiança baseados em evidências
- **Reproducibility**: Resultados consistentes para mesmos inputs

### Conformidade com "Tabela de Estratégias"
- ✅ **14 Estratégias Canônicas**: Todas implementadas
- ✅ **OM+ Controlado**: Detecção apenas quando `enable_om_detection=True`
- ✅ **PRO+ Reservado**: Implementação para estratégias experimentais
- ✅ **Confidence Scoring**: Scores calibrados por tipo de estratégia

## Considerações Futuras

### Melhorias Planejadas
1. **Modelo Fine-tuned**: Treinamento específico para português brasileiro
2. **Ensemble Methods**: Combinação de múltiplos modelos leves
3. **Active Learning**: Incorporação de feedback humano
4. **Performance Profiling**: Otimização baseada em dados reais

### Escalabilidade
- **Containerização**: Docker ready para deploy
- **Load Balancing**: Suporte a múltiplas instâncias
- **Caching Strategy**: Redis para resultados frequentes
- **Monitoring**: Logs estruturados para análise de performance

---

**Documento Técnico**: Versão 1.0 - Agosto 2025  
**Revisão**: Implementação do modelo híbrido paraphrase-multilingual-MiniLM-L12-v2  
**Autor**: Sistema NET-EST - Núcleo de Estudos de Tradução UFRJ
