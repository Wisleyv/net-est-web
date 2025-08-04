"""Tests for Feature Extraction Service - Module 3
Bridge implementation tests connecting semantic alignment to tag classification
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.models.feature_extraction import (
    FeatureExtractionRequest,
    FeatureExtractionResponse,
    UserConfiguration,
    TagType,
    ConfidenceLevel
)
from src.services.feature_extraction_service import FeatureExtractionService


class TestFeatureExtractionService:
    """Test feature extraction and tag classification"""

    @pytest.fixture
    def service(self):
        """Create feature extraction service instance"""
        return FeatureExtractionService()

    @pytest.fixture
    def sample_alignment_data(self):
        """Sample alignment data from Module 2"""
        return {
            "aligned_pairs": [
                {
                    "source_idx": 0,
                    "target_idx": 0,
                    "source_text": "O sistema de análise computacional desenvolvido pela universidade utiliza algoritmos complexos de processamento de linguagem natural para identificar padrões linguísticos sofisticados em textos científicos especializados.",
                    "target_text": "O sistema de análise da universidade usa algoritmos simples para encontrar padrões em textos científicos.",
                    "similarity_score": 0.75
                }
            ],
            "unaligned_source_indices": [1],
            "source_paragraphs": [
                "O sistema de análise computacional desenvolvido pela universidade utiliza algoritmos complexos de processamento de linguagem natural para identificar padrões linguísticos sofisticados em textos científicos especializados.",
                "Este parágrafo adicional contém informações técnicas detalhadas que podem ser consideradas redundantes para o público-alvo."
            ],
            "target_paragraphs": [
                "O sistema de análise da universidade usa algoritmos simples para encontrar padrões em textos científicos."
            ]
        }

    @pytest.fixture
    def default_user_config(self):
        """Default user configuration"""
        return UserConfiguration()

    @pytest.mark.asyncio
    async def test_basic_feature_extraction(self, service, sample_alignment_data, default_user_config):
        """Test basic feature extraction and classification"""
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        assert isinstance(response, FeatureExtractionResponse)
        assert response.success == True
        assert response.total_annotations > 0
        assert len(response.annotated_data) > 0

    @pytest.mark.asyncio
    async def test_sl_plus_detection(self, service, sample_alignment_data, default_user_config):
        """Test SL+ (vocabulary simplification) detection"""
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Should detect SL+ due to vocabulary simplification
        sl_annotations = [a for a in response.annotated_data if a.tag == TagType.SL_PLUS]
        assert len(sl_annotations) > 0
        
        sl_annotation = sl_annotations[0]
        assert sl_annotation.confidence > 0.0
        assert len(sl_annotation.evidence) > 0

    @pytest.mark.asyncio
    async def test_om_plus_not_active_by_default(self, service, sample_alignment_data, default_user_config):
        """Test that OM+ is not applied by default (manual activation only)"""
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Should NOT detect OM+ because it's inactive by default
        om_annotations = [a for a in response.annotated_data if a.tag == TagType.OM_PLUS]
        assert len(om_annotations) == 0

    @pytest.mark.asyncio
    async def test_om_plus_when_activated(self, service, sample_alignment_data):
        """Test OM+ detection when manually activated"""
        
        # Create config with OM+ enabled
        config = UserConfiguration()
        config.tag_config[TagType.OM_PLUS].active = True
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Should detect OM+ for unaligned source paragraph
        om_annotations = [a for a in response.annotated_data if a.tag == TagType.OM_PLUS]
        assert len(om_annotations) > 0
        
        om_annotation = om_annotations[0]
        assert om_annotation.source_indices == [1]  # Unaligned source index
        assert om_annotation.target_indices == []   # No target for omission

    @pytest.mark.asyncio
    async def test_pro_plus_never_generated(self, service, sample_alignment_data):
        """Test that PRO+ is never generated by the system"""
        
        # Even if we try to enable PRO+, it should never be generated
        config = UserConfiguration()
        config.tag_config[TagType.PRO_PLUS].active = True
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Should NEVER detect PRO+ (manual-only tag)
        pro_annotations = [a for a in response.annotated_data if a.tag == TagType.PRO_PLUS]
        assert len(pro_annotations) == 0

    @pytest.mark.asyncio
    async def test_reduction_ratio_calculation(self, service, sample_alignment_data, default_user_config):
        """Test reduction ratio calculation and warnings"""
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Should calculate reduction ratio
        assert response.reduction_ratio_achieved > 0.0
        assert response.reduction_ratio_expected == 0.65  # Default expectation
        
        # Should have warnings if reduction is below expected
        if response.reduction_ratio_achieved < 0.50:  # Well below 65%
            assert len(response.warnings) > 0

    @pytest.mark.asyncio
    async def test_confidence_levels(self, service, sample_alignment_data, default_user_config):
        """Test confidence level assignment"""
        
        request = FeatureExtractionRequest(
            alignment_data=sample_alignment_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        # Check confidence distribution
        assert isinstance(response.confidence_distribution, dict)
        total_annotations = sum(response.confidence_distribution.values())
        assert total_annotations == response.total_annotations
        
        # Each annotation should have valid confidence level
        for annotation in response.annotated_data:
            assert annotation.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
            assert 0.0 <= annotation.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_empty_alignment_data(self, service, default_user_config):
        """Test handling of empty alignment data"""
        
        empty_data = {
            "aligned_pairs": [],
            "unaligned_source_indices": [],
            "source_paragraphs": [],
            "target_paragraphs": []
        }
        
        request = FeatureExtractionRequest(
            alignment_data=empty_data,
            user_config=default_user_config
        )
        
        response = await service.extract_features_and_classify(request)
        
        assert response.success == True
        assert response.total_annotations == 0
        assert "No simplification strategies detected" in response.warnings

    def test_user_configuration_defaults(self):
        """Test default user configuration"""
        
        config = UserConfiguration()
        
        # OM+ should be inactive by default
        assert config.tag_config[TagType.OM_PLUS].active == False
        
        # PRO+ should be inactive and manual-only
        assert config.tag_config[TagType.PRO_PLUS].active == False
        assert config.tag_config[TagType.PRO_PLUS].manual_only == True
        
        # Other tags should be active by default
        assert config.tag_config[TagType.SL_PLUS].active == True
        assert config.tag_config[TagType.RF_PLUS].active == True
        
        # Expected reduction should be 65%
        assert config.expected_reduction_ratio == 0.65
