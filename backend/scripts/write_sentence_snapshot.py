import sys
import json, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.services.sentence_alignment_service import SentenceAlignmentService

UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")

def _normalize(obj):
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(x) for x in obj]
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, str) and UUID_RE.search(obj):
        return UUID_RE.sub("<uuid>", obj)
    return obj

service = SentenceAlignmentService(enable_spacy=False)
src = [
    "A inteligência artificial avança rapidamente.",
    "Computadores processam dados."
]
tgt = [
    "IA avança rápido.",
    "Os computadores processam rapidamente os dados."
]
result = service.align(src, tgt, threshold=0.2)
normalized = _normalize({
    "aligned": result.aligned,
    "similarity_matrix": result.similarity_matrix
})
serialized = json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2)
path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'snapshots', 'test_sentence_alignment_service_snapshot', 'test_alignment_basic_pairs_snapshot', 'sentence_alignment_snapshot')
path = os.path.abspath(path)
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(serialized)
print('WROTE', path)
