import io
import logging
import os
import sys
import unittest

from aiohttp import web
from server import PromptServer

logger = logging.getLogger(__name__)


class TestRoutes(unittest.TestCase):
    def test_hello_world(self):
        self.assertTrue(True)

    def test_register_route_api_exists(self):
        self.assertTrue(hasattr(PromptServer.instance, "register_route"))

    def test_register_local_route(self):
        import aiohttp
        import asyncio

        test_path = "/test_iso_route_dynamic"
        expected_response = "Hello from Dynamic Route!"

        async def handler(request):
            return web.Response(text=expected_response)

        PromptServer.instance.register_route("GET", test_path, handler)

        async def verify():
            port = getattr(PromptServer.instance, "port", 8188)
            base_url = f"http://127.0.0.1:{port}"
            url = f"{base_url}{test_path}"

            async with aiohttp.ClientSession() as session:
                headers = {"Origin": base_url}
                async with session.get(url, headers=headers, timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
                    text = await resp.text()
                    self.assertEqual(text, expected_response)

        loop = PromptServer.instance.loop
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(verify(), loop)
            future.result(timeout=10)
        else:
            loop.run_until_complete(verify())

    def test_routes_decorator(self):
        import aiohttp
        import asyncio

        test_path = "/test_iso_route_decorator"
        expected_response = "Hello from Decorator Route!"

        @PromptServer.instance.routes.get(test_path)
        async def handler(request):
            return web.Response(text=expected_response)

        async def verify():
            port = getattr(PromptServer.instance, "port", 8188)
            base_url = f"http://127.0.0.1:{port}"
            url = f"{base_url}{test_path}"

            async with aiohttp.ClientSession() as session:
                headers = {"Origin": base_url}
                async with session.get(url, headers=headers, timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
                    text = await resp.text()
                    self.assertEqual(text, expected_response)

        loop = PromptServer.instance.loop
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(verify(), loop)
            future.result(timeout=10)
        else:
            loop.run_until_complete(verify())

    def test_prompt_server_messaging(self):
        PromptServer.instance.send_sync("test_event", {"data": "test"})


class RunIsolationTests:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"test_module": (["all", "routes"],)}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "run_tests"
    CATEGORY = "PyIsolate/Debug"
    OUTPUT_NODE = True

    def run_tests(self, test_module):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        if test_module in ("all", "routes"):
            suite.addTests(loader.loadTestsFromTestCase(TestRoutes))

        output = io.StringIO()
        runner = unittest.TextTestRunner(stream=output, verbosity=2)
        result = runner.run(suite)

        report = output.getvalue()
        report += f"\nRan {result.testsRun} tests. Failures: {len(result.failures)} Errors: {len(result.errors)}"

        return (report,)


class TestCLIPProxy:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "text": ("STRING", {"multiline": True, "default": "a photo of a cat"}),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("conditioning", "report")
    FUNCTION = "test_clip"
    CATEGORY = "PyIsolate/Debug"
    OUTPUT_NODE = True

    def test_clip(self, clip, text):
        import torch

        is_isolated = os.environ.get("PYISOLATE_CHILD") == "1"
        clip_type = type(clip).__name__
        report_lines = [f"Isolated: {is_isolated}", f"CLIP type: {clip_type}"]

        tokens = clip.tokenize(text)
        report_lines.append(f"tokenize: keys={list(tokens.keys()) if isinstance(tokens, dict) else type(tokens)}")

        cond = clip.encode_from_tokens_scheduled(tokens)
        if isinstance(cond, list) and len(cond) > 0 and isinstance(cond[0], tuple):
            tensor = cond[0][0]
            report_lines.append(f"encode: shape={tensor.shape if hasattr(tensor, 'shape') else 'N/A'}")

        return (cond, "\n".join(report_lines))


class TestCLIPProxySimple:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "text": ("STRING", {"multiline": False, "default": "hello world"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "test_tokenize"
    CATEGORY = "PyIsolate/Debug"
    OUTPUT_NODE = True

    def test_tokenize(self, clip, text):
        is_isolated = os.environ.get("PYISOLATE_CHILD") == "1"
        clip_type = type(clip).__name__

        tokens = clip.tokenize(text)
        token_info = f"keys={list(tokens.keys())}" if isinstance(tokens, dict) else f"type={type(tokens)}"
        report = f"CLIP tokenize OK\nIsolated: {is_isolated}\nCLIP type: {clip_type}\nTokens: {token_info}"

        return (report,)


NODE_CLASS_MAPPINGS = {
    "RunIsolationTests": RunIsolationTests,
    "TestCLIPProxy": TestCLIPProxy,
    "TestCLIPProxySimple": TestCLIPProxySimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RunIsolationTests": "Run Isolation Tests",
    "TestCLIPProxy": "Test CLIP Proxy (Full)",
    "TestCLIPProxySimple": "Test CLIP Proxy (Tokenize Only)",
}
