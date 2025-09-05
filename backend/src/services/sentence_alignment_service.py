import re
from typing import List, Tuple, Optional
from src.core.feature_flags import feature_flags

class SentenceAlignmentService:
    def __init__(self, enable_spacy: bool = True):
        self.enable_spacy = enable_spacy
        self.nlp = None
        
        if enable_spacy:
            try:
                import spacy
                # Try to load Portuguese model, fallback to blank if not available
                try:
                    self.nlp = spacy.load("pt_core_news_sm")
                except OSError:
                    self.nlp = spacy.blank("pt")
                    # blank pipelines do not include sentence boundary detection by
                    # default. Add the lightweight sentencizer so `doc.sents` is available
                    # even when the language model is missing.
                    try:
                        if 'sentencizer' not in self.nlp.pipe_names:
                            self.nlp.add_pipe('sentencizer')
                    except Exception:
                        # Defensive: if add_pipe fails for any reason, fall back to
                        # regex splitter at runtime (split_sentences handles this when
                        # enable_spacy is False or nlp is None).
                        self.nlp = None
                    else:
                        print("Portuguese model not found. Using blank spaCy model with sentencizer.")
            except ImportError:
                print("spaCy not installed. Using fallback sentence splitter.")
                self.enable_spacy = False

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using spaCy or regex fallback"""
        if self.enable_spacy and self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            # Fallback regex sentence splitter for Portuguese
            return [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text) if s.strip()]

    def calculate_similarity(self, source: List[str], target: List[str]) -> List[List[float]]:
        """Calculate similarity matrix between source and target sentences"""
        # Placeholder for actual similarity calculation
        # In real implementation, we'd use SentenceTransformer embeddings
        matrix = []
        for _ in source:
            row = [1.0] * len(target)  # Dummy similarity values
            matrix.append(row)
        return matrix

    def align(self, source_sentences: List[str], target_sentences: List[str], threshold: float = 0.3):
        """Align sentences between source and target lists"""
        # Prepare default empty result shape
        if not source_sentences or not target_sentences:
            return type('AlignmentResult', (), {
                'aligned': [],
                'unmatched_source': list(range(len(source_sentences))) if source_sentences else [],
                'unmatched_target': list(range(len(target_sentences))) if target_sentences else [],
                'similarity_matrix': []
            })()

        similarity_matrix = self.calculate_similarity(source_sentences, target_sentences)

        aligned = []
        used_target_indices = set()

        for source_idx, source_sent in enumerate(source_sentences):
            best_similarity = -1
            best_target_idx = -1

            for target_idx, target_sent in enumerate(target_sentences):
                if target_idx in used_target_indices:
                    continue

                similarity = similarity_matrix[source_idx][target_idx]

                if similarity > best_similarity and similarity >= threshold:
                    best_similarity = similarity
                    best_target_idx = target_idx

            if best_target_idx != -1:
                # Use plain dicts for alignment records to ensure JSON serializability
                aligned.append({
                    'source_index': source_idx,
                    'target_index': best_target_idx,
                    'relation': 'aligned',
                    'similarity': best_similarity
                })
                used_target_indices.add(best_target_idx)

        # Build unmatched lists
        # Support both dict-records and attribute-style records
        def _rec_source_index(rec):
            if isinstance(rec, dict):
                return rec.get('source_index')
            return getattr(rec, 'source_index', None)

        unmatched_source = [i for i in range(len(source_sentences)) if not any(_rec_source_index(rec) == i for rec in aligned)]
        unmatched_target = [i for i in range(len(target_sentences)) if i not in used_target_indices]

        return type('AlignmentResult', (), {
            'aligned': aligned,
            'unmatched_source': unmatched_source,
            'unmatched_target': unmatched_target,
            'similarity_matrix': similarity_matrix
        })()

# Global instance for easy access
sentence_aligner = SentenceAlignmentService()
