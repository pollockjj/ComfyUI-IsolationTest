from __future__ import annotations

from comfy_api.latest import ComfyExtension, IO

from .nodes_ace import AceExtension_ISO
from .nodes_advanced_samplers import AdvancedSamplersExtension_ISO
from .nodes_align_your_steps import AlignYourStepsExtension_ISO
from .nodes_apg import ApgExtension_ISO
from .nodes_attention_multiply import AttentionMultiplyExtension_ISO
from .nodes_audio_encoder import AudioEncoder_ISO
from .nodes_camera_trajectory import CameraTrajectoryExtension_ISO
from .nodes_canny import CannyExtension_ISO
from .nodes_cfg import CfgExtension_ISO
from .nodes_chroma_radiance import ChromaRadianceExtension_ISO
from .nodes_clip_sdxl import ClipSdxlExtension_ISO
from .nodes_compositing import CompositingExtension_ISO
from .nodes_cond import CondExtension_ISO
from .nodes_context_windows import ContextWindowsExtension_ISO
from .nodes_controlnet import ControlNetExtension_ISO
from .nodes_cosmos import CosmosExtension_ISO
from .nodes_custom_sampler import CustomSamplersExtension_ISO
from .nodes_dataset import DatasetExtension_ISO
from .nodes_differential_diffusion import DifferentialDiffusionExtension_ISO
from .nodes_easycache import EasyCacheExtension_ISO
from .nodes_edit_model import EditModelExtension_ISO
from .nodes_eps import EpsilonScalingExtension_ISO
from .nodes_flux import FluxExtension_ISO
from .nodes_fresca import FreScaExtension_ISO
from .nodes_gits import GITSSchedulerExtension_ISO
from .nodes_hidream import HiDreamExtension_ISO
from .nodes_hunyuan import HunyuanExtension_ISO
from .nodes_hunyuan3d import Hunyuan3dExtension_ISO
from .nodes_hypernetwork import HyperNetworkExtension_ISO
from .nodes_hypertile import HyperTileExtension_ISO
from .nodes_ip2p import InstructPix2PixExtension_ISO
from .nodes_latent import LatentExtension_ISO
from .nodes_logic import LogicExtension_ISO
from .nodes_lora_extract import LoraSaveExtension_ISO
from .nodes_lotus import LotusExtension_ISO
from .nodes_lt import LtxvExtension_ISO
from .nodes_lumina2 import Lumina2Extension_ISO
from .nodes_mahiro import MahiroExtension_ISO
from .nodes_mochi import MochiExtension_ISO
from .nodes_model_passthrough import ModelPassthroughExtension_ISO
from .nodes_model_downscale import ModelDownscaleExtension_ISO
from .nodes_morphology import MorphologyExtension_ISO
from .nodes_nop import NopExtension_ISO
from .nodes_optimalsteps import OptimalStepsExtension_ISO
from .nodes_pag import PAGExtension_ISO
from .nodes_perpneg import PerpNegExtension_ISO
from .nodes_photomaker import PhotomakerExtension_ISO
from .nodes_pixart import PixArtExtension_ISO
from .nodes_post_processing import PostProcessingExtension_ISO
from .nodes_primitive import PrimitivesExtension_ISO
from .nodes_qwen import QwenExtension_ISO
from .nodes_rebatch import RebatchExtension_ISO
from .nodes_rope import RopeExtension_ISO
from .nodes_sag import SagExtension_ISO
from .nodes_sd3 import SD3Extension_ISO
from .nodes_sdupscale import SdUpscaleExtension_ISO
from .nodes_slg import SkipLayerGuidanceExtension_ISO
from .nodes_stable3d import Stable3DExtension_ISO
from .nodes_stable_cascade import StableCascadeExtension_ISO
from .nodes_string import StringExtension_ISO
from .nodes_tcfg import TcfgExtension_ISO
from .nodes_tomesd import TomePatchModelExtension_ISO
from .nodes_torch_compile import TorchCompileExtension_ISO
from .nodes_train import TrainingExtension_ISO
from .nodes_upscale_model import UpscaleModelExtension_ISO
from .nodes_vae_clip_basic import VaeClipBasicExtension_ISO
from .nodes_video import VideoExtension_ISO
from .nodes_wan import WanExtension_ISO

__all__ = ['comfy_entrypoint']

class CompositeIsolationTestExtension(ComfyExtension):
    def __init__(self):
        self.extensions = []
    
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        nodes = []
        for ext in self.extensions:
            nodes.extend(await ext.get_node_list())
        return nodes

async def comfy_entrypoint():
    composite = CompositeIsolationTestExtension()
    composite.extensions = [
        AceExtension_ISO(),
        AdvancedSamplersExtension_ISO(),
        AlignYourStepsExtension_ISO(),
        ApgExtension_ISO(),
        AttentionMultiplyExtension_ISO(),
        CameraTrajectoryExtension_ISO(),
        CannyExtension_ISO(),
        CfgExtension_ISO(),
        ChromaRadianceExtension_ISO(),
        ClipSdxlExtension_ISO(),
        CompositingExtension_ISO(),
        CondExtension_ISO(),
        ContextWindowsExtension_ISO(),
        ControlNetExtension_ISO(),
        CosmosExtension_ISO(),
        CustomSamplersExtension_ISO(),
        DatasetExtension_ISO(),
        DifferentialDiffusionExtension_ISO(),
        EasyCacheExtension_ISO(),
        EditModelExtension_ISO(),
        EpsilonScalingExtension_ISO(),
        FluxExtension_ISO(),
        FreScaExtension_ISO(),
        GITSSchedulerExtension_ISO(),
        HiDreamExtension_ISO(),
        HunyuanExtension_ISO(),
        Hunyuan3dExtension_ISO(),
        HyperNetworkExtension_ISO(),
        HyperTileExtension_ISO(),
        InstructPix2PixExtension_ISO(),
        LatentExtension_ISO(),
        LogicExtension_ISO(),
        LoraSaveExtension_ISO(),
        LotusExtension_ISO(),
        LtxvExtension_ISO(),
        Lumina2Extension_ISO(),
        MahiroExtension_ISO(),
        MochiExtension_ISO(),
        ModelPassthroughExtension_ISO(),
        ModelDownscaleExtension_ISO(),
        MorphologyExtension_ISO(),
        NopExtension_ISO(),
        OptimalStepsExtension_ISO(),
        PAGExtension_ISO(),
        PerpNegExtension_ISO(),
        PhotomakerExtension_ISO(),
        PixArtExtension_ISO(),
        PostProcessingExtension_ISO(),
        PrimitivesExtension_ISO(),
        QwenExtension_ISO(),
        RebatchExtension_ISO(),
        RopeExtension_ISO(),
        SagExtension_ISO(),
        SD3Extension_ISO(),
        SdUpscaleExtension_ISO(),
        SkipLayerGuidanceExtension_ISO(),
        Stable3DExtension_ISO(),
        StableCascadeExtension_ISO(),
        StringExtension_ISO(),
        TcfgExtension_ISO(),
        TomePatchModelExtension_ISO(),
        TorchCompileExtension_ISO(),
        TrainingExtension_ISO(),
        UpscaleModelExtension_ISO(),
        VaeClipBasicExtension_ISO(),
        VideoExtension_ISO(),
        WanExtension_ISO(),
    ]
    return composite