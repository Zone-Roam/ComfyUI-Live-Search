<div align="center">

# 🌐 ComfyUI Live Search Agent

**Real-time Web Search & AI Summarization for ComfyUI**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/Support-DeepSeek-blueviolet)](https://www.deepseek.com/)

[中文文档](README_CN.md) | [English](README.md)

</div>

---

## 📖 Introduction

**ComfyUI Live Search Agent** is a powerful custom node that bridges the gap between ComfyUI and the real-time internet. 

It combines the robustness of **DuckDuckGo/Google Search** with the intelligence of **LLMs (DeepSeek, OpenAI, etc.)** to fetch, read, and summarize information for your workflows. Whether you need current weather data, news summaries, or specific facts to prompt your image generation, this node handles it all.

This project is inspired by the search capabilities of `comfyui_LLM_Polymath` and the user-friendly design of `ComfyUI-TutuBanana`.

## ✨ Key Features

- **🔍 Dual Search Engines**: 
  - **DuckDuckGo**: (Default) Private, no API key needed, cloud-friendly, no ad interference.
  - **Google**: Classic search for specific needs.
  
- **🧠 DeepSeek Native Support**: 
  - First-class support for **DeepSeek-V3/R1**.
  - Built-in integration for **Official API**, **Aliyun (Bailian)**, and **Volcengine (Ark)**.
  - Auto-mapping for Aliyun models (`deepseek-chat` -> `deepseek-v3`).

- **🌤️ Smart Modes**:
  - **Weather/Time Mode**: Just input coordinates (e.g., `30.6, 104.0`), and it auto-fetches local time & weather.
  - **Smart Search**: Uses LLM to refine your vague prompts into precise search queries.

- **☁️ Cloud & Privacy First**:
  - **API Key Security**: Keys entered in the UI are **NEVER** saved to disk (perfect for shared cloud environments like AutoDL/RunningHub).
  - **Local Config**: Supports `api_config.json` for local power users.

## 🚀 Installation

### Method 1: via ComfyUI Manager (Recommended)

1. Open **Manager** panel in ComfyUI
2. Click **Install Custom Nodes**
3. Search for `Live Search`
4. Click **Install** and restart ComfyUI

### Method 2: Git Clone

Navigate to your ComfyUI `custom_nodes` directory and run:

```bash
git clone https://github.com/Louis-Kahn/ComfyUI-Live-Search.git
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

### Node: **🌐 Live Search Agent**

#### Input Parameters

| Parameter | Description |
| :--- | :--- |
| **prompt** | Your question. Supports both Chinese and English. e.g., *"北京现在的天气"* or *"Who won the Super Bowl?"* |
| **output_language** | 🌐 Output Language<br>• **Auto (跟随输入)** (default): Automatically matches question language<br>• **中文**: Force Chinese output<br>• **English**: Force English output |
| **optimize_prompt** | 🔄 Prompt Optimization Toggle (Recommended ON)<br>• **OFF** (default): Use original input directly<br>• **ON**: LLM optimizes your question into precise search keywords<br>  - Preserves original language (CN→CN, EN→EN)<br>  - Removes redundant words, keeps core info<br>  - Outputs before/after comparison |
| **search_engine** | 🔍 **DuckDuckGo** (Only Option)<br>• Stable and automation-friendly<br>• Works reliably with proxies<br>• High-quality search results |
| **provider** | Choose your LLM provider: `OpenAI`, `DeepSeek (Official/Aliyun/Volcengine)`, `Gemini`, etc. |
| **model** | The model name (e.g., `gpt-4o-mini`, `deepseek-chat`, `deepseek-r1`). |
| **api_key** | (Optional) Your API Key. If left empty, it tries to load from `api_config.json`. |
| **proxy** | (Optional) Proxy address like `http://127.0.0.1:7890`. Leave empty for direct connection. |

#### Outputs

| Output | Description |
| :--- | :--- |
| **answer** | AI-generated answer based on search results |
| **source_urls** | List of referenced web page links |
| **optimized_prompt** | Shows prompt optimization status (whether optimized, before/after comparison) |

#### Example Workflows

**1. Real-time Weather Image Generation**
- **Input**: `"What's the weather in Tokyo?"`
- **Optimize**: `ON` ✅
- **Optimized**: `"Tokyo weather now"`
- **Output**: "Currently 2:00 PM in Tokyo, Sunny, 15°C."
- → [Connect to Text2Image] → Generate Tokyo sunny street scene

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
- **Input**: `"What's the weather in Tokyo?"` (English question)
- **Output Language**: `中文` 🇨🇳
- **Output**: Tokyo weather info (**answered in Chinese**)

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

## 🧩 Credits

- **Search Logic**: Adapted from `googlesearch-python` and `duckduckgo_search`.
- **Inspiration**: 
  - `comfyui_LLM_Polymath` for RAG concepts.
  - `ComfyUI-TutuBanana` for project structure and UI/UX philosophy.

## 📄 License

Apache 2.0 License
