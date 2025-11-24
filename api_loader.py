"""
LiveSearch API Loader Node
Handles LLM API configuration separately from the main search logic
"""

import os
from .config_manager import ConfigManager

config_manager = ConfigManager()

# Expanded model configurations
MODEL_CONFIGS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini"
        ]
    },
    "DeepSeek (Official)": {
        "base_url": "https://api.deepseek.com",
        "models": [
            "deepseek-chat",
            "deepseek-reasoner"
        ]
    },
    "DeepSeek (Aliyun)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            "deepseek-v3",
            "deepseek-v2.5",
            "deepseek-chat"
        ]
    },
    "DeepSeek (Volcengine)": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            "deepseek-chat",
            "deepseek-v3"
        ]
    },
    "Gemini (OpenAI-Format)": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]
    },
    "Anthropic (Claude)": {
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229"
        ]
    },
    "Grok": {
        "base_url": "https://api.x.ai/v1",
        "models": [
            "grok-2-1212",
            "grok-2-vision-1212",
            "grok-beta"
        ]
    },
    "Volcengine (Doubao)": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            "doubao-1.5-pro-32k",
            "doubao-1.5-pro-256k",
            "doubao-1.5-lite",
            "doubao-1.5-vision-pro",
            "doubao-1.5-thinking-pro",
            "doubao-pro-32k",
            "doubao-lite-32k",
            "deepseek-v3.1",
            "deepseek-r1",
            "deepseek-v3",
            "kimi-k2"
        ]
    },
    "Qwen (Aliyun)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            "qwen-max",
            "qwen-plus",
            "qwen-turbo"
        ]
    },
    "Ollama (Local)": {
        "base_url": "http://127.0.0.1:11434/v1",
        "models": [
            "llama3.3",
            "llama3.2",
            "qwen2.5",
            "deepseek-r1",
            "phi4"
        ]
    },
    "Custom": {
        "base_url": "",
        "models": ["custom-model"]
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
        
        # Get all unique models
        all_models = []
        for config in MODEL_CONFIGS.values():
            all_models.extend(config["models"])
        unique_models = list(dict.fromkeys(all_models))  # Preserve order, remove duplicates
        
        return {
            "required": {
                "provider": (providers, {"default": "DeepSeek (Official)"}),
                "model": (unique_models, {"default": "deepseek-chat"}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "placeholder": "Leave empty to use .env or config file"}),
                "base_url": ("STRING", {"default": "", "placeholder": "Leave empty to use default"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 128000, "step": 1}),
                "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            }
        }
    
    RETURN_TYPES = ("LLM_CONFIG",)
    RETURN_NAMES = ("llm_config",)
    FUNCTION = "load_api"
    CATEGORY = "LiveSearch"
    
    def load_api(self, provider, model, api_key="", base_url="", temperature=0.7, max_tokens=2048, timeout=120):
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
        
        # Special handling for Aliyun providers
        if provider == "DeepSeek (Aliyun)" and model == "deepseek-chat":
            model = "deepseek-v3"
        
        # Build configuration dict
        llm_config = {
            "provider": provider,
            "model": model,
            "api_key": resolved_api_key,
            "base_url": resolved_base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout
        }
        
        print(f"[LiveSearch API Loader] Configured: {provider} / {model}")
        
        return (llm_config,)

NODE_CLASS_MAPPINGS = {
    "LiveSearch_API_Loader": LiveSearch_API_Loader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_API_Loader": "🔑 Live Search API Loader"
}

