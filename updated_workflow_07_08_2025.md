# NET-EST: Simplification Strategy Analysis System – Workflow Specification

## 🧭 System Overview

The NET-EST system identifies and classifies simplification strategies in intralingual translations (Portuguese → Portuguese). It uses a neural language model to analyze discourse-level paragraph alignments and segment-level simplification, with validation from a human linguist (human-in-the-loop).

---

## ⚙️ Workflow Modules

### 1. Input Submission

- User submits:
  - **Source Text (ST)** and **Target Text (TT)**.
  - Input methods: text input or file upload (`.pdf`, `.docx`, `.odt`, `.md`, `.txt`).
- **Note**: TT is expected to contain ~65% of the ST word count, but no enforcement is applied.

---

### 2. Preprocessing & Validation

- System actions:
  - Word count for both texts.
  - Text segmentation:
    - **Paragraph** = discourse unit.
    - **Phrase** (`sintagma`) = analysis unit.
  - TT Reduction Index (%) calculated.

---

### 3. Semantic Alignment

- Uses `paraphrase-multilingual-MiniLM-L12-v2` to align ST and TT paragraphs.
- Confidence score computed for each alignment pair.

---

### 4. Feature Extraction

- System compares aligned paragraph pairs.
- Phrase-level changes analyzed to identify potential simplification events.
- Features extracted:
  - Lexical variation
  - Structural change
  - Length variation

---

### 5. Tag Classification

- Each detected simplification receives a **tag** from the system.
- Configuration:
  - Confidence threshold for tag insertion: **65%**.
  - Tags inserted as superscript at the **start of the simplified phrase** in TT.
- Overlapping strategies:
  - Tag with highest confidence shown.
  - Other detected tags stored and viewable via user dropdown.

---

### 6. Visualization & Editing

- ST and TT shown side-by-side with:
  - **Color-coded highlights** for each simplification strategy.
  - Superscript tags for quick identification.
- Editing tools for the human-in-the-loop:
  - Change, delete, or insert tags.
  - Visual color updates on tag change.

---

### 7. Report Generation

- User can generate:
  - Printable comparison view with color codes and superscripts.
  - Strategy frequency table.
  - Bar chart with:
    - TT reduction index
    - Strategy distribution

---

### 8. Feedback Loop

- All human edits logged.
- Feedback optionally submitted for:
  - Continuous learning
  - Improving detection accuracy
  - Future model training

---

## 🧩 Esquema de Tags de Estratégias de Simplificação Textual

| **Tag** | **Nome da Estratégia**               | **Descrição Funcional**                                                           |
| ------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| `AS+`   | Alteração de Sentido                 | Mudança de sentido por modulação, tolerada se não comprometer o núcleo semântico. |
| `DL+`   | Reorganização Posicional             | Mudança na ordem dos elementos para melhor fluxo.                                 |
| `EXP+`  | Explicitação e Detalhamento          | Adição de explicações, exemplos ou paráfrases.                                    |
| `IN+`   | Manejo de Inserções                  | Remoção ou reestruturação de elementos parentéticos.                              |
| `MOD+`  | Reinterpretação Perspectiva          | Adaptação semântica ao repertório do público.                                     |
| `MT+`   | Otimização de Títulos                | Reformulação ou criação de títulos mais claros e visíveis.                        |
| `OM+`   | Supressão Seletiva                   | Exclusão de conteúdo periférico ou redundante.                                    |
| `PRO+`  | Desvio Semântico e/ou Interpretativo | Marca problemas de interpretação. Uso exclusivo do agente humano.                 |
| `RF+`   | Reescrita Global                     | Reformulação ampla com múltiplas estratégias combinadas.                          |
| `RD+`   | Estruturação de Conteúdo e Fluxo     | Reorganização macroestrutural para manter coerência textual.                      |
| `RP+`   | Fragmentação Sintática               | Quebra de frases complexas em sentenças curtas.                                   |
| `SL+`   | Adequação de Vocabulário             | Substituição de termos difíceis por equivalentes mais simples.                    |
| `TA+`   | Clareza Referencial                  | Garantia de que pronomes e anáforas sejam facilmente compreensíveis.              |
| `MV+`   | Alteração da Voz Verbal              | Mudança entre voz ativa/passiva para maior clareza.                               |

---

### ⚠️ Regras Especiais

- **OM+ (Supressão Seletiva)**:
  
  - **Desativada por padrão**: simplificações sempre reduzem o número de palavras.
  - Pode ser **ativada manualmente** pelo agente humano se necessário.

- **PRO+ (Desvio Interpretativo)**:
  
  - **Nunca inserida automaticamente**.
  - Disponível no menu de contexto para o humano marcar erros interpretativos.

---

## 📊 Diagrama de Fluxo (Flowchart)

```mermaid
flowchart TD
    A[Início] --> B[Envio de ST e TT]
    B --> C[Pré-processamento e Validação]
    C --> D[Alinhamento Semântico (Parágrafos)]
    D --> E[Extração de Características (Sintagmas)]
    E --> F[Classificação e Marcação de Estratégias]
    F --> G[Exibição Interativa com Edição Humana]
    G --> H[Geração de Relatórios]
    H --> I[Registro de Feedback]
    I --> J[Fim]
```

---

## 🖥️ Deployment Architecture

- **Backend**: HuggingFace Spaces (`gradio`, `transformers`, `scikit-learn`, etc.)
- **Frontend**: Vercel or static React site
- **Integration**:
  - Model inference via API
  - State management with tag versioning
  - Context menus for tag editing

---

## 📌 Authors and Credits

**Projeto:** NET-EST  
**Coordenação:** Profa. Dra. Janine Pimentel  
**Desenvolvedor:** Wisley Vilela  
**Linguística:** Luanny Matos de Lima  
**Assistência Técnica (IA):** Claude 3.5, ChatGPT-4o, Gemini Flash  
**Instituições:** PIPGLA/UFRJ, Politécnico de Leiria
**Apoio:** CAPES (via bolsa de doutorado)
