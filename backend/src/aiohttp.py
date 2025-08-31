"""Tiny aiohttp compatibility shim used by tests when aiohttp isn't installed.
This lives in src/ so 'import aiohttp' resolves during tests.
"""
import asyncio

class ClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, **kwargs):
        class Resp:
            def __init__(self):
                self.status = 200
            async def text(self):
                return ''
            async def json(self):
                return {}
        return Resp()

class TCPConnector:
    def __init__(self, *args, **kwargs):
        pass
