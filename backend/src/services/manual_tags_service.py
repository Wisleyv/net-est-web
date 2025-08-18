"""Manual Tags Service
Service layer for managing user-created manual tags on sentences
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..models.manual_tags import (
    ManualTag, 
    ManualTagType, 
    CreateTagRequest, 
    UpdateTagRequest
)


class ManualTagsService:
    """Service for managing manual tags"""
    
    def __init__(self):
        # In-memory storage for now (could be replaced with database later)
        self._tags: Dict[str, ManualTag] = {}
        self._tags_by_analysis: Dict[str, List[str]] = {}  # analysis_id -> tag_ids
    
    def create_tag(self, request: CreateTagRequest) -> ManualTag:
        """Create a new manual tag"""
        tag_id = str(uuid.uuid4())
        
        tag = ManualTag(
            id=tag_id,
            tag_type=request.tag_type,
            sentence_index=request.sentence_index,
            sentence_text=request.sentence_text,
            analysis_id=request.analysis_id,
            user_notes=request.user_notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store the tag
        self._tags[tag_id] = tag
        
        # Index by analysis_id
        if request.analysis_id not in self._tags_by_analysis:
            self._tags_by_analysis[request.analysis_id] = []
        self._tags_by_analysis[request.analysis_id].append(tag_id)
        
        return tag
    
    def get_tag(self, tag_id: str) -> Optional[ManualTag]:
        """Get a specific tag by ID"""
        return self._tags.get(tag_id)
    
    def get_tags_for_analysis(self, analysis_id: str) -> List[ManualTag]:
        """Get all tags for a specific analysis session"""
        tag_ids = self._tags_by_analysis.get(analysis_id, [])
        return [self._tags[tag_id] for tag_id in tag_ids if tag_id in self._tags]
    
    def get_tags_for_sentence(self, analysis_id: str, sentence_index: int) -> List[ManualTag]:
        """Get all tags for a specific sentence in an analysis"""
        analysis_tags = self.get_tags_for_analysis(analysis_id)
        return [tag for tag in analysis_tags if tag.sentence_index == sentence_index]
    
    def update_tag(self, tag_id: str, request: UpdateTagRequest) -> Optional[ManualTag]:
        """Update an existing tag"""
        tag = self._tags.get(tag_id)
        if not tag:
            return None
        
        # Update fields if provided
        if request.tag_type is not None:
            tag.tag_type = request.tag_type
        if request.user_notes is not None:
            tag.user_notes = request.user_notes
        
        tag.updated_at = datetime.now()
        
        return tag
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag"""
        tag = self._tags.get(tag_id)
        if not tag:
            return False
        
        # Remove from main storage
        del self._tags[tag_id]
        
        # Remove from analysis index
        analysis_id = tag.analysis_id
        if analysis_id in self._tags_by_analysis:
            if tag_id in self._tags_by_analysis[analysis_id]:
                self._tags_by_analysis[analysis_id].remove(tag_id)
        
        return True
    
    def delete_tags_for_analysis(self, analysis_id: str) -> int:
        """Delete all tags for an analysis session"""
        tag_ids = self._tags_by_analysis.get(analysis_id, []).copy()
        deleted_count = 0
        
        for tag_id in tag_ids:
            if self.delete_tag(tag_id):
                deleted_count += 1
        
        # Clean up the analysis index
        if analysis_id in self._tags_by_analysis:
            del self._tags_by_analysis[analysis_id]
        
        return deleted_count
    
    def get_available_tag_types(self) -> Dict[str, str]:
        """Get available manual tag types with descriptions"""
        # Official descriptions from the system
        tag_descriptions = {
            ManualTagType.AS_PLUS.value: "Alteração de Sentido",
            ManualTagType.DL_PLUS.value: "Reorganização Posicional",
            ManualTagType.EXP_PLUS.value: "Explicitação e Detalhamento",
            ManualTagType.IN_PLUS.value: "Manejo de Inserções",
            ManualTagType.MOD_PLUS.value: "Reinterpretação Perspectiva",
            ManualTagType.MT_PLUS.value: "Otimização de Títulos",
            ManualTagType.OM_PLUS.value: "Supressão Seletiva",
            ManualTagType.PRO_PLUS.value: "Desvio Semântico",
            ManualTagType.RF_PLUS.value: "Reescrita Global",
            ManualTagType.RD_PLUS.value: "Estruturação de Conteúdo e Fluxo",
            ManualTagType.RP_PLUS.value: "Fragmentação Sintática",
            ManualTagType.SL_PLUS.value: "Adequação de Vocabulário",
            ManualTagType.TA_PLUS.value: "Clareza Referencial",
            ManualTagType.MV_PLUS.value: "Alteração da Voz Verbal",
        }
        return tag_descriptions
    
    def get_stats(self, analysis_id: Optional[str] = None) -> Dict[str, any]:
        """Get statistics about tags"""
        if analysis_id:
            tags = self.get_tags_for_analysis(analysis_id)
        else:
            tags = list(self._tags.values())
        
        tag_type_counts = {}
        for tag in tags:
            tag_type = tag.tag_type.value
            tag_type_counts[tag_type] = tag_type_counts.get(tag_type, 0) + 1
        
        return {
            "total_tags": len(tags),
            "tag_type_distribution": tag_type_counts,
            "analysis_sessions": len(self._tags_by_analysis) if not analysis_id else 1
        }


# Global service instance
manual_tags_service = ManualTagsService()