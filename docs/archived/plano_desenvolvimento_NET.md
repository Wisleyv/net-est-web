# Plano de Desenvolvimento para o NET – Análise de Tradução Intralinguística

## Autoria e Créditos do Projeto

**Projeto:** NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**
- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)

**Financiamento:** Bolsa de Doutorado CAPES (Coordenação de Aperfeiçoamento de Pessoal de Nível Superior)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

**Licença:** MIT License | **Repositório:** GitHub (código aberto)

*Para informações detalhadas sobre autoria e contribuições, consulte [AUTORIA_E_CREDITOS.md](./AUTORIA_E_CREDITOS.md)*

---

## 1. Organização Inicial do Projeto

### 1.1. Definição de Stack Tecnológica
- **Backend:** Python (FastAPI), SentenceTransformers (BERTimbau), spaCy, SQLite (inicialmente), Docker.
- **Frontend:** React (ou Vue), consumo via REST API, design responsivo.
- **Infraestrutura:** Hugging Face Spaces (backend), Vercel/Netlify (frontend), banco externo (Neon/Supabase) para feedback.

### 1.2. Estrutura de Repositório
- Monorepo com subpastas `/backend` e `/frontend`.
- Documentação em `/docs`.
- Scripts de build e deploy automatizados.

### 1.3. Controle de Versão e Integração Contínua
- GitHub como repositório central.
- Workflows de CI para lint, testes e build.
- Deploy automático para ambientes de staging.

---

## 2. Fase de Implementação Modular

### 2.1. Módulo 1 – Pré-processador
- Implementar UI com abas "Digitar Texto" e "Carregar Arquivo".
- Handlers para `.txt`, `.md`, `.docx`, `.odt`, `.pdf` (usar textract se possível).
- Validação de volume e aviso amigável para textos longos.
- Output: `source_text` e `target_text` limpos.

### 2.2. Módulo 2 – Alinhador Semântico
- Segmentação em parágrafos.
- Embeddings com BERTimbau.
- Matriz de similaridade e alinhamento com limiar configurável.
- Output: JSON com `aligned_pairs` e `unaligned_source_indices`.

### 2.3. Módulo 3 – Extrator/Classificador
- Receber `alignment_data` e `user_config`.
- Extrair features discursivas e lexicais (usar spaCy/TF-IDF).
- Motor de regras heurísticas ponderado por configuração do usuário.
- Garantir que `[PRO+]` nunca seja gerada automaticamente.
- Output: `annotated_data` (lista de anotações).

### 2.4. Módulo 4 – UI Interativa
- Renderização paralela dos textos, realce por cor, tags editáveis.
- Tabela detalhada de anotações.
- Menu de contexto para edição de tags.
- Integração com Módulo 5 para envio de feedback.

### 2.5. Módulo 5 – Coletor de Feedback
- API REST para receber correções do usuário.
- Persistência inicial em SQLite; preparar integração futura com banco externo.
- Estrutura de dados para fácil exportação e uso em treinamento futuro.

### 2.6. Módulo 6 – Gerador de Relatórios
- Função de exportação (Markdown, CSV, DOCX, PDF via pypandoc).
- Relatórios sintético e analítico.
- UI com opções de formato.

---

## 3. Fluxo de Desenvolvimento Recomendado

1. **Kickoff:** Definir requisitos mínimos viáveis (MVP) e milestones.
2. **Implementar Módulos 1 e 2:** Garantir alinhamento robusto de parágrafos.
3. **Desenvolver Módulo 3 (backend) e Módulo 4 (frontend) em paralelo:** Usar dados simulados para UI.
4. **Integrar Módulo 5 assim que a UI estiver funcional:** Começar a coletar feedback real o quanto antes.
5. **Adicionar Módulo 6 (relatórios) após validação dos fluxos principais.**
6. **Testes de usabilidade e refinamento contínuo com usuários reais.**
7. **Preparar scripts de build e deploy para Hugging Face Spaces e Vercel/Netlify.**
8. **Documentar endpoints, fluxos e decisões técnicas.**

---

## 4. Boas Práticas e Garantias de Consistência

- **Modularidade:** Cada módulo deve ser testável e substituível.
- **Versionamento de API:** Planejar para evolução sem breaking changes.
- **Configuração via variáveis de ambiente:** URLs, limiares, etc.
- **Logs e monitoramento:** Registrar erros e feedbacks para análise posterior.
- **Transparência:** Explicar decisões do classificador na UI.
- **Feedback Loop:** Valorizar e versionar dados de correção do usuário.

---

## 5. Usabilidade e Evolução

- **Mensagens claras para o usuário (ex: cold start, textos longos).**
- **Interface intuitiva, responsiva e acessível.**
- **Facilidade de exportação e integração futura com modelos de ML.**
- **Planejar migração do banco de feedback para solução persistente assim que necessário.**

---

## 6. Próximos Passos

1. Montar repositório e estrutura inicial.
2. Definir contratos de dados (JSON) entre módulos.
3. Implementar MVP dos Módulos 1 e 2.
4. Validar fluxo de alinhamento com casos reais.
5. Iterar conforme feedback dos usuários e equipe.

---

Este plano garante desenvolvimento incremental, modular e sustentável, minimizando retrabalho e maximizando a qualidade e usabilidade do sistema.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
