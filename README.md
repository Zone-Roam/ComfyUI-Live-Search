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
| **prompt** | Your query or location. e.g., *"What is the price of Bitcoin?"* or *"35.68, 139.76"* |
| **mode** | • `Normal Search`: Standard search mode.<br>• `Weather/Time Mode`: Optimized for weather/time queries with auto-prefix. |
| **optimize_prompt** | Prompt optimization toggle. When enabled, LLM rewrites your query into better search keywords.<br>• OFF (default): Use original input<br>• ON: LLM optimizes, outputs comparison |
| **search_engine** | • `DuckDuckGo`: Recommended for stability.<br>• `Google`: Alternative option. |
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

**1. The Weather Reporter**
- **Input**: `34.05, -118.24` (Los Angeles)
- **Mode**: `Weather/Time Mode`
- **Output**: "It is currently 2:00 PM in Los Angeles, Sunny, 25°C." -> [Text to Image Node] -> Generates a sunny LA street.

**2. The Fact Checker**
- **Input**: "Who won the latest Super Bowl?"
- **Mode**: `Smart Search`
- **Search Engine**: `DuckDuckGo`
- **Output**: Provides the latest winner based on real-time search results.

## ⚙️ Configuration (Optional)

For local users who don't want to paste their API key every time:

94|1. Rename `api_config_example.json` to `api_config.json` in the root directory.
95|2. Edit `api_config.json` and fill in your API keys:

```json
{
    "openai_api_key": "sk-...",
    "deepseek (official)_api_key": "sk-..."
}
```

> **Note**: On cloud platforms, always use the `api_key` widget in the node for security.

## 🧩 Credits

- **Search Logic**: Adapted from `googlesearch-python` and `duckduckgo_search`.
- **Inspiration**: 
  - `comfyui_LLM_Polymath` for RAG concepts.
  - `ComfyUI-TutuBanana` for project structure and UI/UX philosophy.

## 📄 License

Apache 2.0 License
