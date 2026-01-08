"""
LiveSearch API Loader Node
Handles LLM API configuration separately from the main search logic
"""

import os
from .config_manager import ConfigManager

config_manager = ConfigManager()

# Expanded model configurations
# 每个 provider 包含 base_url、t2t_models（文本模型）、ti2t_models（视觉模型）
MODEL_CONFIGS = {
    "智谱AI": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "t2t_models": [
            "glm-4.5-Flash",
            "glm-4-Flash-250414",
            "glm-Z1-Flash"
        ],
        "ti2t_models": [
            "glm-4.6V-Flash",
            "glm-4V-Flash",
            "glm-4.1V-Thinking-Flash"
        ]
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "t2t_models": [
            "gpt-5.1",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-5-pro",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o3",
            "o3-pro",
            "o3-mini",
            "o3-deep-research",
            "o4-mini-deep-research",
            "o1",
            "o1-pro"
        ],
        "ti2t_models": [
            # OpenAI 视觉模型（使用 OpenAI 兼容格式，与 SiliconFlow 相同）
            "gpt-5.1",
            "gpt-5.1-mini",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-pro",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ]
    },
    "DeepSeek (Official)": {
        "base_url": "https://api.deepseek.com",
        "t2t_models": [
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek-v3"
        ],
        "ti2t_models": []
    },
    "DeepSeek (Aliyun)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "t2t_models": [
            "deepseek-v3",
            "deepseek-v2.5",
            "deepseek-chat"
        ],
        "ti2t_models": []
    },
    "Gemini (OpenAI-Format)": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "t2t_models": [
            "gemini-3-pro",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ],
        "ti2t_models": [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash-live"
        ]
    },
    "Anthropic (Claude)": {
        "base_url": "https://api.anthropic.com/v1",
        "t2t_models": [
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-5",
            "claude-haiku-4-5-20251001",
            "claude-haiku-4-5",
            "claude-opus-4-1-20250805",
            "claude-opus-4-1"
        ],
        "ti2t_models": []
    },
    "Grok": {
        "base_url": "https://api.x.ai/v1",
        "t2t_models": [
            "grok-2-1212",
            "grok-2-vision-1212",
            "grok-2",
            "grok-beta"
        ],
        "ti2t_models": []
    },
    "Volcengine (Doubao)": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "t2t_models": [
            # 豆包主力模型 (Model ID)
            "doubao-seed-1-6-251015",      # doubao-seed-1.6 (最新)
            "doubao-seed-1-6-250615",      # doubao-seed-1.6 (稳定)
            "doubao-seed-1-6-lite-251015", # doubao-seed-1.6-lite
            "doubao-seed-1-6-flash-250828",# doubao-seed-1.6-flash
            "doubao-seed-1-6-thinking-250715", # doubao-seed-1.6-thinking
            "doubao-seed-code-preview-251028", # doubao-seed-code
            "doubao-seed-1-6-vision-250815",   # doubao-seed-1.6-vision
            # DeepSeek (火山引擎托管)
            "deepseek-v3-1-terminus",
            "deepseek-v3-1-250821",
            # 第三方兼容 (如需自定义)
            "custom-endpoint-id"
        ],
        "ti2t_models": []
    },
    "Qwen (Aliyun)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "t2t_models": [
            "qwen3-max",
            "qwen3-max-preview",
            "qwen-plus",
            "qwen-plus-latest",
            "qwen-flash",
            "qwen-max",
            "qwen-turbo"
        ],
        "ti2t_models": [
            "qwen3-vl-flash",
            "qwen3-vl-flash-2025-10-15",
            "qwen3-vl-plus",
            "qwen3-vl-plus-2025-09-23"
        ]
    },
    "SiliconFlow (硅基流动)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "t2t_models": [
            # DeepSeek 系列
            "deepseek-ai/DeepSeek-V3.2-Exp",
            "Pro/deepseek-ai/DeepSeek-V3.2-Exp",
            "Pro/deepseek-ai/DeepSeek-V3.1-Terminus",
            "deepseek-ai/DeepSeek-V3.1-Terminus",
            "Pro/deepseek-ai/DeepSeek-R1",
            "Pro/deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "deepseek-ai/DeepSeek-V2.5",
            # Qwen 系列
            "Qwen/Qwen3-Next-80B-A3B-Instruct",
            "Qwen/Qwen3-Next-80B-A3B-Thinking",
            "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "Qwen/Qwen3-Coder-480B-A35B-Instruct",
            "Qwen/Qwen3-30B-A3B-Thinking-2507",
            "Qwen/Qwen3-30B-A3B-Instruct-2507",
            "Qwen/Qwen3-235B-A22B-Thinking-2507",
            "Qwen/Qwen3-235B-A22B-Instruct-2507",
            "Qwen/Qwen3-30B-A3B",
            "Qwen/Qwen3-32B",
            "Qwen/Qwen3-14B",
            "Qwen/Qwen3-8B",
            "Qwen/Qwen3-235B-A22B",
            "Qwen/Qwen2.5-72B-Instruct-128K",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Qwen/Qwen2-7B-Instruct",
            "Qwen/QwQ-32B",
            "Pro/Qwen/Qwen2.5-7B-Instruct",
            "Pro/Qwen/Qwen2-7B-Instruct",
            # glm 系列（智谱）
            "zai-org/glm-4.6",
            "zai-org/glm-4.5-Air",
            "zai-org/glm-4.5",
            "THUDM/glm-Z1-32B-0414",
            "THUDM/glm-4-32B-0414",
            "THUDM/glm-Z1-Rumination-32B-0414",
            "THUDM/glm-4-9B-0414",
            "THUDM/glm-4-9b-chat",
            "Pro/THUDM/glm-4-9b-chat",
            # 其他模型
            "inclusionAI/Ling-1T",
            "inclusionAI/Ring-flash-2.0",
            "inclusionAI/Ling-flash-2.0",
            "inclusionAI/Ling-mini-2.0",
            "moonshotai/Kimi-K2-Instruct-0905",
            "ByteDance-Seed/Seed-OSS-36B-Instruct",
            "stepfun-ai/step3",
            "baidu/ERNIE-4.5-300B-A47B",
            "ascend-tribe/pangu-pro-moe",
            "tencent/Hunyuan-A13B-Instruct",
            "MiniMaxAI/MiniMax-M1-80k",
            "Tongyi-Zhiwen/QwenLong-L1-32B",
            "internlm/internlm2_5-7b-chat"
        ],
        "ti2t_models": [
            # DeepSeek VLM 系列
            "deepseek-ai/DeepSeek-OCR",
            "deepseek-ai/deepseek-vl2",
            # Qwen3 VL 系列
            "Qwen/Qwen3-VL-32B-Instruct",
            "Qwen/Qwen3-VL-32B-Thinking",
            "Qwen/Qwen3-VL-8B-Instruct",
            "Qwen/Qwen3-VL-8B-Thinking",
            "Qwen/Qwen3-VL-30B-A3B-Instruct",
            "Qwen/Qwen3-VL-30B-A3B-Thinking",
            "Qwen/Qwen3-VL-235B-A22B-Instruct",
            "Qwen/Qwen3-VL-235B-A22B-Thinking",
            # Qwen2.5 VL 系列
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Qwen/Qwen2.5-VL-72B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
            # Qwen2 VL 系列
            "Qwen/Qwen2-VL-72B-Instruct",
            # Qwen3 Omni 系列
            "Qwen/Qwen3-Omni-30B-A3B-Instruct",
            "Qwen/Qwen3-Omni-30B-A3B-Thinking",
            "Qwen/Qwen3-Omni-30B-A3B-Captioner",
            # QVQ 系列
            "Qwen/QVQ-72B-Preview",
            # glm V 系列（视觉）
            "zai-org/glm-4.5V",
            "Pro/THUDM/glm-4.1V-9B-Thinking",
            "THUDM/glm-4.1V-9B-Thinking"
        ]
    },
    "Ollama (Local)": {
        "base_url": "http://127.0.0.1:11434/v1",
        "t2t_models": [
            "huihui_ai/qwen3-vl-abliterated:8b-instruct",
            "huihui_ai/qwen3-vl-abliterated:4b-instruct",
            "llama4",
            "llama3.3",
            "llama3.2",
            "qwen3",
            "qwen2.5",
            "deepseek-r1",
            "deepseek-v3",
            "phi4"
        ],
        "ti2t_models": [
            "huihui_ai/qwen3-vl-abliterated:8b-instruct",
            "huihui_ai/qwen3-vl-abliterated:4b-instruct"
        ]
    },
    "Custom": {
        "base_url": "",
        "t2t_models": ["custom-model"],
        "ti2t_models": ["custom-vlm-model"]
    }
}

