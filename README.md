<div align="center">

# 🌐 Live Search - Real-time Web Search for ComfyUI

**Connect Your ComfyUI to the Internet | Search, Scrape, Summarize**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-8%2B_Providers-orange)](https://github.com/Zone-Roam/ComfyUI-Live-Search)

**🔥 Use Cases**: Real-time Weather · News Summary · Fact Checking · Product Reviews · Web Scraping

**🤖 Supported Models**: GPT-5.1 · DeepSeek-V3 · Gemini 3 Pro · Claude 4.5 · Qwen3 · Llama 4 · Ollama

[中文文档](README_CN.md) | [English](README.md)

</div>

---

## 📖 Why Choose Live Search?

**ComfyUI Live Search** brings the internet directly to your workflows! This powerful **internet search node** provides:

✅ **Real-time Search**: DuckDuckGo search engine, stable and reliable  
✅ **AI Summarization**: Automatically reads web pages and extracts key information  
✅ **Multi-LLM Support**: GPT-5.1, DeepSeek-V3, Gemini 3 Pro, Claude 4.5, Qwen3, and 8+ LLM providers  
✅ **Modular Architecture**: Separated API config, search settings, and execution logic  
✅ **Chinese-Friendly**: Perfect support for Chinese LLM providers (Qwen, Doubao, DeepSeek)

**Typical Use Cases**:
- 🌤️ Query real-time weather to generate scene images
- 📰 Fetch latest news and generate related content
- 🔍 Fact checking and information verification
- 🛍️ Product information lookup and review summarization
- 🌐 Any creative workflow requiring internet information

## 🏗️ New Modular Architecture

**Inspired by [comfyui_LLM_party](https://github.com/heshengtao/comfyui_LLM_party)'s excellent design**, we adopt a **modular layered architecture**:

### 📊 Node Composition

```
🔑 API Loader → ⚙️ Settings → 🌐 Search Agent → Results
```

| Node | Function | Output |
|------|----------|--------|
| **🔑 Live Search API Loader** | API config & model selection | LLM_CONFIG |
| **⚙️ Live Search Settings** | Search parameters | SEARCH_SETTINGS |
| **🌐 Live Search Agent** | Main search logic | answer, source_urls, optimized_prompt |

### ✅ New Architecture Benefits

- **Modular Design**: Separation of config and logic, easier to maintain
- **Reusability**: One API Loader can connect to multiple Agents
- **Flexibility**: Different Settings for different scenarios
- **Professional**: Best practices from large-scale projects

### 🔄 Backward Compatibility

- Legacy single-node `🌐 Live Search (Legacy)` still available
- New users recommended to use the new three-node combo

---

## ✨ Key Features

- **🔍 DuckDuckGo Search Engine**:
  - Stable and automation-friendly
  - No API key required, privacy-focused
  - Proxy support for various network environments
  - High-quality search results for real-time information retrieval
  
- **🧠 Multiple LLM Provider Support** (Latest 2025 Models):
  - **OpenAI**: GPT-5.1, GPT-5 series, GPT-4.1 series, GPT-4o series, O3 series reasoning models
  - **DeepSeek**: deepseek-v3, deepseek-chat, deepseek-reasoner (Official/Aliyun/Volcengine)
  - **Gemini**: gemini-3-pro, gemini-2.5 series, gemini-2.0 series, gemini-1.5 series
  - **Anthropic**: Claude 4.5 Sonnet/Haiku, Claude 4.1 Opus
  - **Volcengine (Doubao)**: doubao-1.5 series, deepseek-v3.1/r1, kimi-k2
  - **Qwen (Aliyun)**: qwen3-max, qwen-plus, qwen-flash (Aliyun Bailian)
  - **Grok**: grok-2 series (xAI Official)
  - **Local Deployment**: Ollama supports llama4, qwen3, deepseek-v3, phi4, etc.

- **🎯 Smart Features**:
  - **Prompt Optimization**: Optional LLM-powered search keyword refinement for better precision
  - **Multi-language Output**: Auto-detect, force Chinese, or force English output modes
  - **Modular Architecture**: Separated API config, search settings, and execution logic for flexibility

- **☁️ Cloud & Privacy Security**:
  - **API Key Safety**: Keys entered in nodes are **NOT saved to disk** (perfect for AutoDL, RunningHub shared environments)
  - **Local Config**: Supports both `.env` and `api_config.json` configuration methods
  - **Proxy Support**: Built-in proxy configuration for various network scenarios

## 🚀 Installation

### Method 1: via ComfyUI Manager (Recommended)

1. Open **Manager** panel in ComfyUI
2. Click **Install Custom Nodes**
3. Search for `Live Search`
4. Click **Install** and restart ComfyUI

### Method 2: Git Clone

Navigate to your ComfyUI `custom_nodes` directory and run:

```bash
git clone https://github.com/Zone-Roam/ComfyUI-Live-Search.git
cd ComfyUI-Live-Search

# If using Portable version of ComfyUI (Recommended)
..\..\..\python_embeded\python.exe -m pip install -r requirements.txt

# If using system Python or virtual environment
pip install -r requirements.txt
```

Then restart ComfyUI.

### Method 3: Manual Installation

1. Download the ZIP file
2. Extract it to `ComfyUI/custom_nodes/ComfyUI-Live-Search`
3. Install dependencies as shown in Method 2
4. Restart ComfyUI

## 🛠️ Usage Guide

### 📸 Workflow Example

The image below shows both usage methods:
- **Left**: Legacy single-node mode - Simple and fast, all configs in one node
- **Bottom right**: New modular architecture - API Loader + Settings + Agent, more flexible and reusable

![Workflow Example](images/workflow_example.png)

---

### Method 1: New Modular Architecture (Recommended) ⭐

#### 1. **🔑 Live Search API Loader**

Configure LLM API and model parameters.

| Parameter | Description |
|-----------|-------------|
| **provider** | Choose provider: OpenAI, DeepSeek, Gemini, Anthropic, Grok, Doubao, Qwen, Ollama, etc. |
| **model** | Select model from dropdown list |
| **api_key** | API key (optional, supports .env) |
| **base_url** | API endpoint (optional, uses default standard endpoints) |
| **temperature** | Temperature (0.0-2.0) |
| **max_tokens** | Maximum output length |
| **timeout** | Request timeout |

#### 2. **⚙️ Live Search Settings**

Configure search behavior.

| Parameter | Description |
|-----------|-------------|
| **num_results** | Number of search results (1-10) |
| **output_language** | Output language: Auto / 中文 / English |
| **optimize_prompt** | Whether to optimize search query |
| **proxy** | Proxy address (optional) |

#### 3. **🌐 Live Search Agent**

Main search node, connects to the above two nodes.

| Input | Type | Description |
|-------|------|-------------|
| **prompt** | STRING | Your question |
| **llm_config** | LLM_CONFIG | From API Loader |
| **search_settings** | SEARCH_SETTINGS | From Settings |

| Output | Description |
|--------|-------------|
| **answer** | AI-generated answer |
| **source_urls** | Referenced source links |
| **optimized_prompt** | Optimized search query |

---

### Method 2: Legacy Single-Node Mode

#### Node: **🌐 Live Search (Legacy)**

#### Input Parameters

| Parameter | Description |
| :--- | :--- |
| **prompt** | Your question. Supports both Chinese and English. e.g., *"What's the weather in Beijing?"* or *"北京现在的天气"* |
| **output_language** | 🌐 Output Language<br>• **Auto** (default): Automatically matches question language<br>• **中文**: Force Chinese output<br>• **English**: Force English output |
| **optimize_prompt** | 🔄 Prompt Optimization Toggle (Recommended ON)<br>• **OFF** (default): Use original input directly<br>• **ON**: LLM optimizes your question into precise search keywords<br>  - Preserves original language (CN→CN, EN→EN)<br>  - Removes redundant words, keeps core info<br>  - Outputs before/after comparison |
| **provider** | Choose your LLM provider: `OpenAI`, `DeepSeek (Official/Aliyun/Volcengine)`, `Gemini`, etc. |
| **model** | 🎯 Model Selection (Dropdown)<br>• **OpenAI**: gpt-5.1, gpt-5, gpt-4.1, o3, o3-pro, etc.<br>• **DeepSeek**: deepseek-v3, deepseek-chat, deepseek-reasoner<br>• **Gemini**: gemini-3-pro, gemini-2.5-pro, gemini-2.5-flash, etc.<br>• **Claude**: claude-sonnet-4-5, claude-haiku-4-5, etc.<br>• Supports search filtering for quick model lookup |
| **api_key** | (Optional) Your API Key. If left empty, it tries to load from config files. |
| **proxy** | (Optional) Proxy address like `http://127.0.0.1:7890`. Leave empty for direct connection. |

#### Outputs

| Output | Description |
| :--- | :--- |
| **answer** | AI-generated answer based on search results |
| **source_urls** | List of referenced web page links |
| **optimized_prompt** | Shows prompt optimization status (whether optimized, before/after comparison) |

#### Example Workflows

**1. Real-time Weather Image Generation**
- **Input**: `"What's the weather in Beijing?"`
- **Optimize**: `ON` ✅
- **Optimized**: `"Beijing weather now"`
- **Output**: "Currently 2:00 PM in Beijing, Sunny, 15°C."
- → [Connect to Text2Image] → Generate Beijing sunny street scene

**2. Fact Checking**
- **Input**: `"Who won the latest Super Bowl?"`
- **Optimize**: `ON` ✅
- **Output**: Accurate answer based on real-time results

**3. Cross-Language Query**
- **Input**: `"北京现在的天气"` (Chinese question)
- **Output Language**: `English` 🇺🇸
- **Optimize**: `ON` ✅
- **Output**: Beijing weather info (**answered in English**)

**4. International Collaboration**
- **Input**: `"What's the weather in Beijing?"` (English question)
- **Output Language**: `中文` 🇨🇳
- **Output**: Beijing weather info (**answered in Chinese**)

## 🔍 Why Only DuckDuckGo?

This node uses **real web scraping** for search, not API calls. In our testing:

**✅ DuckDuckGo Advantages**:
- Automation-friendly with lenient anti-bot measures
- Works reliably even with proxy configuration
- Search quality fully meets real-time information retrieval needs
- Open-source friendly with strong community support

**❌ Google Issues**:
- Extremely strict anti-scraping mechanisms (CAPTCHAs, IP blocks, User-Agent detection)
- Often returns empty results or CAPTCHA pages even with proxies
- `googlesearch-python` library is unstable in production
- Frequent access leads to temporary IP bans

**💡 If You Need Google Search Quality**:
- Consider using official **Google Custom Search API** (paid)
- Or use third-party services like **SerpAPI** (paid)

We chose DuckDuckGo to ensure the node works **reliably** across all environments.

---

## 💰 Free Usage Options

**Don't want to pay for APIs? Here are completely free solutions!**

### Recommended: Ollama Local Models ⭐

1. **Install Ollama**: Visit https://ollama.com/ to download
2. **Download Models**: 
   ```bash
   ollama pull llama4       # Recommended: Meta Llama 4 (2025 Latest)
   ollama pull qwen3        # Or: Alibaba Qwen3
   ollama pull deepseek-v3  # Or: DeepSeek V3
   ```
3. **Configure in Node**:
   - Provider: `Ollama (Local)`
   - Model: `llama4` (or other downloaded models: qwen3, deepseek-v3, phi4)
   - Base URL: `http://localhost:11434/v1`
   - API Key: Leave empty

**Advantages**:
- ✅ Completely free, no usage limits
- ✅ Privacy-focused, runs entirely locally
- ✅ No network latency (except search part)
- ✅ Supports latest models like llama4, qwen3, deepseek-v3, phi4

### Alternative: Ultra-Low-Cost APIs

If local resources are limited, consider these nearly-free options:

| Provider | Price | Notes |
|----------|-------|-------|
| **DeepSeek** | $0.14/million tokens | Official API, best value |
| **SiliconFlow** | Free tier available | China-friendly |
| **Groq** | Free tier available | Extremely fast |

---

## ⚙️ Configuration (Optional)

For local users who don't want to paste their API key every time, there are two configuration methods:

### Method 1: Use .env File (Recommended) ⭐

1. Copy `.env.example` to `.env`
2. Edit `.env` and fill in your API keys:

```bash
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_OFFICIAL_API_KEY=sk-your-deepseek-key-here
```

**Advantages**:
- ✅ Industry standard practice
- ✅ Automatically excluded by `.gitignore`, won't be accidentally committed
- ✅ More secure and professional

### Method 2: Use api_config.json

1. Rename `api_config_example.json` to `api_config.json`
2. Edit and fill in your API keys:

```json
{
    "openai_api_key": "sk-...",
    "deepseek (official)_api_key": "sk-..."
}
```

### API Key Priority

```
Node Input (Highest) > .env File > api_config.json (Lowest)
```

> **Note**: On cloud platforms, always use the `api_key` widget in the node for security.

## 📄 License

Apache 2.0 License
