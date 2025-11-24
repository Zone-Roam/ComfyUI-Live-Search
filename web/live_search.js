import { app } from "../../scripts/app.js";

// Model configurations matching Python MODEL_CONFIGS (Legacy Node)
const LEGACY_MODEL_CONFIGS = {
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini"
    ],
    "DeepSeek (Official)": [
        "deepseek-chat",
        "deepseek-reasoner"
    ],
    "DeepSeek (Aliyun)": [
        "deepseek-v3",
        "deepseek-v2.5",
        "deepseek-chat"
    ],
    "Volcengine (Doubao)": [
        "doubao-1.5-pro-32k",
        "doubao-1.5-lite",
        "doubao-pro-32k",
        "doubao-lite-32k",
        "deepseek-v3",
        "deepseek-r1",
        "kimi-k2"
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
    "Custom": [
        "custom-model"
    ]
};

// Model configurations for API Loader (New Architecture)
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
        "doubao-seed-1.6",
        "doubao-seed-1.6-lite",
        "doubao-seed-1.6-flash",
        "doubao-seed-1.6-thinking",
        "doubao-seed-code",
        "doubao-seed-translation",
        "doubao-seed-1.6-vision",
        "deepseek-v3.1",
        "deepseek-r1",
        "deepseek-v3",
        "kimi-k2"
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
        
        // Apply to Legacy node
        if (nodeData.name === "LiveSearchNode") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                setupProviderModelLink(this, LEGACY_MODEL_CONFIGS);
                return result;
            };
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

