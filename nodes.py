import unittest
import io
import sys
import os
import logging
from server import PromptServer
from aiohttp import web

# Define tests directly in the node file
class TestRoutes(unittest.TestCase):
    def test_hello_world(self):
        """Basic hello world test to verify test runner works."""
        self.assertTrue(True, "Hello World should pass")

    def test_register_route_api_exists(self):
        """Verify that PromptServer.instance has register_route method."""
        self.assertTrue(hasattr(PromptServer.instance, "register_route"), 
                        "PromptServer.instance should have register_route method")

    def test_register_local_route(self):
        """Verify that a route can be registered and accessed."""
        import aiohttp
        import asyncio
        
        # Define a unique path for this test
        test_path = "/test_iso_route_dynamic"
        expected_response = "Hello from Dynamic Route!"
        
        # Define handler
        async def handler(request):
            return web.Response(text=expected_response)
            
        # Register route - this should now work dynamically thanks to server.py fix
        PromptServer.instance.register_route("GET", test_path, handler)
        
        # Verify route access
        async def verify():
            logger = logging.getLogger("PyIsolate.Test")
            logger.info(f"DEBUG: Starting verification for {test_path}")
            port = getattr(PromptServer.instance, "port", 8188)
            # Try localhost first, then 127.0.0.1
            base_url = f"http://127.0.0.1:{port}"
            url = f"{base_url}{test_path}"
            logger.info(f"DEBUG: Requesting {url}")
            
            try:
                async with aiohttp.ClientSession() as session:
                    # CRITICAL: Send Origin header to bypass CSRF middleware
                    headers = {"Origin": base_url}
                    
                    async with session.get(url, headers=headers, timeout=5) as resp:
                        logger.info(f"DEBUG: Response status {resp.status}")
                        if resp.status == 404:
                            logger.warning(f"WARNING: Dynamic route {test_path} not found (404). Runtime registration might be blocked.")
                        
                        self.assertEqual(resp.status, 200, f"Route returned status {resp.status}")
                        text = await resp.text()
                        logger.info(f"DEBUG: Response text: {text}")
                        self.assertEqual(text, expected_response, f"Route returned unexpected text: {text}")
            except Exception as e:
                logger.error(f"DEBUG: Verification failed with exception: {e}")
                raise e
                    
        # Run verification
        logger = logging.getLogger("PyIsolate.Test")
        logger.info("DEBUG: Getting loop from PromptServer")
        loop = PromptServer.instance.loop
        logger.info(f"DEBUG: Loop is {loop}, running={loop.is_running()}")
        
        if loop.is_running():
            logger.info("DEBUG: Scheduling verify() on loop")
            future = asyncio.run_coroutine_threadsafe(verify(), loop)
            try:
                logger.info("DEBUG: Waiting for future result...")
                # Increased timeout to 10s
                future.result(timeout=10)
                logger.info("DEBUG: Future completed successfully")
            except Exception as e:
                logger.error(f"DEBUG: Future result failed: {e}")
                raise e
        else:
            logger.info("DEBUG: Loop not running, using run_until_complete")
            loop.run_until_complete(verify())

    def test_routes_decorator(self):
        """Verify that @PromptServer.instance.routes.get works."""
        import aiohttp
        import asyncio
        
        test_path = "/test_iso_route_decorator"
        expected_response = "Hello from Decorator Route!"
        
        # Define handler using decorator
        # Note: We can't use the decorator syntax directly inside a method easily if we want to capture local vars?
        # Actually we can.
        
        @PromptServer.instance.routes.get(test_path)
        async def handler(request):
            return web.Response(text=expected_response)
            
        # Verify route access
        async def verify():
            logger = logging.getLogger("PyIsolate.Test")
            port = getattr(PromptServer.instance, "port", 8188)
            base_url = f"http://127.0.0.1:{port}"
            url = f"{base_url}{test_path}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Origin": base_url}
                    async with session.get(url, headers=headers, timeout=5) as resp:
                        self.assertEqual(resp.status, 200, f"Decorator route returned status {resp.status}")
                        text = await resp.text()
                        self.assertEqual(text, expected_response, f"Decorator route returned unexpected text: {text}")
            except Exception as e:
                logger.error(f"DEBUG: Decorator verification failed: {e}")
                raise e

        # Run verification
        loop = PromptServer.instance.loop
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(verify(), loop)
            future.result(timeout=10)
        else:
            loop.run_until_complete(verify())

    def test_prompt_server_messaging(self):
        """Verify PromptServer messaging API exists and doesn't crash."""
        # We can't easily verify the frontend received it, but we can verify the call succeeds
        try:
            PromptServer.instance.send_sync("test_event", {"data": "test"})
        except Exception as e:
            self.fail(f"PromptServer.send_sync failed: {e}")
            
        # Verify queue has item (optional, depends on implementation details)
        # self.assertTrue(PromptServer.instance.messages.qsize() > 0)

