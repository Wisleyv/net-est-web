# Contribuindo para o NET-EST

Este guia resume os passos essenciais para configurar o ambiente de desenvolvimento isolado e executar os testes.

## 1. Clonar o Repositório
```
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web/backend
```

## 2. Criar e Ativar Ambiente Virtual (Backend)
Windows PowerShell:
```
python -m venv venv
./venv/Scripts/Activate.ps1
```
Linux/macOS:
```
python -m venv venv
source venv/bin/activate
```

## 3. Instalar Dependências
Runtime:
```
pip install -r requirements.txt
```
Desenvolvimento / Testes:
```
pip install -r requirements-dev.txt
```
Isso garante instalação local de pytest, pytest-asyncio e plugins associados (evite instalar globalmente para assegurar reprodutibilidade).

## 4. Executar Testes
Executar tudo:
```
pytest
```
Executar subset (ex.: hierarquia):
```
pytest -k hierarchical_output
```

## 5. Boas Práticas
* Nunca instalar libs de teste globalmente (fora do venv).
* Atualizar `requirements.in` / `requirements-dev.in` e usar `pip-compile` para travar versões.
* Rodar testes antes de abrir PR.
* Manter mensagens de commit claras (escopo + resumo curto).
* Evitar refactors grandes no mesmo PR de novas features.

## 5.1 Language Conventions (Política de Idioma)
To ensure consistency across the codebase and documentation:
* Technical assets (architecture docs, code comments, design docs, issue/PR templates, commit messages, test names) SHOULD be written in English.
* Portuguese (PT-BR / PT) MUST be used for: user-facing UI labels, strategy names (e.g., "Supressão Seletiva"), domain examples, linguistic heuristic explanations, and sample corpus fragments.
* When describing language-dependent rules, use an English explanation followed by a clearly delimited Portuguese example block.
* Strategy tags (AS+, OM+, SL+, etc.) retain original Portuguese semantics; do not translate tag identifiers.
* Avoid mixing languages inside the same sentence unless required for clarity; prefer: English paragraph → Portuguese example.
* New files: start with English section headings; append a short Portuguese note only if it adds domain clarity.
* Pull Requests touching documentation should confirm adherence to this section (add a checklist item if needed).

Example pattern:
```
English explanation: The sentence splitter handles abbreviations.
Exemplo (PT): "Dr. Silva chegou às 10h. Ele aguardou."
```

Rationale: maximizes accessibility for international contributors while preserving linguistic fidelity required for Portuguese simplification analysis.

## 6. Atualização de Dependências
Gerar lockfiles novamente (ex.: após adicionar lib em requirements.in):
```
pip install pip-tools
pip-compile requirements.in
pip-compile requirements-dev.in
```

## 7. Estrutura Relevante
```
backend/
  requirements.txt
  requirements-dev.txt
  src/
  tests/
frontend/
  package.json
docs/
```

## 8. Contato
Abra uma issue ou use Discussions no GitHub para dúvidas.

---
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
