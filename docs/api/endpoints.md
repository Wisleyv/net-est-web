# Documentação da API - NET-EST

## Endpoints Disponíveis - Foundation Layer

### Health Check

#### GET /api/health
Verifica o status básico da API.

**Response:**
```json
{
  "success": true,
  "message": "NET-EST API está funcionando",
  "timestamp": "2025-07-31T10:30:00.000Z",
  "version": "1.0.0",
  "status": "healthy",
  "uptime_seconds": 123.45
}
```

#### GET /api/status
Retorna informações detalhadas do sistema.

**Response:**
```json
{
  "api": {
    "name": "NET-EST API",
    "version": "1.0.0",
    "debug": true,
    "uptime_seconds": 123.45
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_total_gb": 16.0,
    "memory_used_gb": 8.5,
    "memory_percent": 53.1
  },
  "limits": {
    "max_words": 2000,
    "max_file_size_mb": 10
  },
  "models": {
    "bertimbau_model": "neuralmind/bert-base-portuguese-cased",
    "similarity_threshold": 0.5
  }
}
```

## Próximos Endpoints (Em Desenvolvimento)

### Preprocessador (Intervenção 2.1.2)
- `POST /api/v1/preprocess/text` - Processar entrada de texto
- `POST /api/v1/preprocess/file` - Processar arquivo
- `GET /api/v1/preprocess/formats` - Formatos suportados

### Alinhador Semântico (Intervenção 2.1.3)
- `POST /api/v1/align` - Alinhar textos semanticamente
- `GET /api/v1/align/config` - Configurações de alinhamento

### Classificador (Intervenções futuras)
- `POST /api/v1/classify` - Classificar estratégias
- `PUT /api/v1/feedback` - Enviar feedback

## Códigos de Status

- `200` - Sucesso
- `400` - Erro de validação
- `422` - Erro de dados
- `500` - Erro interno do servidor

## Formato de Erro Padrão

```json
{
  "success": false,
  "message": "Mensagem de erro",
  "error_type": "validation_error",
  "details": {
    "field": "Detalhes específicos"
  },
  "timestamp": "2025-07-31T10:30:00.000Z"
}
```
