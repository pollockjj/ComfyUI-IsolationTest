from __future__ import annotations

import logging
from typing import Awaitable, Callable

from comfy_api.latest import ComfyExtension, IO

from .packages.pyisolated_v3 import comfy_entrypoint as pyisolated_v3_entrypoint

logger = logging.getLogger(__name__)


async def _collect_nodes(
    label: str,
    entrypoint: Callable[[], Awaitable[ComfyExtension]],
) -> list[type[IO.ComfyNode]]:
    try:
        extension = await entrypoint()
        return await extension.get_node_list()
    except Exception:
        logger.warning(
            "][ ComfyUI-IsolationTest skipped bundle '%s' due to import/runtime error",
            label,
            exc_info=True,
        )
        return []


class IsolationTestExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        node_list: list[type[IO.ComfyNode]] = []
        node_list.extend(
            await _collect_nodes("pyisolated_v3", pyisolated_v3_entrypoint)
        )
        return node_list


async def comfy_entrypoint() -> IsolationTestExtension:
    return IsolationTestExtension()
