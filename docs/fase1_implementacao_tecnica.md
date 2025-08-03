# NET-EST - Primeira Fase de Implementação Técnica

## Autoria e Créditos do Projeto

**Projeto:** NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**
- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PPGLEN/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

**Financiamento:** Bolsa de Doutorado CAPES (Coordenação de Aperfeiçoamento de Pessoal de Nível Superior)

**Licença:** MIT License | **Repositório:** GitHub (código aberto)

*Para informações detalhadas sobre autoria e contribuições, consulte [AUTORIA_E_CREDITOS.md](./AUTORIA_E_CREDITOS.md)*

---

**Desenvolvedor Principal:** Wisley Vilela  
**Data:** 31 de Julho de 2025  
**Versão:** 1.0

---

## Análise Comparativa dos Documentos Base

### Convergência de Requisitos

Após análise comparativa entre `plano_desenvolvimento_NET.md` e `proposta_arquitetura_algoritmo.md`, identifiquei total alinhamento nos seguintes aspectos críticos:

1. **Arquitetura Modular:** Ambos documentos enfatizam a modularidade como pilar fundamental
2. **Foco no Discurso:** Análise no nível de parágrafo, não sentença
3. **Human-in-the-Loop:** Controle humano sobre validação e correções
4. **Priorização dos Módulos 1 e 2:** Base fundamental para todo o sistema
5. **Stack Tecnológica:** Python/FastAPI + React/Vue + BERTimbau

### Discrepâncias e Decisões Técnicas

- **Hospedagem:** Proposta arquitetural detalha Hugging Face Spaces; plano básico sugere alternativas
- **Banco de Dados:** Proposta especifica SQLite → PostgreSQL; plano menciona Neon/Supabase
- **Timeline:** Proposta é mais prescritiva; plano é mais flexível

---

## FASE 1: Fundação Técnica (Módulos 1 e 2)

### Objetivo da Fase 1
Estabelecer a base sólida do sistema com capacidade de entrada de dados e alinhamento semântico robusto entre textos fonte e alvo.

---

## Passo 1: Configuração do Ambiente de Desenvolvimento

### 1.1 Estrutura de Repositório
```
net-est/
├── backend/
│   ├── src/
│   │   ├── modules/
│   │   │   ├── preprocessor.py
│   │   │   ├── semantic_aligner.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── docs/
├── .github/workflows/
└── README.md
```

### 1.2 Configuração de Dependências (Backend)

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
sentence-transformers==2.2.2
spacy==3.7.2
python-docx==0.8.11
PyPDF2==3.0.1
pdfminer.six==20221105
textract==1.6.5
numpy==1.24.3
scikit-learn==1.3.0
pandas==2.1.1
pydantic==2.4.2
python-dotenv==1.0.0
fastapi-cors==0.0.6
pytest==7.4.2
```

### 1.3 Configuração Inicial do Backend

**main.py:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.modules.preprocessor import PreprocessorModule
from src.modules.semantic_aligner import SemanticAlignerModule
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="NET-EST API", version="1.0.0")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias dos módulos
preprocessor = PreprocessorModule()
aligner = SemanticAlignerModule()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## Passo 2: Implementação do Módulo 1 - Pré-processador

### 2.1 Especificação Técnica Detalhada

**Contratos de Entrada e Saída:**
```python
from pydantic import BaseModel
from typing import Optional, Union
from enum import Enum

class InputType(str, Enum):
    TEXT = "text"
    FILE = "file"

class TextInput(BaseModel):
    source_text: str
    target_text: str
    input_type: InputType = InputType.TEXT

class FileInput(BaseModel):
    source_file: bytes
    target_file: bytes
    source_filename: str
    target_filename: str
    input_type: InputType = InputType.FILE

class PreprocessorOutput(BaseModel):
    source_text: str
    target_text: str
    source_word_count: int
    target_word_count: int
    warnings: list[str] = []
    processing_time: float
```

### 2.2 Implementação do Preprocessor

**src/modules/preprocessor.py:**
```python
import time
import re
from typing import Tuple, List
import textract
from io import BytesIO
import magic

