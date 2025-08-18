---

### **Módulo 3 (Revisado): Extrator de Features Hierárquico e Classificador Híbrido**

#### **Finalidade**

Este módulo atua como o núcleo analítico do sistema NET v3.0. Sua função é receber os resultados do alinhamento discursivo do Módulo 2 e orquestrar uma **análise hierárquica (top-down)**, identificando estratégias de simplificação em múltiplos níveis (parágrafo, sentença e frase). Ele utiliza um conjunto de ferramentas especializadas, incluindo um modelo de linguagem leve e extratores de features linguísticas, para classificar as transformações de acordo com a configuração definida pelo usuário.

#### **Inputs**

1. `alignment_data` (JSON): Objeto vindo do Módulo 2, contendo as chaves `aligned_pairs` e `unaligned_source_indices`.
2. `user_config` (JSON): Objeto vindo da UI, especificando quais tags estão ativas e seus pesos (`{'OM+': {'active': false}, 'SL+': {'active': true}, ...}`).
3. `source_paragraphs` (Lista de strings): O texto fonte já segmentado.
4. `target_paragraphs` (Lista de strings): O texto alvo já segmentado.

#### **Ferramentas Chave (Atualizadas)**

1. **Modelo de Linguagem (Substituição do BERTimbau):**
   
   * **Modelo:** `paraphrase-multilingual-MiniLM-L12-v2`
   * **Justificativa:** Conforme o requisito 1, este modelo substitui o pesado BERTimbau. Ele oferece um excelente balanço de performance e precisão para o português, sendo ideal para as tarefas de alinhamento semântico de parágrafos e sentenças sem causar timeouts. Será usado para gerar embeddings.

2. **Extrator de Frases-Chave (Nova Ferramenta):**
   
   * **Ferramenta:** Google `LangExtract`
   * **Avaliação de Aplicabilidade:** A ferramenta é **altamente aplicável e recomendada** para o nível micro da análise. Sua força reside em identificar as frases nominais e os termos mais salientes de um texto. No nosso contexto, ele não substitui outras ferramentas, mas as **enriquece**. Usaremos o `LangExtract` para determinar a **importância** de uma simplificação lexical. Uma `[SL+]` aplicada a uma frase-chave (ex: um termo técnico complexo) é mais significativa do que uma aplicada a uma palavra comum.
   * **Aplicação:** Será usado na análise de frases para dar mais peso e confiança às detecções de `[SL+]` que ocorrem em trechos linguisticamente importantes.

3. **Outras Ferramentas:** `spaCy` (para análise sintática e POS tagging), `difflib` (para comparação de tokens), `textstat` (para métricas de legibilidade).

#### **Arquitetura Interna e Processo de Detecção Hierárquico**

O módulo opera em uma sequência de três estágios, do macro para o micro.

##### **Estágio 1: Análise Macro (Nível de Parágrafo/Discurso)**

* **Processo:**
  1. **Processar Não Alinhados:** Itera sobre a lista `alignment_data['unaligned_source_indices']`. Se `user_config['OM+']['active']` for verdadeiro, gera uma anotação `[OM+]` para cada parágrafo fonte omitido.
  2. **Processar Alinhados:** Itera sobre a lista `alignment_data['aligned_pairs']`. Para cada par, realiza uma análise discursiva.
* **Tags Detectadas:**
  * `[OM+]`: Um parágrafo fonte não tem correspondente semântico no alvo.
  * `[RF+]` (Reescrita Global): Um par fonte/alvo tem alta similaridade semântica mas uma redução de palavras significativa (ex: >30%).
  * `[RD+]` (Estruturação de Conteúdo): A ordem dos índices dos parágrafos alinhados é diferente entre o fonte e o alvo (ex: parágrafo fonte 5 alinha com alvo 2, e fonte 2 alinha com alvo 4).
  * Após a classificação, para cada par alinhado, o sistema invoca o **Estágio 2**.

##### **Estágio 2: Análise Meso (Nível de Sentença/Cláusula)**

* **Processo:**
  1. **"Zoom-in":** Para cada par de parágrafos alinhados do Estágio 1, a função `analyze_sentences` é chamada.
  2. **Segmentação e Alinhamento de Sentenças:** Os parágrafos fonte e alvo são divididos em sentenças. O modelo `MiniLM-L12-v2` é usado novamente para criar embeddings para estas sentenças e alinhá-las, gerando uma nova lista de `aligned_sentence_pairs`.
  3. **Análise das Relações:** O sistema analisa as relações entre as sentenças alinhadas.
* **Tags Detectadas:**
  * `[RP+]` (Fragmentação Sintática): Uma sentença fonte alinha com duas ou mais sentenças alvo.
  * `[EXP+]` (Explicitação): Uma sentença alvo é significativamente mais longa que a sua correspondente fonte e introduz novas palavras-chave (identificadas com `LangExtract` ou análise de TF-IDF).
  * `[AS+]` (Alteração de Sentido): Um par de sentenças alinhadas apresenta um score de similaridade semântica abaixo de um limiar secundário (ex: < 0.6).
  * Para cada par de sentenças alinhadas, o sistema invoca o **Estágio 3**.

##### **Estágio 3: Análise Micro (Nível de Frase/Palavra)**

* **Processo:**
  1. **"Final Zoom":** Para cada par de sentenças alinhadas do Estágio 2, a função `analyze_phrases` é chamada.
  2. **Análise Diferencial:** `difflib.SequenceMatcher` é usado para encontrar as operações `replace` entre os tokens das duas sentenças.
  3. **Análise Lexical Enriquecida com `LangExtract`:**
     * **a.** Executa-se `LangExtract` na sentença fonte para extrair uma lista de frases-chave (ex: `['fatores psicossociais', 'tratamento medicamentoso']`).
     * **b.** Para cada operação `replace` do `difflib`, o sistema verifica se os tokens substituídos (`source_tokens`) fazem parte de alguma das frases-chave extraídas.
     * **c.** **Extração de Features:** Calcula-se o vetor de features para a operação (mudança em sílabas, frequência, etc.). Se a operação ocorreu dentro de uma frase-chave (passo b), um feature booleano `is_key_phrase` é setado para `True`.
  4. **Motor de Regras Micro:** Um conjunto de heurísticas classifica a operação com base nas features.
* **Tags Detectadas:**
  * `[SL+]`: Uma operação `replace` que resulta em redução de complexidade lexical. A confiança desta tag é **aumentada** se `is_key_phrase` for `True`, indicando uma simplificação mais significativa.
  * `[MV+]`: Análise sintática (`spaCy`) da operação `replace` para detectar mudanças na voz verbal.
  * `[TA+]`: Detecção de substituição de pronomes por substantivos explícitos.
  * **`[MOD+]`**: A mais desafiadora. Pode ser inferida por um `replace` onde a similaridade semântica da frase é moderada e há uma mudança na estrutura gramatical ou no registro (formal -> informal).

#### **Output**

O output final do módulo permanece um **objeto JSON com estrutura hierárquica (em árvore)**. Cada nó na árvore representa uma anotação e contém: `level` (paragraph, sentence, phrase), `tag`, `confidence`, `source_text/indices`, `target_text/indices`, `explanation` e uma chave opcional `nested_findings` que contém uma lista de anotações do nível inferior. Este formato é essencial para suportar a análise detalhada e a visualização hierárquica na UI.
