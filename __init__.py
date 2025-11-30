import os
import sys

# Startup diagnostic - this should appear in logs for BOTH isolated and non-isolated
is_child = os.environ.get("PYISOLATE_CHILD") == "1"
print(f"📚 [IsolationTest] STARTUP: isolated={is_child}, pid={os.getpid()}", file=sys.stderr, flush=True)

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
