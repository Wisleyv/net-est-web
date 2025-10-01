# Backend FastAPI - Windows Troubleshooting & Definitive Solution

## Problemas Comuns

### 1. Erro de Permissão de Porta ([WinError 10013])
- Sintoma: Ao iniciar o backend com Uvicorn, aparece `[WinError 10013] Foi feita uma tentativa de acesso a um soquete de uma maneira que é proibida pelas permissões de acesso`.
- Causa: Porta bloqueada por firewall, antivírus, VPN, proxy ou políticas de segurança. Uso de `0.0.0.0` pode exigir permissões administrativas.

### 2. Problemas de Importação Relativa
- Sintoma: `attempted relative import with no known parent package`.
- Causa: Python não reconhece o diretório `src` como pacote raiz se o diretório de trabalho não está correto. Manipulação de `sys.path` e `os.chdir` pode confundir o Python.

### 3. Comunicação Frontend-Backend
- Sintoma: `ERR_CONNECTION_REFUSED` e status "Erro desconhecido" no frontend.
- Causa: Frontend configurado para porta errada ou backend inacessível.

### 4. Execução de Scripts no Windows
- Sintoma: Scripts `.bat` e PowerShell não iniciam o servidor corretamente.
- Causa: Falta de permissões administrativas, ambiente virtual não ativado, conflitos de PATH.

---

## Solução Definitiva

### A. Padronização de Porta e Host
- Use sempre `127.0.0.1` como host (localhost).
- Use a porta `8000` (ou outra livre).

### B. Correção dos Imports e Estrutura
- Mantenha o diretório de trabalho como raiz do projeto (`c:\net\backend`).
- Evite manipular `sys.path` e `os.chdir` no script de inicialização.
- Execute Uvicorn diretamente apontando para o módulo principal (`src.main:app`).

### C. Scripts de Inicialização
- Batch File:
  ```bat
  @echo off
  cd /d "C:\net\backend"
  call .\venv\Scripts\activate.bat
  python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
  pause
  ```
- Evite mudar o diretório de trabalho para `src`.

### D. Atualização do Frontend
- Todos os endpoints do frontend devem apontar para `http://localhost:8000`.

### E. Permissões e Ambiente
- Execute o terminal como administrador se necessário.
- Garanta que o ambiente virtual está ativado.

### F. Teste de Porta
- Antes de iniciar o servidor, teste se a porta está livre:
  ```python
  import socket; s = socket.socket(); s.bind(('127.0.0.1', 8000)); print('✅ Porta 8000 disponivel'); s.close()
  ```

---

## Checklist Final
- [x] Porta e host padronizados (`127.0.0.1:8000`)
- [x] Imports corrigidos (sem manipulação de path)
- [x] Scripts de inicialização simples e diretos
- [x] Frontend atualizado para nova porta
- [x] Ambiente virtual ativado corretamente
- [x] Teste de porta antes de iniciar

---

