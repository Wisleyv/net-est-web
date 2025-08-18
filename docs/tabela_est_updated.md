# Tabela de Estratégias de Simplificação Textual

## Autoria e Créditos do Projeto

**Projeto:** NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**

- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

**Apoio:** CAPES (via bolsa de doutorado)

---

### 🧩 **Tabela de Estratégias de Simplificação Textual**

| **Sigla** | **Nome Descritivo**                  | **Descrição Funcional**                                                                                                                                                                                                        |
| --------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **AS+**   | Alteração de Sentido                 | Embora não seja usada como estratégia intencional, pode ocorrer como resultado de modulações, ao expressar a mesma ideia por outro ponto de vista. Pode ser tolerada se não comprometer o sentido essencial do texto original. |
| **DL+**   | Reorganização Posicional             | Mudança na ordem dos elementos na frase para melhorar o fluxo da informação. Inclui extraposição, antecipação e movimentação de inserções ou tópicos para facilitar a leitura.                                                 |
| **EXP+**  | Explicitação e Detalhamento          | Adição de informações, exemplos ou paráfrases para esclarecer conteúdos implícitos ou complexos. Ajuda o leitor a compreender conceitos que exigiriam conhecimento prévio.                                                     |
| **IN+**   | Manejo de Inserções                  | Eliminação, deslocamento ou reestruturação de inserções que atrapalham a fluidez da sentença. Pode incluir repetição de elementos para manter a coesão em textos falados ou escritos.                                          |
| **MOD+**  | Reinterpretação Perspectiva          | Reformulação semântica para adaptar o conteúdo ao repertório do público. Inclui substituição de metáforas, expressões idiomáticas e construções figurativas por formas mais diretas.                                           |
| **MT+**   | Otimização de Títulos                | Reformulação ou criação de títulos que tornem o conteúdo mais visível, explícito e tematicamente alinhado ao público-alvo.                                                                                                     |
| **OM+**   | Supressão Seletiva                   | Exclusão de elementos redundantes, ambíguos, idiomáticos ou periféricos que não comprometem o núcleo do conteúdo e atrapalham a compreensão.                                                                                   |
| **PRO+**  | Desvio Semântico e/ou Interpretativo | Tag usada para anotação de problemas tradutórios de interpretação textual.                                                                                                                                                     |
| **RF+**   | Reescrita Global                     | Estratégia abrangente que integra múltiplos procedimentos de simplificação (lexical, sintática, discursiva). Visa à reformulação integral do texto para otimizar sua acessibilidade.                                           |
| **RD+**   | Estruturação de Conteúdo e Fluxo     | Reorganização macroestrutural do texto (sequência temática, paragrafação, uso de conectivos) para manter coerência, continuidade e progressão textual.                                                                         |
| **RP+**   | Fragmentação Sintática               | Divisão de períodos extensos ou complexos em sentenças mais curtas e diretas, facilitando o processamento por parte de leitores com menor fluência.                                                                            |
| **SL+**   | Adequação de Vocabulário             | Substituição de termos difíceis, técnicos ou raros por sinônimos mais simples, comuns ou hiperônimos. Também envolve evitar polissemia, jargões e repetições desnecessárias.                                                   |
| **TA+**   | Clareza Referencial                  | Estratégias para garantir que pronomes e outras referências anafóricas sejam facilmente compreendidos. Inclui evitar catáforas e uso de sinônimos distantes ou ambíguos.                                                       |
| **MV+**   | Alteração da Voz Verbal              | Mudança da voz passiva para ativa (ou vice-versa) para garantir maior clareza, fluência e naturalidade. A escolha depende da necessidade de destacar ou omitir agentes.                                                        |

-------------------------------------------------------------------------------------------------------

---

Usos especiais: As tags OM+ e PRO+ seguem regras de uso distantas, conforme instrução abaixo:

OM+ - Por padrão, a análise dessa estratégia de simplificação permanece desativada. Visto que a tradução intralingual com objetivo de simplificação textual invariavelmente implica redução no número de palavras, OM+ sempre ocorrerá. Essa tag ficará disponível para ativação pelo humano no circuito de análise, caso este julgue necessária a implementação dela em circunstâncias específicas.

PRO+ - Essa tag nunca será marcada pelo sistema computacional de análise. Ela permanecerá disponível em um menu de contexto, ativo na caixa do "Texto Alvo", permitindo ao humano no circuito que a selecione para marcar ocorrências específicas.

Todas as tags estarão disponíveis em um menu de contexto na caixa "Texto Alvo" para alteração de tag pelo humano no circuito. As alterações efetuadas pelo agente humano serão armazenadas com o objetivo de refinar os métodos de análise computacional.
