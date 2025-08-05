# NET-est Backend - Estrutura Final Consolidada

## Autoria e Créditos do Projeto

**Projeto:** NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**
- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Tecnologias-Chave:**
- **Modelo de Linguagem:** `paraphrase-multilingual-MiniLM-L12-v2` (118MB)
- **Estratégia:** Detecção híbrida (ML semântico + heurísticas especializadas)
- **Performance:** Otimizado para análise de textos longos (até 50k caracteres)
- **Precisão Acadêmica:** Thresholds rigorosos para validação científica

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

## 📁 Estrutura Após Consolidação

```
backend/
├── src/                          # Código fonte principal
│   ├── __init__.py
│   ├── main.py                   # FastAPI app principal
│   ├── api/                      # Endpoints da API
│   ├── services/                 # Serviços de negócio
│   └── models/                   # Modelos de dados
│
├── tests/                        # Testes automatizados
│
├── venv/                         # Ambiente virtual Python
│
├── docs_dev/                     # Documentação de desenvolvimento
│   ├── README.md
│   ├── backend_windows_troubleshooting.md
│   ├── corrections_applied.md
│   └── project_structure.md      # Este arquivo
│
├── start_optimized.py            # 🚀 Script principal (RECOMENDADO)
├── start_optimized.bat           # 🚀 Batch principal (RECOMENDADO)
├── start_server.py               # 🔧 Script backup simples
├── start_backend.bat             # 🔧 Batch backup simples
├── diagnose_fixed.py             # 🔍 Diagnóstico do ambiente
│
├── requirements.txt              # Dependências principais
├── requirements-dev.txt          # Dependências de desenvolvimento
├── pytest.ini                   # Configuração de testes
├── Dockerfile                    # Container Docker
├── .env.example                  # Template de variáveis ambiente
└── .env                          # Variáveis ambiente (git ignored)
```

## 🚀 Scripts de Inicialização

### Recomendado (com fallback automático)
- **start_optimized.py**: Script Python com detecção automática de porta
- **start_optimized.bat**: Batch com verificações completas

### Backup (inicialização simples)
- **start_server.py**: Script Python simples, porta fixa 8000
- **start_backend.bat**: Batch simples, sem verificações extras

### Diagnóstico
- **diagnose_fixed.py**: Verifica ambiente, portas, dependências

## 🗑️ Arquivos Removidos na Consolidação

### Scripts Redundantes
- ✅ `main.py` (raiz) - Redundante com src/main.py
- ✅ `run_api.py` - Funcionalidade integrada em start_optimized.py
- ✅ `run_server.py` - Substituído por scripts otimizados
- ✅ `diagnose.py` - Versão antiga do diagnóstico
- ✅ `dev_config.py` - Configurações integradas no script principal

### Arquivos de Teste Temporários
- ✅ `test_alignment.json` - Dados de teste não mais necessários
- ✅ `test_alignment2.json` - Dados de teste não mais necessários  
- ✅ `test_alignment3.json` - Dados de teste não mais necessários
- ✅ `test_cleanup.py` - Script de teste temporário
- ✅ `test_pdf_fix.py` - Script de teste temporário

### Scripts Batch Redundantes
- ✅ `quick_start.bat` - Funcionalidade integrada em start_optimized.bat

### Cache e Temporários
- ✅ `__pycache__/` - Cache Python
- ✅ `__init__.py` (raiz) - Desnecessário no diretório raiz

## 📋 Como Usar

### Inicialização Recomendada
```bash
cd C:\net\backend
start_optimized.bat
```

### Inicialização Manual
```bash
cd C:\net\backend
.\venv\Scripts\activate
python start_optimized.py
```

### Diagnóstico
```bash
cd C:\net\backend
.\venv\Scripts\activate  
python diagnose_fixed.py
```

---
**Status:** ✅ Consolidação concluída
**Última atualização:** 31/07/2025
