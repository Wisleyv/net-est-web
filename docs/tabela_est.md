# Documento Canônico de Estratégias de Simplificação Textual (Português)

## 1. Introdução

Este documento define formalmente as **estratégias de simplificação textual** a serem detectadas automaticamente em pares de textos (fonte e simplificado). Ele integra três fontes:

- **Documento A** (exemplos comentados),

- **Documento B** (definições teóricas das estratégias),

- **Patriotismo rev Nana** (texto-fonte original).

A finalidade é orientar o desenvolvimento de um sistema computacional que identifique, classifique e explique ocorrências de simplificação.

---

## 2. Estratégias de Simplificação

### 2.1 Reformulação (RF+)

**Descrição:**  
Expressão da mesma ideia com palavras diferentes, geralmente visando **simplificação, encurtamento ou clareza**. Pode combinar outras estratégias (ex.: modulação ou simplificação lexical).

**Critérios de Detecção:**

- Identidade semântica parcial ou total entre segmentos do texto fonte e alvo, mas com diferença significativa na **forma verbal**.

- Alteração de ordem de palavras e/ou reestruturação de expressões sem perda do núcleo semântico.

- Pode incluir substituições lexicais neutras (não necessariamente simplificadoras).

**Exemplo:**

- **Fonte (Patriotismo):** “Desde que o Brasil se tornou independente, inúmeras vozes e movimentos políticos recorreram ao ideário do patriotismo e do nacionalismo.”

- **Simplificado (Documento A):** “Desde que o Brasil se tornou independente, várias pessoas e grupos políticos se voltaram para o patriotismo e o nacionalismo.”

- **Análise:** O núcleo semântico é preservado. “Inúmeras vozes e movimentos políticos recorreram ao ideário” foi reformulado para “várias pessoas e grupos políticos se voltaram para”.

---

### 2.2 Simplificação Lexical (SL+)

**Descrição:**  
Substituição de termos **menos frequentes ou especializados** por outros de uso mais comum e acessível.

**Critérios de Detecção:**

- Correspondência semântica próxima, mas com redução de complexidade lexical.

- Preservação da estrutura frasal, alterando apenas termos pontuais.

- Pode ser mapeado com auxílio de frequência de uso em corpora do português.

**Exemplo:**

- **Fonte:** “Suas motivações foram bastante diversas.”

- **Simplificado:** “Suas motivações foram bastante heterogêneas.”

- **Análise:** O termo “heterogêneas” foi trocado por “diversas”, mais coloquial e acessível.

---

### 2.3 Inserção (IN+)

**Descrição:**  
Adição de termos ou trechos não presentes no texto-fonte. Visa explicitar relações, dar ênfase ou reforçar conclusões.

**Critérios de Detecção:**

- Segmentos do texto alvo sem correspondência direta no texto fonte.

- Presença de novos conectores, frases explicativas ou exemplos.

- Pode ser identificado por alinhamento frase a frase (text-to-text alignment).

**Exemplo:**

- **Fonte:** “Um exemplo recente disso são os ataques do 11 de Setembro de 2001, que estimularam o patriotismo norte-americano e guerras ao ‘terror’.”

- **Simplificado:** “Um exemplo recente disso são os ataques do 11 de Setembro de 2001, que estimularam o patriotismo norte-americano e guerras ao ‘terror’.” [IN+ → acréscimo explícito sobre mobilização]

- **Análise:** O trecho inserido enfatiza a **mobilização em resposta aos ataques**, não explicitada no original.

---

### 2.4 Omissão (OM+)

**Descrição:**  
Supressão de segmentos significativos do texto original. Frequentemente usada para condensar ou resumir.

**Critérios de Detecção:**

- Segmentos inteiros presentes no texto-fonte mas ausentes no texto-alvo.

- Diferença considerável de extensão entre parágrafos correspondentes.

- Pode ser mapeado por alinhamento e cálculo de cobertura semântica.

**Exemplo:**

- **Fonte:** A seção sobre Plínio Salgado detalha sua atuação antes e depois da AIB.

- **Simplificado:** O trecho equivalente omite parte da trajetória de Plínio, resumindo em uma frase.

- **Análise:** Cortes de parágrafos e detalhes históricos caracterizam OM+.

---

### 2.5 Reconstrução de Período (RP+)

**Descrição:**  
Divisão ou fusão de períodos complexos para simplificação sintática.

**Critérios de Detecção:**

- Presença de um período longo no texto fonte correspondendo a dois ou mais períodos curtos no texto simplificado (ou vice-versa).

- Preservação de conteúdo semântico, mas com **mudança de segmentação sintática**.

**Exemplo:**

