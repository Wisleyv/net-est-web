import asyncio, traceback
from types import SimpleNamespace
from src.services.comparative_analysis_service import ComparativeAnalysisService

async def run():
    svc = ComparativeAnalysisService()
    req = {'source_text':'This is a test source','target_text':'This is a test target'}
    try:
        res = await svc.perform_comparative_analysis(req)
        print('OK', type(res))
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(run())
