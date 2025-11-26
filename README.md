<div align="center">

# 🌐 Live Search - Real-time Web Search for ComfyUI

**Connect Your ComfyUI to the Internet | Search, Scrape, Summarize**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-8%2B_Providers-orange)](https://github.com/Zone-Roam/ComfyUI-Live-Search)

**🔥 Use Cases**: Real-time Weather · News Summary · Fact Checking · Product Reviews · Web Scraping · GPS Coordinate Conversion

**🤖 Supported Models**: GPT-5.1 · DeepSeek-V3 · Gemini 3 Pro · Claude 4.5 · Qwen3 · Doubao · Llama 4 · Ollama

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
- 📍 GPS coordinate to location conversion (e.g., "40.00023, 116.27808" → "Beijing, Haidian District")
- 💬 Pure LLM chat (disable web search for direct AI conversations)
- 🌐 Any creative workflow requiring internet information

## 🏗️ New Modular Architecture

**Inspired by [comfyui_LLM_party](https://github.com/heshengtao/comfyui_LLM_party)'s excellent design**, we adopt a **modular layered architecture**:

### 📊 Node Composition

```
🔑 API Loader → ⚙️ Settings → 🌐 Search Agent → Results
```

| Node | Function | Output |
|------|----------|--------|
| **🔑 Live Search API Loader** | API config & model selection | MODEL_CONFIG |
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

- **🔍 DuckDuckGo Search Engine**  
  Stable, proxy-friendly, no API key required. Perfect for real-time info retrieval and complements any LLM/VLM.
  
- **🧠 Multi-Provider Model Hub (Text & Vision)**  
  - **OpenAI**: GPT-5.x, GPT-4.1 family, GPT-4o (now fully TI2T-capable)  
  - **SiliconFlow**: DeepSeek, Qwen3/Qwen2.5 VL, GLM-4.5V, Qwen3-Omni, etc. (single provider covering 70+ CN models)  
  - **DeepSeek Official / Aliyun / Volcengine**, **Gemini (OpenAI-format)**, **Anthropic Claude**, **Qwen (Aliyun)**, **Grok**, **Doubao**, **Ollama (local)**  
  > ✅ Every provider is validated end-to-end (auth, payload, response parsing).

- **🖼️ Dual Mode: T2T & TI2T**  
  - **T2T**: Traditional text-only LLM flow with web search + summarization  
  - **TI2T**: Vision-language pipeline (prompt + IMAGE) for reverse image search, landmark recognition, document reading, etc.  
  - TI2T supports **web search + image context fusion** (two-stage VLM call) and is available for **OpenAI GPT-5.1 / GPT-4o families** & **SiliconFlow VLMs**.

- **🌦️ Structured Tooling**  
  - **Open-Meteo** integration for precise real-time weather/time when GPS coordinates are provided  
  - **geopy + Nominatim** reverse geocoding (lat/lon → city/country)  
  - **Query Optimization** (rename: `optimize_query`) improves English search keywords while keeping answers in your selected language  
  - **Conflict resolution** prompts ensure VLM trusts web data for up-to-date info (time, weather).

- **🈚 Multi-Language Output**  
  Explicit output control: **中文** or **English** (no more “Auto” surprises). System prompts enforce consistency for both LLM and VLM flows.

- **🔐 Cloud-Friendly Security**  
  API keys never persist to disk, `.env` + `api_config.json` supported, and per-node proxy keeps shared GPU rentals safe.

## 🧠 T2T vs TI2T Modes

| Mode | Inputs | Model Slot | Flow | Perfect For |
|------|--------|------------|------|-------------|
| **T2T (Text → Text)** | Prompt | `t2t_model` | Search (DuckDuckGo) → scrape trusted sources → inject Open-Meteo & geopy context → LLM summarization. | Weather/time, news, fact checking, research, pure LLM chat (disable web search). |
| **TI2T (Text + IMAGE → Text)** | Prompt + ComfyUI IMAGE tensor | `ti2t_model` | Encode image → VLM query generation → DuckDuckGo search → VLM final reasoning with image + search snippets. | Landmark recognition, “reverse image” info, screenshot comprehension, visual + real-time hybrid tasks. |

**Implementation Notes**
- API Loader now provides **independent `t2t_model` / `ti2t_model` dropdowns** per provider. Agent auto-selects based on Settings `mode`.
- TI2T currently supports **OpenAI GPT-5.1 / GPT-4o / GPT-4-turbo** and **SiliconFlow VLM lineups** (Qwen3-VL, Qwen3-Omni, GLM-4.5V, DeepSeek-VL2, etc.).
- TI2T keeps **web search optional**: when enabled, VLM runs twice (query generation + final answer) so image context stays synced with live data.
- Both modes reuse the unified **`MODEL_CONFIG`** output, so legacy workflows remain compatible.

#### OpenAI GPT-5.x usage notes
- Access to GPT-5.1 family still requires an OpenAI plan with GPT-5 privileges (Pro/Team/Enterprise). If the API returns 404/403, double-check your account permissions.
- Live Search automatically switches GPT-5.* calls to the **Responses API**. You do not need to edit the base URL; simply pick `gpt-5.1`, `gpt-5.1-mini`, `gpt-5`, `gpt-5-mini`, or `gpt-5-pro` in API Loader.
- The node maps `max_tokens` → OpenAI's `max_output_tokens` under the hood, so you can keep using the same control in the UI.
- TI2T (image + text) is currently validated for `gpt-5.1`, `gpt-5.1-mini`, `gpt-5`, `gpt-5-mini`, and `gpt-5-pro`. Older GPT-4 models stay available for backward compatibility.

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
| **provider** | Choose provider: OpenAI, SiliconFlow, DeepSeek, Gemini, Anthropic, Qwen, Doubao, Ollama, etc. |
| **t2t_model** | Text-only model for T2T mode (LLM) |
| **ti2t_model** | Vision-language model for TI2T mode (VLM). Shows “No VLM models available” if the provider has none. |
| **api_key** | API key (optional, supports .env) |
| **base_url** | API endpoint (optional, falls back to provider defaults) |
| **temperature** | Temperature (0.0-2.0) |
| **max_tokens** | Maximum output length |
| **timeout** | Request timeout |

#### 2. **⚙️ Live Search Settings**

Configure search behavior.

| Parameter | Description |
|-----------|-------------|
| **mode** | `T2T` (text) or `TI2T` (text + image). TI2T expects an IMAGE input on the Agent node. |
| **enable_web_search** | Enable/disable web search (OFF = use as pure LLM) |
| **num_results** | Number of search results (1-10) |
| **output_language** | Output language: `中文` or `English` |
| **optimize_query** | LLM-powered search keyword optimization (English-focused for better search recall) |
| **proxy** | Proxy address (optional) |

#### 3. **🌐 Live Search Agent**

Main search node, connects to the above two nodes.

| Input | Type | Description |
|-------|------|-------------|
| **prompt** | STRING | Your question |
| **model_config** | MODEL_CONFIG | From API Loader |
| **search_settings** | SEARCH_SETTINGS | From Settings |
| *(optional)* **image** | IMAGE | Required when `mode = TI2T`. Pass any ComfyUI image tensor (RGB/RGBA). |
| *(optional)* **role** | STRING | Custom system prompt injected before the default instructions. |

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
| **output_language** | 🌐 Output Language<br>• **中文**: Force Chinese output<br>• **English**: Force English output |
| **optimize_query** | 🔄 Search Keyword Optimization (Recommended ON)<br>• **OFF** (default): Use original input directly<br>• **ON**: LLM rewrites the query (English keywords) for better DuckDuckGo recall<br>  - Preserves answer language via Agent settings<br>  - Removes redundancy, keeps core info<br>  - Outputs before/after comparison |
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

**5. GPS Coordinate Search**
- **Input**: `"What's the weather at coordinates 40.00023, 116.27808?"`
- **Optimize**: `ON` ✅
- **Auto-conversion**: Coordinates → "Beijing, Haidian District"
- **Optimized Query**: `"timeanddate Beijing Haidian"`
- **Output**: Real-time weather and time for Haidian District, Beijing

**6. Pure LLM Mode (No Search)**
- **Settings**: `enable_web_search = OFF`
- **Input**: `"Explain quantum computing"`
- **Output**: Direct LLM response without web search (faster, no internet required)

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
