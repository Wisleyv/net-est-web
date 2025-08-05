## Estratégias de Simplificação Textual: Integração e Detecção Computacional

### Fonte Canônica

Todas as estratégias de simplificação textual implementadas no sistema NET-EST devem seguir rigorosamente as definições, siglas e descrições presentes na [Tabela Simplificação Textual.md](../docs/Tabela%20Simplifica%C3%A7%C3%A3o%20Textual.md). Esta tabela é a referência única para o desenvolvimento, manutenção e validação dos métodos de detecção.

### Relacionamento entre Arquivos de Configuração e Implementação

- **Tabela Simplificação Textual.md:**  
  - Define as 14 estratégias, suas siglas, nomes e descrições funcionais.
  - Serve de base para a implementação dos métodos de detecção no backend.
  - O backend deve implementar métodos de detecção para cada estratégia e retornar os resultados na análise comparativa.
  - O frontend deve exibir todas as estratégias detectadas, conforme definido na tabela.

- **strategy_detector.py:**  
  - Implementa métodos de detecção para cada estratégia.
  - Utiliza BERTimbau para similaridade semântica onde aplicável.
  - Cada método deve mapear diretamente para uma estratégia da tabela.

- **comparative_analysis_service.py:**  
  - Responsável por orquestrar a análise comparativa e converter os resultados para o formato esperado pelo frontend.
  - Garante que os objetos retornados contenham sigla, nome, tipo, descrição e exemplos conforme a tabela.

- **Frontend:**  
  - Exibe as estratégias usando os nomes e descrições em português, conforme fornecido pelo backend.

- **Configuração de CORS/Portas:**  
  - Garante comunicação entre frontend e backend, independentemente das portas utilizadas.

### Abordagem Recomendada

1. **Referência Única:**  
   - Centralizar todas as definições de estratégias na tabela e garantir que o código utilize essas definições.

2. **Alinhamento dos Métodos de Detecção:**  
   - Implementar e revisar métodos para cada estratégia, utilizando BERTimbau e heurísticas apropriadas.

3. **Mapeamento Consistente:**  
   - Assegurar que o backend retorne os dados corretamente mapeados para o frontend.

4. **Validação e Testes:**  
   - Criar casos de teste para cada estratégia e validar a detecção.

5. **Atualização da Documentação:**  
   - Documentar o fluxo de dados, mapeamento e lógica de detecção para facilitar futuras manutenções e melhorias.

### Observações

- As tags OM+ e PRO+ possuem regras especiais de uso, conforme descrito na tabela.
- Qualquer alteração nas estratégias deve ser refletida na tabela e nos métodos de detecção correspondentes.

---

**Última revisão:** 04/08/2025