class PreprocessorModule:
    
    WORD_LIMIT = 2000
    SUPPORTED_FORMATS = ['.txt', '.md', '.docx', '.odt', '.pdf']
    
    def __init__(self):
        self.mime_types = {
            'text/plain': self._extract_text,
            'text/markdown': self._extract_text,
            'application/pdf': self._extract_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._extract_docx,
            'application/vnd.oasis.opendocument.text': self._extract_odt
        }
    
    async def process_text_input(self, source_text: str, target_text: str) -> PreprocessorOutput:
        """Processa entrada de texto direto"""
        start_time = time.time()
        
        # Limpeza básica de texto
        clean_source = self._clean_text(source_text)
        clean_target = self._clean_text(target_text)
        
        # Contagem de palavras
        source_words = self._count_words(clean_source)
        target_words = self._count_words(clean_target)
        
        # Validações e avisos
        warnings = []
        if source_words > self.WORD_LIMIT:
            warnings.append(
                f"Atenção: texto-fonte com {source_words} palavras pode gerar "
                "um grande volume de anotações e levar mais tempo para análise."
            )
        
        processing_time = time.time() - start_time
        
        return PreprocessorOutput(
            source_text=clean_source,
            target_text=clean_target,
            source_word_count=source_words,
            target_word_count=target_words,
            warnings=warnings,
            processing_time=processing_time
        )
    
    async def process_file_input(self, source_file: bytes, target_file: bytes, 
                               source_filename: str, target_filename: str) -> PreprocessorOutput:
        """Processa entrada de arquivos"""
        start_time = time.time()
        
        # Detectar tipo MIME
        source_mime = magic.from_buffer(source_file, mime=True)
        target_mime = magic.from_buffer(target_file, mime=True)
        
        # Extrair texto
        source_text = await self._extract_text_from_file(source_file, source_mime)
        target_text = await self._extract_text_from_file(target_file, target_mime)
        
        # Delegar para processamento de texto
        result = await self.process_text_input(source_text, target_text)
        result.processing_time = time.time() - start_time
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Limpeza e normalização de texto"""
        # Remove excesso de espaços em branco
        text = re.sub(r'\s+', ' ', text)
        # Remove quebras de linha excessivas
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()
    
    def _count_words(self, text: str) -> int:
        """Contagem precisa de palavras"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    async def _extract_text_from_file(self, file_bytes: bytes, mime_type: str) -> str:
        """Extrai texto baseado no tipo MIME"""
        if mime_type in self.mime_types:
            return self.mime_types[mime_type](file_bytes)
        else:
            # Fallback para textract (universal)
            return textract.process(BytesIO(file_bytes)).decode('utf-8')
    
    def _extract_text(self, file_bytes: bytes) -> str:
        """Extrai texto simples"""
        return file_bytes.decode('utf-8', errors='ignore')
    
    def _extract_pdf(self, file_bytes: bytes) -> str:
        """Extrai texto de PDF usando textract"""
        return textract.process(BytesIO(file_bytes)).decode('utf-8')
    
    def _extract_docx(self, file_bytes: bytes) -> str:
        """Extrai texto de DOCX usando textract"""
        return textract.process(BytesIO(file_bytes)).decode('utf-8')
    
    def _extract_odt(self, file_bytes: bytes) -> str:
        """Extrai texto de ODT usando textract"""
        return textract.process(BytesIO(file_bytes)).decode('utf-8')
```

---

## Passo 3: Implementação do Módulo 2 - Alinhador Semântico

### 3.1 Especificação Técnica Detalhada

**Contratos de Dados:**
```python
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np

class AlignmentPair(BaseModel):
    source_idx: int
    target_idx: int
    similarity_score: float
    source_text: str
    target_text: str

class AlignmentData(BaseModel):
    aligned_pairs: List[AlignmentPair]
    unaligned_source_indices: List[int]
    unaligned_source_texts: List[str]
    similarity_matrix: List[List[float]]
    processing_time: float
    threshold_used: float

class AlignerConfig(BaseModel):
    similarity_threshold: float = 0.5
    model_name: str = "neuralmind/bert-base-portuguese-cased"
    max_length: int = 512
```

### 3.2 Implementação do Alinhador Semântico

**src/modules/semantic_aligner.py:**
```python
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Any
import re