## Diagnóstico Rápido
Se ainda houver problemas:
- Inicie o backend manualmente:
  ```powershell
  cd C:\net\backend
  .\venv\Scripts\activate
  python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- Se aparecer `[WinError 10013]`, tente outra porta (ex: 8080).
- Verifique se o firewall ou antivírus está bloqueando o Python/Uvicorn.
- Use `netstat -ano | findstr :8000` para garantir que a porta está livre.

---

**Essas recomendações garantem um ambiente de desenvolvimento estável para FastAPI + React no Windows.**

---

## Correções Aplicadas

### Scripts Corrigidos
- **start_server.py**: Removida manipulação de `sys.path` e `os.chdir`, implementação simplificada
- **start_optimized.py**: Versão otimizada com detecção automática de porta e configurações centralizadas
- **start_backend.bat**: Implementa teste de porta e fallback automático
- **diagnose_fixed.py**: Script de diagnóstico abrangente do ambiente

### Configurações Centralizadas
- **dev_config.py**: Arquivo de configuração central para padronizar host, porta e caminhos
- Padronização de `127.0.0.1:8000` com fallback para `8080`
- URLs do frontend automaticamente sincronizadas

### Melhorias Implementadas
- ✅ Teste automático de disponibilidade de porta
- ✅ Fallback inteligente para porta alternativa  
- ✅ Verificação de dependências antes da inicialização
- ✅ Diagnóstico abrangente do ambiente
- ✅ Tratamento robusto de erros com referência à documentação

### Scripts Disponíveis
- `start_optimized.bat`: Inicialização com verificações completas ⭐ **PRINCIPAL**
- `start_optimized.py`: Script Python otimizado ⭐ **PRINCIPAL**
- `start_backend.bat`: Batch backup simples
- `start_server.py`: Script Python backup simples  
- `diagnose_fixed.py`: Diagnóstico completo do ambiente

### Integração com VS Code (tasks.json)
- A tarefa **Start Backend Server** do VS Code executa `scripts/process/start-backend.ps1`, que invoca `backend/start_optimized.py`. Portanto, iniciar pelo atalho do VS Code ou pelo comando manual `python -X utf8 backend\start_optimized.py` aciona o mesmo backend consolidado.
- Se a saída indicar `⚠️  Porta 8000 ocupada, usando 8080`, significa que um processo órfão reteve a porta principal. Use as tarefas **Stop Backend Server** ou **Stop All Servers** para encerrá-lo, e, se necessário, rode `Inspect Ports` ou `List Backend Processes` para localizar o PID antes de tentar de novo.
- Para depuração com log persistente, execute manualmente:
  ```powershell
  python -X utf8 backend\start_optimized.py 2>&1 | Tee-Object -FilePath backend\upload_debug.log
  ```
  Esse comando é compatível com a tarefa e garante logs UTF-8 sem perdas de caracteres quando precisar anexar evidências.
- Confirme que o backend correto respondeu procurando linhas como `Processing file upload` e `Comparative analysis completed` na saída (ou no arquivo de log). A ausência dessas linhas sugere que o fluxo HTTP não chegou ao endpoint esperado.

#### Tratamento para processos "fantasmas" do Uvicorn
- O `start_optimized.py` roda o Uvicorn com `reload=True`. Nessa configuração o WatchFiles cria **dois** processos: o *reloader* (exibe `Started reloader process [PID]`) e o *server worker* (exibe `Started server process [PID]`). Apenas o worker escuta na porta 8000; se ele for morto sozinho o reloader imediatamente cria outro worker, mantendo a porta ocupada.
- O script `kill_backend_8000.ps1` foi atualizado para:
  - Descobrir o worker escutando na porta 8000 e percorrer a cadeia de processos pais (`watchfiles`, `uvicorn`, `start_optimized`),
  - Encerrar os pais primeiro (impedindo respawns) e depois o worker,
  - Validar se a porta foi liberada; se não, avisar explicitamente para usar o Gerenciador de Tarefas.
- Caso você tenha sessões Python adicionais (ex.: notebooks ou depuradores) que também executam `uvicorn` ou `watchfiles`, eles serão listados no processo pai. Confirme o comando exibido antes de aceitar o encerramento.

---

## ✅ Consolidação Final Aplicada

### Arquivos Mantidos (Essenciais)
- **start_optimized.py**: Script principal com fallback automático de porta
- **start_optimized.bat**: Batch principal com verificações completas
- **start_server.py**: Script backup simples (porta fixa 8000)
- **start_backend.bat**: Batch backup simples
- **diagnose_fixed.py**: Diagnóstico consolidado do ambiente

### Arquivos Removidos (Redundantes)
- Scripts: `main.py`, `run_api.py`, `run_server.py`, `diagnose.py`, `dev_config.py`
- Testes: `test_*.py`, `test_*.json` (temporários)
- Batch: `quick_start.bat`
- Cache: `__pycache__/`, `__init__.py` (raiz)

### Estrutura Final Limpa
```
backend/
├── src/                    # Código fonte
├── tests/                  # Testes oficiais
├── venv/                   # Ambiente virtual
├── start_optimized.py      # 🚀 PRINCIPAL
├── start_optimized.bat     # 🚀 PRINCIPAL  
├── start_server.py         # 🔧 Backup
├── start_backend.bat       # 🔧 Backup
├── diagnose_fixed.py       # 🔍 Diagnóstico
└── requirements.txt        # Dependências
```

## Plano de acompanhamento
- **Monitoramento**: após executar `Stop Backend Server` ou `Stop All Servers`, observe a saída do `kill_backend_8000.ps1`. Caso ainda haja PIDs escutando na porta, abra o Gerenciador de Tarefas (`Ctrl+Shift+Esc`) e finalize manualmente qualquer `python.exe` cujo comando exibido contenha `uvicorn`, `watchfiles` ou `src.main:app`.
- **Automação**: se o hot reload não for imprescindível na sessão atual, considere definir `RELOAD=False` via `.env` ou `Settings`. Isso evita o processo reloader e reduz a chance de retenção da porta 8000.
- **Telemetria leve**: planeje um hook futuro (por exemplo, log estruturado ao término do `kill_backend_8000.ps1`) para registrar quando processos órfãos forem encontrados, facilitando a identificação de padrões ou conflitos com depuradores externos.
- **Revisão periódica**: inclua a checagem dos scripts `start-backend.ps1` e `kill_backend_8000.ps1` na governança de releases; qualquer mudança no `start_optimized.py` deve ser refletida neles para manter o comportamento sincronizado.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