class LiveSearch_API_Loader:
    """
    API Configuration Loader Node
    Separated from main search logic for better organization
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        # Get all providers
        providers = list(MODEL_CONFIGS.keys())
        
        # Get all unique models for T2T
        all_t2t_models = []
        for config in MODEL_CONFIGS.values():
            all_t2t_models.extend(config.get("t2t_models", []))
        unique_t2t_models = list(dict.fromkeys(all_t2t_models))
        # Add placeholder for validation when list is empty in frontend
        unique_t2t_models.append("No T2T models available")
        
        # Get all unique models for TI2T
        all_ti2t_models = []
        for config in MODEL_CONFIGS.values():
            all_ti2t_models.extend(config.get("ti2t_models", []))
        unique_ti2t_models = list(dict.fromkeys(all_ti2t_models))
        # Add placeholder for validation when list is empty in frontend
        unique_ti2t_models.append("No VLM models available")
        
        return {
            "required": {
                "provider": (providers, {"default": "DeepSeek (Official)"}),
                "t2t_model": (unique_t2t_models, {"default": "deepseek-chat"}),
                "ti2t_model": (unique_ti2t_models, {"default": "Qwen/Qwen2.5-VL-72B-Instruct"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "placeholder": "Leave empty to use .env or config file"}),
                "base_url": ("STRING", {"default": "", "placeholder": "Leave empty to use default"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 128000, "step": 1}),
                "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            }
        }
    
    RETURN_TYPES = ("MODEL_CONFIG",)
    RETURN_NAMES = ("model_config",)
    FUNCTION = "load_api"
    CATEGORY = "LiveSearch"
    
    def load_api(self, provider, t2t_model, ti2t_model, api_key="", base_url="", temperature=0.7, max_tokens=2048, timeout=120):
        """
        Load and validate API configuration
        Returns a config dict that can be passed to other nodes
        """
        # Resolve API key with priority: input > env > config file
        resolved_api_key = api_key.strip() if api_key else ""
        if not resolved_api_key:
            resolved_api_key = config_manager.get_api_key(provider, "")
        
        # Resolve base URL
        resolved_base_url = base_url.strip() if base_url else MODEL_CONFIGS.get(provider, {}).get("base_url", "")
        
        # Build configuration dict (包含两个模型，由 Agent 根据 mode 选择)
        model_config = {
            "provider": provider,
            "t2t_model": t2t_model,
            "ti2t_model": ti2t_model,
            "api_key": resolved_api_key,
            "base_url": resolved_base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout
        }
        
        print(f"[LiveSearch API Loader] Configured: {provider} / T2T: {t2t_model} / TI2T: {ti2t_model}")
        
        return (model_config,)

NODE_CLASS_MAPPINGS = {
    "LiveSearch_API_Loader": LiveSearch_API_Loader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_API_Loader": "🔑 Live Search API Loader"
}

