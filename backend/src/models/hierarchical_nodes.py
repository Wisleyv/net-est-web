# Salience normalization semantics:
# - Paragraph salience (ParagraphNode.confidence) is computed as the average unit weight
#   for the paragraph and then normalized across all paragraphs so the maximum paragraph
#   salience becomes 1.0 (local paragraph normalization).
# - Sentence salience (SentenceNode.salience_score / PhraseNode.salience_score) is
#   computed per sentence/phrase and normalized within its containing paragraph
#   (per-paragraph max => 1.0). These semantics make salience relative within the
#   paragraph scope rather than globally comparable across the entire document.
# - Consumers (frontend / analytics) should treat salience values as relative unless
#   explicitly denormalized by server-side aggregation.
#
# Note: The service implements these normalization steps inside the hierarchical builder
# (see backend/src/services/comparative_analysis_service.py). If you change the
# normalization algorithm, update this comment and add/adjust unit tests accordingly.
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict


@dataclass
class PhraseNode:
    """
    Represents a phrase in the hierarchical analysis (dataclass form).
    Extended with feature extraction fields:
      - key_phrases: list of detected key-phrase strings relevant to this phrase node
      - salience_score: optional numeric salience (0..1) assigned by salience provider
      - features: dictionary for arbitrary, extracted feature values (e.g., syllable counts, POS tags)
    Kept JSON-serializable via dataclasses.asdict.
    """
    level: str = "phrase"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    # Feature extraction fields
    key_phrases: List[str] = field(default_factory=list)
    salience_score: Optional[float] = None
    features: Dict[str, Any] = field(default_factory=dict)
    # Additional arbitrary payload (kept flexible for forward compatibility)
    extra: Any = None


@dataclass
class SentenceNode:
    """
    Represents a sentence in the hierarchical analysis (dataclass form).
    Contains nested PhraseNode objects in nested_findings.
    Extended with:
      - key_phrases: aggregated key phrases for the sentence
      - salience_score: numeric salience for the sentence (0..1) when available
      - features: dictionary for sentence-level extracted features (e.g., avg_word_len, syllable_count)
    """
    level: str = "sentence"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    nested_findings: List[PhraseNode] = field(default_factory=list)
    # Feature extraction fields
    key_phrases: List[str] = field(default_factory=list)
    salience_score: Optional[float] = None
    features: Dict[str, Any] = field(default_factory=dict)
    extra: Any = None


@dataclass
class ParagraphNode:
    """
    Represents a paragraph in the hierarchical analysis (dataclass form).
    Contains nested SentenceNode objects in nested_findings.
    """
    level: str = "paragraph"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    nested_findings: List[SentenceNode] = field(default_factory=list)
    extra: Any = None


# Helper to convert dataclass instances to JSON-serializable dicts (shallow convert).
def to_dict(node):
    return asdict(node)