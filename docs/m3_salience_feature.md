# Milestone M3: Saliência de Parágrafos e Sentenças

Esta fase introduz um provedor de saliência pluggable e integração opcional na saída hierárquica.

## Resumo
- Provedor: `SalienceProvider` (`backend/src/services/salience_provider.py`)
- Métodos suportados: `frequency` (sempre), `keybert` (se instalado), `yake` (se instalado)
- Normalização: valores de parágrafo normalizados globalmente; sentenças normalizadas localmente dentro de cada parágrafo
- Campos expostos: `paragraph.salience`, `sentence.salience`

## Flags de Requisição
```jsonc
{
  "hierarchical_output": true,
  "salience_method": "frequency", // opcional; frequency|keybert|yake
  "analysis_options": {
    "include_salience": true
  }
}
```

## Comportamento
1. Se `include_salience` for `false`, todos os campos de saliência retornam `null`.
2. Se método solicitado não estiver disponível (ex.: keybert sem dependência), fallback silencioso para `frequency`.
3. Peso de sentença = máx. dos pesos de unidades extraídas (palavras / n-gramas) naquele enunciado.
4. Peso de parágrafo = média dos pesos das unidades extraídas normalizada pelo maior valor entre parágrafos.

## Considerações de Desempenho
- Execução de saliência é O(n) em tokens; recomendada desativação em textos muito longos se latência for crítica.
- Possível melhoria futura: cache por sentença normalizada.

## Testes
- `test_salience_provider.py`: extrator base
- `test_salience_flags.py`: presença/ausência via flags

## Próximos Passos (Opcional)
- Cache de saliência por sentença (hash MD5) para reutilização entre parágrafos.
- Exposição visual (heatmap) no frontend utilizando gradiente baseado em `sentence.salience`.

---
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