- **Fonte:** “A mobilização ‘patriótica’ do 7 de setembro de 2021, chamada para testar os limites das instituições democráticas, evocou com força as motivações, discursos e bordões dos conservadorismos extremos e fascismos de outros tempos.”

- **Simplificado:** “A mobilização ‘patriótica’ ocorrida no 7 de setembro de 2021 teve como objetivo testar os limites das instituições democráticas. E evocou com força as motivações, discursos e bordões dos conservadorismos extremos e fascismos de outros tempos.”

- **Análise:** Um período extenso foi dividido em dois mais curtos.

---

### 2.6 Reorganização Discursiva (RD+)

**Descrição:**  
Alteração da lógica de conexão entre ideias, por meio de novos conectores ou reordenação de informações.

**Critérios de Detecção:**

- Presença de conectores discursivos diferentes no texto alvo (ex.: “contudo” → “por isso”).

- Mudança na ordem dos parágrafos ou fusão de trechos com rearticulação semântica.

- Pode ser detectado via análise de conectores e estruturas discursivas.

**Exemplo:**

- **Fonte:** “Patriotismo e nacionalismo têm sido invocados por forças políticas díspares e, contudo, também bastante criticados.”

- **Simplificado:** “Patriotismo e nacionalismo têm sido invocados por forças políticas díspares e, por isso, também bastante criticados.”

- **Análise:** O conector adversativo “contudo” foi trocado por “por isso”, alterando a relação lógica.

---

### 2.7 Modulação (MOD+)

**Descrição:**  
Mudança de ponto de vista, categoria ou voz (ativa ↔ passiva; afirmativa ↔ negativa).

**Critérios de Detecção:**

- Alteração de estrutura gramatical que **muda a perspectiva semântica**.

- Ex.: transformar um agente em paciente, ou substituir negação por afirmação.

- Pode ser identificado por análise de dependências sintáticas.

**Exemplo:**

- **Fonte:** “Antecedentes dos discursos patrióticos contemporâneos podem ser identificados [...]”

- **Simplificado:** “Hoje podemos identificar antecedentes dos discursos patrióticos [...]”

- **Análise:** Passiva (“podem ser identificados”) foi modulada para ativa (“podemos identificar”).

---

### 2.8 Deslocamento de Unidades Lexicais (DL+)

**Descrição:**  
Reorganização de palavras ou expressões, sem alteração de conteúdo, visando clareza e fluidez.

**Critérios de Detecção:**

- Palavras que mudam de posição sintática mantendo a mesma função.

- Mais comum em adjuntos adverbiais, qualificadores ou explicações.

**Exemplo:**

- **Fonte:** “Convergências e interseções inusitadas entre forças religiosas e setores militares.”

- **Simplificado:** “Algumas convergências e interseções, bastante inusitadas, entre forças religiosas e setores militares.”

- **Análise:** O qualificativo “inusitadas” foi deslocado de posição adjacente.

---

### 2.9 Explicação (EXP+)

**Descrição:**  
Acrescentar glossas, definições ou paráfrases para termos especializados ou pouco acessíveis.

**Critérios de Detecção:**

- Presença de equivalentes em forma expandida (ex.: “antissemitismo (discriminação de judeus)”).

- Normalmente introduzido por parênteses ou oração subordinada.

**Exemplo:**

- **Fonte:** “Episódios de violência cristianofóbica [...]”

- **Simplificado:** “Episódios de violência cristianofóbica ocorridos no Oriente Médio e na Ásia do Sul, onde cristãos são minoria.”

- **Análise:** Foi inserida explicação contextualizante (“onde cristãos são minoria”).

---

### 2.10 Mudança de Título (MT+)

**Descrição:**  
Alteração de subtítulos ou títulos de seções, geralmente para refletir cortes ou reorganização de conteúdo.

**Critérios de Detecção:**

- Diferença lexical nos títulos de seções correspondentes.

- Normalmente acompanhada de omissões ou fusões de conteúdo.

**Exemplo:**

- **Fonte:** “As raízes da palavra.”

- **Simplificado:** “A origem da palavra.”

- **Análise:** Título simplificado lexicalmente e mais direto.

---

## 3. Exceções (Fora do Escopo)

- **OM+ (Omissão Significativa)**: Embora seja crucial no processo, será tratado apenas como **anotação humana**, pois identificar cortes “significativos” exige julgamento interpretativo.

- **PRO+ (Problema)**: Etiqueta usada apenas para marcar **erros de tradução ou simplificação**. Não deve ser alvo de detecção automática.

---

## 4. Conclusão

Este documento constitui a referência única para o desenvolvimento do sistema de IA. Cada estratégia está definida com:

1. Nome canônico,

2. Definição teórica,

3. Critérios de detecção observáveis,

4. Exemplos empíricos alinhados (fonte/alvo).