class SemanticAlignerModule:
    
    def __init__(self, model_name: str = "neuralmind/bert-base-portuguese-cased"):
        """Inicializa o alinhador com modelo BERTimbau"""
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        
    async def align_paragraphs(self, source_text: str, target_text: str, 
                             threshold: float = 0.5) -> AlignmentData:
        """Alinha parágrafos entre texto fonte e alvo"""
        start_time = time.time()
        
        # Segmentação em parágrafos
        source_paragraphs = self._segment_paragraphs(source_text)
        target_paragraphs = self._segment_paragraphs(target_text)
        
        # Validação básica
        if not source_paragraphs or not target_paragraphs:
            raise ValueError("Textos devem conter pelo menos um parágrafo")
        
        # Geração de embeddings
        source_embeddings = self.model.encode(source_paragraphs)
        target_embeddings = self.model.encode(target_paragraphs)
        
        # Matriz de similaridade
        similarity_matrix = cosine_similarity(source_embeddings, target_embeddings)
        
        # Processo de alinhamento
        aligned_pairs, unaligned_indices = self._perform_alignment(
            source_paragraphs, target_paragraphs, similarity_matrix, threshold
        )
        
        # Textos não alinhados
        unaligned_texts = [source_paragraphs[i] for i in unaligned_indices]
        
        processing_time = time.time() - start_time
        
        return AlignmentData(
            aligned_pairs=aligned_pairs,
            unaligned_source_indices=unaligned_indices,
            unaligned_source_texts=unaligned_texts,
            similarity_matrix=similarity_matrix.tolist(),
            processing_time=processing_time,
            threshold_used=threshold
        )
    
    def _segment_paragraphs(self, text: str) -> List[str]:
        """Segmenta texto em parágrafos"""
        # Split por dupla quebra de linha
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        # Filtrar parágrafos muito curtos (menos de 10 caracteres)
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 10]
        
        return paragraphs
    
    def _perform_alignment(self, source_paragraphs: List[str], 
                          target_paragraphs: List[str],
                          similarity_matrix: np.ndarray, 
                          threshold: float) -> Tuple[List[AlignmentPair], List[int]]:
        """Executa o alinhamento baseado na matriz de similaridade"""
        
        aligned_pairs = []
        used_target_indices = set()
        unaligned_source_indices = []
        
        for source_idx, source_text in enumerate(source_paragraphs):
            # Encontrar melhor match no alvo
            best_target_idx = -1
            best_score = -1
            
            for target_idx in range(len(target_paragraphs)):
                if target_idx in used_target_indices:
                    continue
                    
                score = similarity_matrix[source_idx][target_idx]
                if score > best_score:
                    best_score = score
                    best_target_idx = target_idx
            
            # Verificar se passa no threshold
            if best_score >= threshold and best_target_idx != -1:
                aligned_pairs.append(AlignmentPair(
                    source_idx=source_idx,
                    target_idx=best_target_idx,
                    similarity_score=float(best_score),
                    source_text=source_text,
                    target_text=target_paragraphs[best_target_idx]
                ))
                used_target_indices.add(best_target_idx)
            else:
                unaligned_source_indices.append(source_idx)
        
        return aligned_pairs, unaligned_source_indices
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo carregado"""
        return {
            "model_name": self.model_name,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'N/A'),
            "embedding_dimension": self.model.get_sentence_embedding_dimension()
        }
```

---

## Passo 4: API Endpoints para Fase 1

### 4.1 Endpoints Implementados

**Adições ao main.py:**
```python
from fastapi import UploadFile, File, Form
from src.modules.preprocessor import PreprocessorModule, PreprocessorOutput
from src.modules.semantic_aligner import SemanticAlignerModule, AlignmentData, AlignerConfig

# Endpoints do Módulo 1
@app.post("/api/v1/preprocess/text", response_model=PreprocessorOutput)
async def preprocess_text(source_text: str = Form(...), target_text: str = Form(...)):
    """Processa entrada de texto direto"""
    try:
        result = await preprocessor.process_text_input(source_text, target_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/preprocess/files", response_model=PreprocessorOutput)
async def preprocess_files(
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...)
):
    """Processa entrada de arquivos"""
    try:
        source_content = await source_file.read()
        target_content = await target_file.read()
        
        result = await preprocessor.process_file_input(
            source_content, target_content,
            source_file.filename, target_file.filename
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints do Módulo 2
@app.post("/api/v1/align", response_model=AlignmentData)
async def align_paragraphs(
    source_text: str = Form(...),
    target_text: str = Form(...),
    threshold: float = Form(0.5)
):
    """Alinha parágrafos semanticamente"""
    try:
        result = await aligner.align_paragraphs(source_text, target_text, threshold)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/model-info")
async def get_model_info():
    """Retorna informações sobre o modelo carregado"""
    return aligner.get_model_info()

# Pipeline completa Fase 1
@app.post("/api/v1/process-complete")
async def process_complete_pipeline(
    source_text: str = Form(None),
    target_text: str = Form(None),
    source_file: UploadFile = File(None),
    target_file: UploadFile = File(None),
    threshold: float = Form(0.5)
):
    """Pipeline completa: pré-processamento + alinhamento"""
    try:
        # Determinar tipo de entrada
        if source_text and target_text:
            preprocessed = await preprocessor.process_text_input(source_text, target_text)
        elif source_file and target_file:
            source_content = await source_file.read()
            target_content = await target_file.read()
            preprocessed = await preprocessor.process_file_input(
                source_content, target_content,
                source_file.filename, target_file.filename
            )
        else:
            raise HTTPException(status_code=400, detail="Deve fornecer textos ou arquivos")
        
        # Alinhamento semântico
        alignment = await aligner.align_paragraphs(
            preprocessed.source_text, 
            preprocessed.target_text, 
            threshold
        )
        
        return {
            "preprocessing": preprocessed,
            "alignment": alignment,
            "pipeline_status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Passo 5: Frontend Básico para Teste

### 5.1 Estrutura Frontend Mínima

**package.json:**
```json
{
  "name": "net-est-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@vitejs/plugin-react": "^4.0.3",
    "vite": "^4.4.5"
  }
}
```

### 5.2 Componente de Teste Principal

**src/App.jsx:**
```jsx
import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [sourceText, setSourceText] = useState('');
  const [targetText, setTargetText] = useState('');
  const [threshold, setThreshold] = useState(0.5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleProcess = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('source_text', sourceText);
      formData.append('target_text', targetText);
      formData.append('threshold', threshold);
      
      const response = await axios.post(`${API_BASE_URL}/api/v1/process-complete`, formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro no processamento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>NET-EST - Teste Fase 1</h1>
      
      <div className="input-section">
        <div className="text-inputs">
          <div>
            <label>Texto Fonte:</label>
            <textarea 
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              rows={10}
              cols={50}
              placeholder="Cole aqui o texto fonte..."
            />
          </div>
          
          <div>
            <label>Texto Alvo:</label>
            <textarea 
              value={targetText}
              onChange={(e) => setTargetText(e.target.value)}
              rows={10}
              cols={50}
              placeholder="Cole aqui o texto alvo..."
            />
          </div>
        </div>
        
        <div className="controls">
          <label>
            Limiar de Similaridade: 
            <input 
              type="number"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
            />
          </label>
          
          <button onClick={handleProcess} disabled={loading}>
            {loading ? 'Processando...' : 'Processar'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <h3>Erro:</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="results">
          <h2>Resultados da Fase 1</h2>
          
          <div className="preprocessing">
            <h3>Pré-processamento:</h3>
            <p>Palavras no fonte: {result.preprocessing.source_word_count}</p>
            <p>Palavras no alvo: {result.preprocessing.target_word_count}</p>
            <p>Tempo de processamento: {result.preprocessing.processing_time.toFixed(2)}s</p>
            {result.preprocessing.warnings.length > 0 && (
              <div className="warnings">
                <h4>Avisos:</h4>
                {result.preprocessing.warnings.map((warning, idx) => (
                  <p key={idx} className="warning">{warning}</p>
                ))}
              </div>
            )}
          </div>
          
          <div className="alignment">
            <h3>Alinhamento Semântico:</h3>
            <p>Pares alinhados: {result.alignment.aligned_pairs.length}</p>
            <p>Parágrafos não alinhados: {result.alignment.unaligned_source_indices.length}</p>
            <p>Limiar usado: {result.alignment.threshold_used}</p>
            <p>Tempo de processamento: {result.alignment.processing_time.toFixed(2)}s</p>
            
            <h4>Pares Alinhados:</h4>
            {result.alignment.aligned_pairs.map((pair, idx) => (
              <div key={idx} className="alignment-pair">
                <p><strong>Similaridade:</strong> {pair.similarity_score.toFixed(3)}</p>
                <p><strong>Fonte:</strong> {pair.source_text.substring(0, 100)}...</p>
                <p><strong>Alvo:</strong> {pair.target_text.substring(0, 100)}...</p>
                <hr />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
```

---

## Passo 6: Configuração de Testes

### 6.1 Testes Unitários do Backend

**tests/test_preprocessor.py:**
```python
import pytest
from src.modules.preprocessor import PreprocessorModule

@pytest.mark.asyncio
class TestPreprocessorModule:
    
    def setup_method(self):
        self.preprocessor = PreprocessorModule()
    
    async def test_process_text_input(self):
        source = "Este é um parágrafo de teste.\n\nEste é outro parágrafo."
        target = "Parágrafo de teste.\n\nOutro parágrafo aqui."
        
        result = await self.preprocessor.process_text_input(source, target)
        
        assert result.source_word_count > 0
        assert result.target_word_count > 0
        assert result.processing_time > 0
        assert len(result.source_text) > 0
        assert len(result.target_text) > 0
    
    async def test_word_limit_warning(self):
        # Criar texto longo (>2000 palavras)
        long_text = " ".join(["palavra"] * 2500)
        short_text = "Texto curto."
        
        result = await self.preprocessor.process_text_input(long_text, short_text)
        
        assert len(result.warnings) > 0
        assert "2500 palavras" in result.warnings[0]
```

**tests/test_semantic_aligner.py:**
```python
import pytest
from src.modules.semantic_aligner import SemanticAlignerModule

@pytest.mark.asyncio
class TestSemanticAlignerModule:
    
    def setup_method(self):
        self.aligner = SemanticAlignerModule()
    
    async def test_align_paragraphs(self):
        source = "O gato subiu no telhado.\n\nO cachorro latiu muito alto."
        target = "Um felino escalou o teto.\n\nO cão fez muito barulho."
        
        result = await self.aligner.align_paragraphs(source, target, threshold=0.3)
        
        assert len(result.aligned_pairs) > 0
        assert result.processing_time > 0
        assert result.threshold_used == 0.3
    
    def test_segment_paragraphs(self):
        text = "Primeiro parágrafo.\n\nSegundo parágrafo.\n\nTerceiro parágrafo."
        
        paragraphs = self.aligner._segment_paragraphs(text)
        
        assert len(paragraphs) == 3
        assert paragraphs[0] == "Primeiro parágrafo."
```

---

## Passo 7: Validação e Critérios de Aceite da Fase 1

### 7.1 Critérios de Sucesso

**Funcionalidades Essenciais:**
- [ ] API recebe textos ou arquivos e processa corretamente
- [ ] Pré-processador limpa textos e conta palavras precisamente
- [ ] Aviso amigável para textos > 2000 palavras
- [ ] Alinhador semântico gera embeddings com BERTimbau
- [ ] Matriz de similaridade calculada corretamente
- [ ] Alinhamento baseado em limiar funcional
- [ ] Parágrafos não alinhados identificados
- [ ] API retorna dados estruturados conforme contratos
- [ ] Frontend básico permite teste completo da pipeline

**Indicadores de Performance:**
- Processamento de 2000 palavras < 60 segundos
- Acurácia de alinhamento > 70% em testes manuais
- API responde sem erros em cenários válidos
- Tratamento de erros robusto para entradas inválidas

---

## Próximos Passos (Fase 2)

Após validação bem-sucedida da Fase 1:

1. **Módulo 3:** Implementação do classificador heurístico
2. **Módulo 4:** Interface rica com visualização de alinhamentos
3. **Módulo 5:** Sistema de feedback e banco de dados
4. **Deploy:** Configuração de produção em Hugging Face Spaces

---

**Assinatura Técnica:**  
*Wisley Vilela - Desenvolvedor Principal NET-EST*  
*Implementação baseada na proposta arquitetural do Núcleo de Estudos de Tradução*
