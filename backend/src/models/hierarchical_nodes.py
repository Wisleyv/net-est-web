from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any


@dataclass
class PhraseNode:
    """
    Represents a phrase in the hierarchical analysis (dataclass form).
    Kept minimal and JSON-serializable via dataclasses.asdict.
    """
    level: str = "phrase"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    # Additional arbitrary payload (kept flexible for forward compatibility)
    extra: Any = None


@dataclass
class SentenceNode:
    """
    Represents a sentence in the hierarchical analysis (dataclass form).
    Contains nested PhraseNode objects in nested_findings.
    """
    level: str = "sentence"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    nested_findings: List[PhraseNode] = field(default_factory=list)
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