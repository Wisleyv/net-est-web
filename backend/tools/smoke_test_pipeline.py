import os
import sys
# Ensure the workspace backend directory is on sys.path so imports like `from src...`
# resolve correctly (we need the parent directory that contains the `src` package).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
from pprint import pprint

from src.services.comparative_analysis_service import ComparativeAnalysisService
from src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions

async def run_smoke_test():
    service = ComparativeAnalysisService()

    src = (
        "A inteligência artificial está transformando o mundo. "
        "Os computadores podem processar informações rapidamente. "
        "A tecnologia blockchain é revolucionária."
    )
    tgt = (
        "IA está mudando nossa sociedade profundamente. "
        "Máquinas processam dados com alta velocidade. "
        "Blockchain representa uma nova era tecnológica."
    )

    req = ComparativeAnalysisRequest(
        source_text=src,
        target_text=tgt,
        hierarchical_output=True,
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
            include_micro_spans=False,
            include_salience=False,
        ),
    )

    resp = await service.perform_comparative_analysis(req)

    print("=== Summary ===")
    print(f"Success: response present, processing_time: {resp.processing_time:.3f}s")
    print("=== Hierarchical Analysis (trimmed) ===")
    pprint(resp.hierarchical_analysis)

if __name__ == "__main__":
    asyncio.run(run_smoke_test())