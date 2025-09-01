"""Feature Extraction API Endpoints - Module 3
API endpoints for discourse feature extraction and tag classification
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from ...services.feature_extraction_service import FeatureExtractionService
from ...models.feature_extraction import (
    FeatureExtractionRequest,
    FeatureExtractionResponse,
    UserConfiguration,
    TagType,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feature-extraction", tags=["feature-extraction"])

# Service instance
feature_service = FeatureExtractionService()


@router.post("/analyze", response_model=FeatureExtractionResponse)
async def analyze_features_and_classify(request: FeatureExtractionRequest):
    """
    Extract discourse features and classify simplification strategies
    
    Main entry point for Module 3 - Feature Extractor and Classifier
    Takes semantic alignment results and applies tag classification
    """
    try:
        response = await feature_service.extract_features_and_classify(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Feature extraction failed: {response.warnings}"
            )
        
        logger.info(f"Feature extraction completed: {response.total_annotations} annotations generated")
        return response
        
    except Exception as e:
        logger.error(f"Feature extraction endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature extraction service error: {str(e)}"
        )


@router.post("/", response_model=FeatureExtractionResponse)
async def analyze_features_root(request_body: dict):
    """Compatibility root POST -> accepts legacy payloads such as {"text": "..."}
    and coerces into FeatureExtractionRequest expected by /analyze."""
    # If provided a full FeatureExtractionRequest shape, let pydantic handle it
    if isinstance(request_body, dict) and "alignment_data" in request_body:
        request = FeatureExtractionRequest(**request_body)
    elif isinstance(request_body, dict) and "text" in request_body:
        # Build a minimal alignment_data stub from raw text input
        stub_alignment = {
            "aligned_pairs": [],
            "unaligned_source_indices": [],
            "source_paragraphs": [request_body.get("text", "")],
            "target_paragraphs": [request_body.get("text", "")],
        }
        request = FeatureExtractionRequest(alignment_data=stub_alignment, user_config=UserConfiguration())
    else:
        request = FeatureExtractionRequest(**request_body)

    return await analyze_features_and_classify(request)


@router.post("/analyze-from-alignment", response_model=FeatureExtractionResponse)
async def analyze_from_alignment_response(
    alignment_response: Dict[str, Any],
    user_config: UserConfiguration | None = None
):
    """
    Convenience endpoint that takes semantic alignment response directly
    
    Designed to be chained after semantic alignment for complete pipeline
    """
    try:
        # Use default configuration if none provided
        if user_config is None:
            user_config = UserConfiguration()
        
        # Create feature extraction request
        request = FeatureExtractionRequest(
            alignment_data=alignment_response,
            user_config=user_config
        )
        
        return await analyze_features_and_classify(request)
        
    except Exception as e:
        logger.error(f"Alignment-to-features analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}"
        )


@router.get("/default-config", response_model=UserConfiguration)
async def get_default_configuration():
    """Get default user configuration for tag analysis"""
    return UserConfiguration()


@router.post("/update-config", response_model=UserConfiguration)
async def update_user_configuration(
    tag_updates: Dict[str, Dict[str, Any]] | None = None,
    threshold_updates: Dict[str, float] | None = None,
    reduction_ratio: float | None = None
):
    """
    Update user configuration for tag analysis
    
    Args:
        tag_updates: Dict of tag configs {tag_name: {active: bool, weight: float}}
        threshold_updates: Dict of confidence thresholds {level: float}
        reduction_ratio: Expected reduction ratio (0.0-1.0)
    """
    try:
        config = UserConfiguration()
        
        # Update tag configurations
        if tag_updates:
            for tag_name, updates in tag_updates.items():
                try:
                    tag_type = TagType(tag_name)
                    if tag_type in config.tag_config:
                        if 'active' in updates:
                            config.tag_config[tag_type].active = updates['active']
                        if 'weight' in updates:
                            config.tag_config[tag_type].weight = max(0.0, min(2.0, updates['weight']))
                except ValueError:
                    logger.warning(f"Invalid tag type: {tag_name}")
        
        # Update confidence thresholds
        if threshold_updates:
            for level, threshold in threshold_updates.items():
                try:
                    confidence_level = ConfidenceLevel(level)
                    config.confidence_thresholds[confidence_level] = max(0.0, min(1.0, threshold))
                except ValueError:
                    logger.warning(f"Invalid confidence level: {level}")
        
        # Update reduction ratio
        if reduction_ratio is not None:
            config.expected_reduction_ratio = max(0.0, min(1.0, reduction_ratio))
        
        return config
        
    except Exception as e:
        logger.error(f"Configuration update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Configuration update failed: {str(e)}"
        )


@router.get("/supported-tags")
async def get_supported_tags():
    """Get list of all supported simplification strategy tags with official descriptions"""
    
    # Official descriptions from "Tabela Simplificação Textual.md"
    tag_descriptions = {
        TagType.AS_PLUS: "Alteração de Sentido - Embora não seja usada como estratégia intencional, pode ocorrer como resultado de modulações, ao expressar a mesma ideia por outro ponto de vista.",
        TagType.DL_PLUS: "Reorganização Posicional - Mudança na ordem dos elementos na frase para melhorar o fluxo da informação. Inclui extraposição, antecipação e movimentação de inserções ou tópicos para facilitar a leitura.",
        TagType.EXP_PLUS: "Explicitação e Detalhamento - Adição de informações, exemplos ou paráfrases para esclarecer conteúdos implícitos ou complexos. Ajuda o leitor a compreender conceitos que exigiriam conhecimento prévio.",
        TagType.IN_PLUS: "Manejo de Inserções - Eliminação, deslocamento ou reestruturação de inserções que atrapalham a fluidez da sentença. Pode incluir repetição de elementos para manter a coesão em textos falados ou escritos.",
        TagType.MOD_PLUS: "Reinterpretação Perspectiva - Reformulação semântica para adaptar o conteúdo ao repertório do público. Inclui substituição de metáforas, expressões idiomáticas e construções figurativas por formas mais diretas.",
        TagType.MT_PLUS: "Otimização de Títulos - Reformulação ou criação de títulos que tornem o conteúdo mais visível, explícito e tematicamente alinhado ao público-alvo.",
        TagType.OM_PLUS: "Supressão Seletiva - Exclusão de elementos redundantes, ambíguos, idiomáticos ou periféricos que não comprometem o núcleo do conteúdo e atrapalham a compreensão. [MANUAL ACTIVATION ONLY]",
        TagType.PRO_PLUS: "Desvio Semântico e/ou Interpretativo - Tag usada para anotação de problemas tradutórios de interpretação textual. [MANUAL INSERTION ONLY - NEVER GENERATED]",
        TagType.RF_PLUS: "Reescrita Global - Estratégia abrangente que integra múltiplos procedimentos de simplificação (lexical, sintática, discursiva). Visa à reformulação integral do texto para otimizar sua acessibilidade.",
        TagType.RD_PLUS: "Estruturação de Conteúdo e Fluxo - Reorganização macroestrutural do texto (sequência temática, paragrafação, uso de conectivos) para manter coerência, continuidade e progressão textual.",
        TagType.RP_PLUS: "Fragmentação Sintática - Divisão de períodos extensos ou complexos em sentenças mais curtas e diretas, facilitando o processamento por parte de leitores com menor fluência.",
        TagType.SL_PLUS: "Adequação de Vocabulário - Substituição de termos difíceis, técnicos ou raros por sinônimos mais simples, comuns ou hiperônimos. Também envolve evitar polissemia, jargões e repetições desnecessárias.",
        TagType.TA_PLUS: "Clareza Referencial - Estratégias para garantir que pronomes e outras referências anafóricas sejam facilmente compreendidos. Inclui evitar catáforas e uso de sinônimos distantes ou ambíguos.",
        TagType.MV_PLUS: "Alteração da Voz Verbal - Mudança da voz passiva para ativa (ou vice-versa) para garantir maior clareza, fluência e naturalidade. A escolha depende da necessidade de destacar ou omitir agentes."
    }
    
    return {
        "supported_tags": tag_descriptions,
        "default_active": [tag.value for tag in TagType if tag not in [TagType.OM_PLUS, TagType.PRO_PLUS]],
        "manual_activation_only": [TagType.OM_PLUS.value],
        "manual_insertion_only": [TagType.PRO_PLUS.value], 
        "never_generated": [TagType.PRO_PLUS.value],
        "usage_notes": {
            "OM+": "Only applied when manually activated by user - not default for unaligned paragraphs",
            "PRO+": "Never generated by system - manual insertion only in target text body",
            "reduction_expectation": "Simplification should target ~65% text reduction"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for feature extraction service"""
    try:
        # Test basic functionality
        config = UserConfiguration()
        
        return {
            "status": "healthy",
            "service": "feature-extraction",
            "spacy_available": feature_service.nlp is not None,
            "default_tags_active": len([t for t in config.tag_config.values() if t.active]),
            "version": "1.0.0"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Feature extraction service unhealthy: {str(e)}"
        )
