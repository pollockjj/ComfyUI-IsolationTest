from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import List, Type

from comfy_api.latest import ComfyExtension, io

# V1 exports (kept for existing tests)
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = [
	"NODE_CLASS_MAPPINGS",
	"NODE_DISPLAY_NAME_MAPPINGS",
	"Extension",
]


# --- V3 support: load per-module wrappers from v3_nodes/ ---
_V3_DIR = Path(__file__).parent / "v3_nodes"


def _load_module(path: Path):
	name = f"comfyui_isolationtest_v3_{path.stem}"
	spec = importlib.util.spec_from_file_location(name, path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Unable to load module spec for {path}")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def _discover_v3_nodes() -> List[Type[io.ComfyNode]]:
	nodes: List[Type[io.ComfyNode]] = []
	for path in sorted(_V3_DIR.glob("*.py")):
		if path.name.startswith("__"):
			continue
		mod = _load_module(path)
		for cls_name in getattr(mod, "__all__", []):
			cls = getattr(mod, cls_name, None)
			if cls is not None:
				try:
					# Validate schema eagerly; skip nodes whose original schema is incomplete
					cls.define_schema()
				except Exception as e:
					# Fail loud in logs but do not crash load; skip incompatible nodes
					import logging
					logging.getLogger(__name__).warning(
						"Skipping V3 node %s from %s: %s", cls_name, path.name, e
					)
					continue
				nodes.append(cls)
	return nodes


class Extension(ComfyExtension):
	async def on_load(self) -> None:  # noqa: D401
		return None

	async def get_node_list(self) -> list[type[io.ComfyNode]]:
		return _discover_v3_nodes()
