<div align="center">

# 🌐 ComfyUI Live Search Agent

**ComfyUI 的实时联网搜索与 AI 总结节点**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/Support-DeepSeek-blueviolet)](https://www.deepseek.com/)

[中文文档](README_CN.md) | [English](README.md)

</div>

---

## 📖 项目简介

**ComfyUI Live Search Agent** 是一个强大的自定义节点，旨在打通 ComfyUI 与实时互联网之间的壁垒。

它结合了 **DuckDuckGo/Google 搜索** 的广度与 **DeepSeek/OpenAI 等大模型** 的深度，能够自动抓取网页、阅读内容并提取你所需要的信息。无论你是需要获取当下的天气数据、新闻摘要，还是为图像生成寻找精确的事实依据，这个节点都能轻松搞定。

本项目的灵感来源于 `comfyui_LLM_Polymath` 的搜索能力与 `ComfyUI-TutuBanana` 的优秀交互设计。

## ✨ 核心特性

- **🔍 双搜索引擎支持**：
  - **DuckDuckGo**：（默认推荐）保护隐私，无需 API Key，对云端服务器友好，无广告干扰。
  - **Google**：经典的搜索选择，适合特定需求。
  
- **🧠 DeepSeek 原生支持**：
  - 完美支持 **DeepSeek-V3** 和 **DeepSeek-R1**。
  - 内置 **官方 API**、**阿里云 (百炼)** 和 **火山引擎 (方舟)** 的接口支持。
  - 智能映射：使用阿里云时，自动将 `deepseek-chat` 映射为 `deepseek-v3`。

- **🌤️ 智能模式**：
  - **天气/时间模式**：只需输入经纬度（如 `30.6, 104.0`），节点自动搜索并总结当地的实时时间与天气。
  - **智能搜索 (Smart Search)**：使用 LLM 先优化你的模糊提问，再进行精准搜索。

- **☁️ 云端与隐私安全**：
  - **API Key 安全**：在节点界面输入的 Key **绝不** 保存到本地硬盘（完美适配 AutoDL、RunningHub 等共享云环境）。
  - **本地配置**：同时也支持 `api_config.json`，方便本地部署用户持久化配置。

## 🚀 安装说明

### 方法一：通过 ComfyUI Manager 安装（推荐）

1. 在 ComfyUI 中打开 **Manager** 面板
2. 点击 **Install Custom Nodes**
3. 搜索 `Live Search`
4. 点击 **Install** 并重启 ComfyUI

### 方法二：Git 克隆

进入你的 ComfyUI `custom_nodes` 目录并运行：

```bash
git clone https://github.com/Louis-Kahn/ComfyUI-Live-Search.git
cd ComfyUI-Live-Search

# 如果使用 Portable 版本的 ComfyUI（推荐）
..\..\..\python_embeded\python.exe -m pip install -r requirements.txt

# 如果使用系统 Python 或虚拟环境
pip install -r requirements.txt
```

然后重启 ComfyUI。

### 方法三：手动安装

1. 下载本项目的 ZIP 压缩包
2. 解压到 `ComfyUI/custom_nodes/ComfyUI-Live-Search`
3. 参考方法二安装依赖
4. 重启 ComfyUI

## 🛠️ 使用指南

### 节点：**🌐 Live Search Agent**

#### 参数说明

| 参数名 | 说明 |
| :--- | :--- |
| **prompt** | 你的问题或位置坐标。例如 *"比特币现在的价格是多少？"* 或 *"35.68, 139.76"* |
| **mode** | • `Normal Search`: 普通搜索模式。<br>• `Weather/Time Mode`: 专为天气/时间查询优化，自动添加相关搜索前缀。 |
| **optimize_prompt** | 提示词优化开关。开启后，LLM 会将你的问题改写为更适合搜索的关键词。<br>• 关闭（默认）：直接使用原始输入<br>• 开启：LLM 优化后搜索，并输出优化结果 |
| **search_engine** | • `DuckDuckGo`: 推荐，更稳定。<br>• `Google`: 备选方案。 |
| **provider** | 选择 LLM 提供商：支持 `OpenAI`, `DeepSeek (官方/阿里云/火山)`, `Gemini` 等。 |
| **model** | 模型名称（如 `gpt-4o-mini`, `deepseek-chat`, `deepseek-r1`）。 |
| **api_key** | （可选）你的 API Key。留空则尝试读取配置文件。 |
| **proxy** | （可选）代理地址，如 `http://127.0.0.1:7890`。留空则直连。 |

#### 输出说明

| 输出名 | 说明 |
| :--- | :--- |
| **answer** | AI 根据搜索结果生成的答案 |
| **source_urls** | 引用的网页链接列表 |
| **optimized_prompt** | 显示提示词优化情况（是否优化、优化前后对比） |

#### 典型工作流示例

**1. 实时天气画图**
- **输入**: `34.05, -118.24` (洛杉矶坐标)
- **模式**: `Weather/Time Mode`
- **输出**: "洛杉矶当前时间下午2点，阳光明媚，气温25度。" -> [连接到提示词节点] -> 生成一张洛杉矶街头的阳光照片。

**2. 事实核查**
- **输入**: "最新的奥斯卡最佳影片是谁？"
- **模式**: `Smart Search`
- **搜索引擎**: `DuckDuckGo`
- **输出**: 基于实时搜索结果的准确回答。

## ⚙️ 高级配置（可选）

如果你是在本地电脑使用，不想每次都复制粘贴 API Key，可以配置 `api_config.json`：

94|1. 将项目根目录下的 `api_config_example.json` 重命名为 `api_config.json`。
95|2. 编辑 `api_config.json`：

```json
{
    "openai_api_key": "sk-...",
    "deepseek (official)_api_key": "sk-..."
}
```

> **注意**：在云端平台使用时，请务必直接在节点输入框填写 Key，以保证安全。

## 🧩 致谢

- **搜索逻辑**：参考了 `googlesearch-python` 和 `duckduckgo_search` 库。
- **灵感来源**：
  - `comfyui_LLM_Polymath`：提供了 RAG 和搜索的思路。
  - `ComfyUI-TutuBanana`：提供了优秀的项目结构和用户体验设计理念。

## 📄 许可证

Apache 2.0 License

