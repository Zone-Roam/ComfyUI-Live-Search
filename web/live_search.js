import { app } from "../../scripts/app.js";

// Model configurations for API Loader
const API_LOADER_MODEL_CONFIGS = {
    "OpenAI": [
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
    "DeepSeek (Official)": [
        "deepseek-chat",
        "deepseek-reasoner",
        "deepseek-v3"
    ],
    "DeepSeek (Aliyun)": [
        "deepseek-v3",
        "deepseek-v2.5",
        "deepseek-chat"
    ],
    "Gemini (OpenAI-Format)": [
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
    "Anthropic (Claude)": [
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-5",
        "claude-haiku-4-5-20251001",
        "claude-haiku-4-5",
        "claude-opus-4-1-20250805",
        "claude-opus-4-1"
    ],
    "Grok": [
        "grok-2-1212",
        "grok-2-vision-1212",
        "grok-2",
        "grok-beta"
    ],
    "Volcengine (Doubao)": [
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
    "Qwen (Aliyun)": [
        "qwen3-max",
        "qwen3-max-preview",
        "qwen-plus",
        "qwen-plus-latest",
        "qwen-flash",
        "qwen-max",
        "qwen-turbo"
    ],
    "SiliconFlow (硅基流动)": [
        "deepseek-chat",
        "deepseek-reasoner",
        "deepseek-v3",
        "Qwen/Qwen2.5-72B-Instruct",
        "Qwen/Qwen2.5-32B-Instruct",
        "Qwen/Qwen2.5-14B-Instruct",
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "Qwen/QVQ-72B-Preview",
        "Qwen/Qwen-VL-72B-Instruct",
        "meta-llama/Llama-3.1-70B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct",
        "meta-llama/Llama-3-70B-Instruct",
        "meta-llama/Llama-3-8B-Instruct",
        "01-ai/Yi-1.5-34B-Chat",
        "01-ai/Yi-1.5-9B-Chat",
        "01-ai/Yi-1.5-6B-Chat",
        "THUDM/glm-4-9b-chat",
        "THUDM/glm-4-9b-chat-1m",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "internlm/internlm2_5-20b-chat",
        "internlm/internlm2_5-7b-chat"
    ],
    "Ollama (Local)": [
        "llama4",
        "llama3.3",
        "llama3.2",
        "qwen3",
        "qwen2.5",
        "deepseek-r1",
        "deepseek-v3",
        "phi4"
    ],
    "Custom": [
        "custom-model"
    ]
};

app.registerExtension({
    name: "ComfyUI.LiveSearch.ModelSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Helper function to setup provider-model linkage
        function setupProviderModelLink(node, configMap) {
            const providerWidget = node.widgets.find(w => w.name === "provider");
            const modelWidget = node.widgets.find(w => w.name === "model");
            
            if (providerWidget && modelWidget) {
                // Store original callback
                const originalCallback = providerWidget.callback;
                
                // Override provider widget callback
                providerWidget.callback = function(value) {
                    // Call original callback if exists
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    
                    // Update model dropdown options
                    const models = configMap[value] || configMap["DeepSeek (Official)"];
                    modelWidget.options.values = models;
                    
                    // Set default model for the provider
                    if (models.length > 0) {
                        modelWidget.value = models[0];
                    }
                    
                    // Force UI update
                    if (app.graph) {
                        app.graph.setDirtyCanvas(true);
                    }
                };
                
                // Initialize with default provider
                const initialModels = configMap[providerWidget.value] || configMap["DeepSeek (Official)"];
                modelWidget.options.values = initialModels;
                if (initialModels.length > 0 && !initialModels.includes(modelWidget.value)) {
                    modelWidget.value = initialModels[0];
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

