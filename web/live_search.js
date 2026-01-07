import { app } from "../../scripts/app.js";

// Model configurations for API Loader
const API_LOADER_MODEL_CONFIGS = {
    "智谱AI": {
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
        "t2t_models": [
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek-v3"
        ],
        "ti2t_models": []
    },
    "DeepSeek (Aliyun)": {
        "t2t_models": [
            "deepseek-v3",
            "deepseek-v2.5",
            "deepseek-chat"
        ],
        "ti2t_models": []
    },
    "Gemini (OpenAI-Format)": {
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
        "ti2t_models": []
    },
    "Anthropic (Claude)": {
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
        "t2t_models": [
            "grok-2-1212",
            "grok-2-vision-1212",
            "grok-2",
            "grok-beta"
        ],
        "ti2t_models": []
    },
    "Volcengine (Doubao)": {
        "t2t_models": [
            "doubao-seed-1-6-251015",
            "doubao-seed-1-6-250615",
            "doubao-seed-1-6-lite-251015",
            "doubao-seed-1-6-flash-250828",
            "doubao-seed-1-6-thinking-250715",
            "doubao-seed-code-preview-251028",
            "doubao-seed-1-6-vision-250815",
            "deepseek-v3-1-terminus",
            "deepseek-v3-1-250821",
            "custom-endpoint-id"
        ],
        "ti2t_models": []
    },
    "Qwen (Aliyun)": {
        "t2t_models": [
            "qwen3-max",
            "qwen3-max-preview",
            "qwen-plus",
            "qwen-plus-latest",
            "qwen-flash",
            "qwen-max",
            "qwen-turbo"
        ],
        "ti2t_models": []
    },
    "SiliconFlow (硅基流动)": {
        "t2t_models": [
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
            "zai-org/glm-4.6",
            "zai-org/glm-4.5-Air",
            "zai-org/glm-4.5",
            "THUDM/glm-Z1-32B-0414",
            "THUDM/glm-4-32B-0414",
            "THUDM/glm-Z1-Rumination-32B-0414",
            "THUDM/glm-4-9B-0414",
            "THUDM/glm-4-9b-chat",
            "Pro/THUDM/glm-4-9b-chat",
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
            "deepseek-ai/DeepSeek-OCR",
            "deepseek-ai/deepseek-vl2",
            "Qwen/Qwen3-VL-32B-Instruct",
            "Qwen/Qwen3-VL-32B-Thinking",
            "Qwen/Qwen3-VL-8B-Instruct",
            "Qwen/Qwen3-VL-8B-Thinking",
            "Qwen/Qwen3-VL-30B-A3B-Instruct",
            "Qwen/Qwen3-VL-30B-A3B-Thinking",
            "Qwen/Qwen3-VL-235B-A22B-Instruct",
            "Qwen/Qwen3-VL-235B-A22B-Thinking",
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Qwen/Qwen2.5-VL-72B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
            "Qwen/Qwen2-VL-72B-Instruct",
            "Qwen/Qwen3-Omni-30B-A3B-Instruct",
            "Qwen/Qwen3-Omni-30B-A3B-Thinking",
            "Qwen/Qwen3-Omni-30B-A3B-Captioner",
            "Qwen/QVQ-72B-Preview",
            "zai-org/glm-4.5V",
            "Pro/THUDM/glm-4.1V-9B-Thinking",
            "THUDM/glm-4.1V-9B-Thinking"
        ]
    },
    "Ollama (Local)": {
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
        "t2t_models": ["custom-model"],
        "ti2t_models": ["custom-vlm-model"]
    }
};

app.registerExtension({
    name: "ComfyUI.LiveSearch.ModelSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Helper function to setup provider-model linkage for both T2T and TI2T models
        function setupProviderModelLink(node, configMap) {
            const providerWidget = node.widgets.find(w => w.name === "provider");
            const t2tModelWidget = node.widgets.find(w => w.name === "t2t_model");
            const ti2tModelWidget = node.widgets.find(w => w.name === "ti2t_model");
            
            if (providerWidget && t2tModelWidget && ti2tModelWidget) {
                // Store original callback
                const originalCallback = providerWidget.callback;
                
                // Override provider widget callback
                providerWidget.callback = function(value) {
                    // Call original callback if exists
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    
                    // Default to empty config if provider not found
                    const config = configMap[value] || configMap["DeepSeek (Official)"] || {};
                    const t2tModels = config.t2t_models || [];
                    const ti2tModels = config.ti2t_models || [];
                    
                    // Update both model dropdown options
                    // Important: Set options first before setting value
                    t2tModelWidget.options.values = t2tModels.length > 0 ? t2tModels : ["No T2T models available"];
                    ti2tModelWidget.options.values = ti2tModels.length > 0 ? ti2tModels : ["No VLM models available"];
                    
                    // Set default models for the provider
                    if (t2tModels.length > 0) {
                        t2tModelWidget.value = t2tModels[0];
                    } else {
                        t2tModelWidget.value = "No T2T models available";
                    }
                    
                    if (ti2tModels.length > 0) {
                        ti2tModelWidget.value = ti2tModels[0];
                    } else {
                        ti2tModelWidget.value = "No VLM models available";
                    }
                    
                    // Force UI update
                    if (app.graph) {
                        app.graph.setDirtyCanvas(true);
                    }
                };
                
                // Initialize with default provider
                const provider = providerWidget.value;
                // Default to empty config if provider not found
                const config = configMap[provider] || configMap["DeepSeek (Official)"] || {};
                const t2tModels = config.t2t_models || [];
                const ti2tModels = config.ti2t_models || [];
                
                t2tModelWidget.options.values = t2tModels.length > 0 ? t2tModels : ["No T2T models available"];
                ti2tModelWidget.options.values = ti2tModels.length > 0 ? ti2tModels : ["No VLM models available"];
                
                if (t2tModels.length > 0 && !t2tModels.includes(t2tModelWidget.value)) {
                    t2tModelWidget.value = t2tModels[0];
                } else if (t2tModels.length === 0) {
                    t2tModelWidget.value = "No T2T models available";
                }
                
                if (ti2tModels.length > 0 && !ti2tModels.includes(ti2tModelWidget.value)) {
                    ti2tModelWidget.value = ti2tModels[0];
                } else if (ti2tModels.length === 0) {
                    ti2tModelWidget.value = "No VLM models available";
                }
            }
        }
        
        // Apply to new API Loader node
        if (nodeData.name === "LiveSearch_API_Loader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                setupProviderModelLink(this, API_LOADER_MODEL_CONFIGS);
                return result;
            };
        }
    }
});
