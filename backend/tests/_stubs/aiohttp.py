"""Minimal aiohttp stub for tests that import aiohttp when running locally.
Provides a tiny ClientSession and TCPConnector shim sufficient for test concurrency.
"""
import asyncio

class ClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None):
        # Very small compatibility shim used by tests that spawn concurrent posts.
        class Resp:
            def __init__(self):
                self.status = 200
            async def text(self):
                return ''
        return Resp()

class TCPConnector:
    def __init__(self, *args, **kwargs):
        pass
"""Lightweight test stub for aiohttp to satisfy import in tests.
This stub provides only the small subset used in the test suite (client session context manager).
"""
import asyncio
from types import SimpleNamespace

class ClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None):
        # Minimal stubbed response object used in tests
        class Resp:
            def __init__(self):
                self.status = 200

            async def json(self):
                return {}

        return Resp()

# Expose minimal API
__all__ = ['ClientSession']