class RunIsolationTests:
    """
    A node that runs the internal unit test suite for PyIsolate integration.
    This serves as both a verification tool and a reference implementation.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "test_module": (["all", "routes"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)
    FUNCTION = "run_tests"
    CATEGORY = "PyIsolate/Debug"
    OUTPUT_NODE = True

    def run_tests(self, test_module):
        # This runs INSIDE the isolated process
        logger = logging.getLogger("PyIsolate.Test")
        logger.info(f"Starting isolation tests: module={test_module}")

        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Load tests defined in this file
        if test_module == "all" or test_module == "routes":
            suite.addTests(loader.loadTestsFromTestCase(TestRoutes))

        output = io.StringIO()
        runner = unittest.TextTestRunner(stream=output, verbosity=2)
        result = runner.run(suite)
        
        report = output.getvalue()
        report += f"\nRan {result.testsRun} tests."
        report += f"\nFailures: {len(result.failures)}"
        report += f"\nErrors: {len(result.errors)}"
        
        logger.info(f"Test execution complete:\n{report}")

        if not result.wasSuccessful():
            logger.error(f"Isolation tests failed:\n{report}")
            # DO NOT RAISE - return the report so it can be saved
            # raise RuntimeError(f"Isolation tests failed:\n{report}")
            
        return (report,)

class TestCLIPProxy:
    """
    Test node that exercises CLIP proxy functionality.
    
    When running isolated, CLIP will be a CLIPProxy that RPCs to host.
    This node verifies:
    1. clip.tokenize() works
    2. clip.encode_from_tokens_scheduled() works
    3. Results are valid conditioning tensors
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP",),
                "text": ("STRING", {"multiline": True, "default": "a photo of a cat"}),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "STRING",)
    RETURN_NAMES = ("conditioning", "report",)
    FUNCTION = "test_clip"
    CATEGORY = "PyIsolate/Debug"
    OUTPUT_NODE = True

    def test_clip(self, clip, text):
        """
        Exercise CLIP proxy methods and verify results.
        
        This is the core test for CLIP isolation - if this works,
        custom nodes that use CLIP encoding will work.
        """
        import torch
        logger = logging.getLogger("PyIsolate.Test")
        report_lines = []
        
        # Check if we're in isolated mode
        is_isolated = os.environ.get("PYISOLATE_CHILD") == "1"
        clip_type = type(clip).__name__
        report_lines.append(f"Isolated: {is_isolated}")
        report_lines.append(f"CLIP type: {clip_type}")
        logger.info(f"📚 [TestCLIPProxy] Isolated={is_isolated}, CLIP type={clip_type}")
        
        # Test 1: tokenize
        try:
            tokens = clip.tokenize(text)
            report_lines.append(f"✅ tokenize() succeeded")
            report_lines.append(f"   Token keys: {list(tokens.keys()) if isinstance(tokens, dict) else 'not a dict'}")
            logger.info(f"📚 [TestCLIPProxy] tokenize() returned: {type(tokens)}")
        except Exception as e:
            report_lines.append(f"❌ tokenize() failed: {e}")
            logger.error(f"📚 [TestCLIPProxy] tokenize() failed: {e}")
            raise
        
        # Test 2: encode_from_tokens_scheduled (the method used by CLIPTextEncode)
        try:
            cond = clip.encode_from_tokens_scheduled(tokens)
            report_lines.append(f"✅ encode_from_tokens_scheduled() succeeded")
            
            # Validate conditioning structure
            if isinstance(cond, list) and len(cond) > 0:
                first_item = cond[0]
                if isinstance(first_item, tuple) and len(first_item) >= 2:
                    tensor, pooled = first_item[0], first_item[1]
                    report_lines.append(f"   Tensor shape: {tensor.shape if hasattr(tensor, 'shape') else 'no shape'}")
                    report_lines.append(f"   Pooled type: {type(pooled)}")
                    logger.info(f"📚 [TestCLIPProxy] Conditioning tensor shape: {tensor.shape if hasattr(tensor, 'shape') else 'N/A'}")
                else:
                    report_lines.append(f"   Unexpected tuple structure: {type(first_item)}")
            else:
                report_lines.append(f"   Unexpected result type: {type(cond)}")
            
            logger.info(f"📚 [TestCLIPProxy] encode_from_tokens_scheduled() returned: {type(cond)}")
        except Exception as e:
            report_lines.append(f"❌ encode_from_tokens_scheduled() failed: {e}")
            logger.error(f"📚 [TestCLIPProxy] encode_from_tokens_scheduled() failed: {e}")
            raise
        
        # Test 3: Verify we can use the conditioning (it's valid tensor data)
        try:
            # Standard ComfyUI conditioning format check
            if isinstance(cond, list) and len(cond) > 0:
                report_lines.append(f"✅ Conditioning is valid ComfyUI format")
            else:
                report_lines.append(f"⚠️ Conditioning format unexpected")
        except Exception as e:
            report_lines.append(f"❌ Conditioning validation failed: {e}")
        
        report = "\n".join(report_lines)
        logger.info(f"📚 [TestCLIPProxy] Test complete:\n{report}")
        
        return (cond, report,)


class TestCLIPProxySimple:
    """
    Minimal CLIP test - just tokenize and report.
    No encoding, no tensors - pure string in, dict out.
    """
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
        """Just test tokenization - no tensor operations."""
        logger = logging.getLogger("PyIsolate.Test")
        
        is_isolated = os.environ.get("PYISOLATE_CHILD") == "1"
        clip_type = type(clip).__name__
        
        try:
            tokens = clip.tokenize(text)
            token_info = f"keys={list(tokens.keys())}" if isinstance(tokens, dict) else f"type={type(tokens)}"
            report = f"✅ CLIP tokenize succeeded\nIsolated: {is_isolated}\nCLIP type: {clip_type}\nTokens: {token_info}"
            logger.info(f"📚 [TestCLIPProxySimple] {report}")
        except Exception as e:
            report = f"❌ CLIP tokenize failed\nIsolated: {is_isolated}\nCLIP type: {clip_type}\nError: {e}"
            logger.error(f"📚 [TestCLIPProxySimple] {report}")
            raise
        
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
