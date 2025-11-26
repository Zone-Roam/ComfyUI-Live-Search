<div align="center">

# 🌐 Live Search - ComfyUI 实时联网搜索节点

**让你的 ComfyUI 接入互联网 | 搜索、抓取、总结一站式解决**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-8%2B_Providers-orange)](https://github.com/Zone-Roam/ComfyUI-Live-Search)

**🔥 热门场景**: 实时天气 · 新闻摘要 · 事实查询 · 产品评测 · 网页抓取 · GPS坐标转换

**🤖 支持模型**: GPT-5.1 · DeepSeek-V3 · Gemini 3 Pro · Claude 4.5 · Qwen3 · Doubao · Llama 4 · Ollama

[中文文档](README_CN.md) | [English](README.md)

</div>

---

## 📖 为什么选择 Live Search?

**ComfyUI Live Search** 让你的工作流直接访问互联网！这是一个功能强大的**联网搜索节点**，支持：

✅ **实时搜索**: DuckDuckGo 搜索引擎，稳定可靠  
✅ **智能总结**: AI 自动阅读网页并提取关键信息  
✅ **多模型支持**: GPT-5.1、DeepSeek-V3、Gemini 3 Pro、Claude 4.5、Qwen3 等 8+ LLM 提供商  
✅ **模块化架构**: API 配置、搜索设置、执行逻辑分离，灵活复用  
✅ **国内友好**: 完美支持国产大模型（通义千问/Qwen、豆包/Doubao、DeepSeek）

**典型应用场景**:
- 🌤️ 查询实时天气生成对应场景图
- 📰 获取最新新闻并生成相关内容
- 🔍 事实核查和信息验证
- 🛍️ 产品信息查询和评测总结
- 📍 GPS 坐标转地名（如 "40.00023, 116.27808" → "北京海淀区"）
- 💬 纯 LLM 对话（关闭联网搜索，直接 AI 对话）
- 🌐 任何需要联网信息的创意工作流

## 🏗️ 新版架构设计

**参考 [comfyui_LLM_party](https://github.com/heshengtao/comfyui_LLM_party) 的优秀设计**，我们采用了**模块化分层架构**：

### 📊 节点组合

```
🔑 API Loader → ⚙️ Settings → 🌐 Search Agent → 输出结果
```

| 节点 | 功能 | 输出 |
|------|------|------|
| **🔑 Live Search API Loader** | API 配置和模型选择 | MODEL_CONFIG |
| **⚙️ Live Search Settings** | 搜索参数配置 | SEARCH_SETTINGS |
| **🌐 Live Search Agent** | 主搜索逻辑 | answer, source_urls, optimized_prompt |

### ✅ 新架构优势

- **模块化设计**：配置与逻辑分离，更易维护
- **可复用性**：一个 API Loader 可连接多个 Agent
- **灵活性**：不同场景使用不同的 Settings 组合
- **专业性**：符合大型项目的最佳实践

### 🔄 向后兼容

- 旧版单节点 `🌐 Live Search (Legacy)` 仍然可用
- 建议新用户使用新的三节点组合

---

## ✨ 核心特性

- **🔍 DuckDuckGo 搜索引擎**  
  稳定、代理友好、免 API Key，最适合作为实时信息抓取的基础。
  
- **🧠 文本 + 视觉模型一网打尽**  
  - **OpenAI**: GPT-5.x、GPT-4.1 系列、GPT-4o（已全面接入 TI2T）  
  - **硅基流动**: DeepSeek、Qwen3/Qwen2.5 VL、GLM-4.5V、Qwen3-Omni……单一供应商覆盖 70+ VLM  
  - **DeepSeek 官方/阿里/火山**、**Gemini (OpenAI-Format)**、**Anthropic Claude**、**Qwen (阿里云)**、**Grok**、**Doubao**、**Ollama 本地**  
  > ✅ 所有供应商均已跑通：鉴权、payload、响应解析全验证。

- **🖼️ 双模式管线（T2T & TI2T）**  
  - **T2T**：纯文本 LLM + 搜索 + 抓取 + 总结  
  - **TI2T**：文本 + 图片输入，走 Vision-Language 流程，可做图片反推、地标识别、截图理解  
  - TI2T 支持 **双阶段搜索**（VLM 生成搜索词 → 搜索 → VLM 最终回答），当前开放 **OpenAI GPT-5.1/4o/4-turbo** 与 **硅基流动 VLM 家族**。

- **🌦️ 专业级工具链**  
  - **Open-Meteo** 精准注入实时天气/时间（有坐标即可）  
  - **geopy + Nominatim** 自动把经纬度反查城市名称  
  - **Query Optimization (`optimize_query`)**：LLM 将自然语言提示转为高命中英文关键词，但回答仍按设定语言输出  
  - **冲突处理策略**：当图片与实时信息冲突时，优先信任搜索数据，避免幻觉。

- **🈚 输出语言可控**  
  只保留 **中文 / English** 两种模式，系统 prompt 保证 LLM/VLM 双通道都严格遵守。

- **🔐 云环境友好**  
  API Key 不落盘，`.env` 与 `api_config.json` 双配置，节点级代理让共享 GPU 平台也能放心使用。

## 🧠 T2T 与 TI2T 模式对比

| 模式 | 输入 | 模型槽位 | 流程 | 典型场景 |
|------|------|-----------|------|----------|
| **T2T（Text → Text）** | 纯文本 Prompt | `t2t_model` | DuckDuckGo 搜索 → 抓取可信站点 → 注入 Open-Meteo & geopy 信息 → LLM 总结 | 实时天气、新闻、事实核查、只想纯 LLM 聊天（可关搜索）。 |
| **TI2T（Text+Image → Text）** | Prompt + ComfyUI IMAGE 张量 | `ti2t_model` | 图像编码 → VLM 生成搜索词 → 搜索 → VLM 最终回答（融合图像+搜索） | 图片反推、地标识别、截图理解、视觉 + 实时信息混合任务。 |

**实现要点**
- API Loader 提供 **独立的 `t2t_model` / `ti2t_model` 下拉菜单**，Agent 会根据 Settings.mode 自动选择。
- TI2T 目前支持 **OpenAI GPT-5.1/4o/4-turbo** 与 **硅基流动 VLM 系列**（Qwen3-VL、Qwen3-Omni、GLM-4.5V、DeepSeek-VL2 等）。
- TI2T 可选开启联网搜索：打开后 VLM 会执行两次调用，确保图片语境与实时数据同步。
- 两种模式共用统一的 **`MODEL_CONFIG`** 输出，旧版工作流无需重建。

#### OpenAI GPT-5.x 使用提示
- GPT-5.1 家族需要具备 GPT-5 权限的 OpenAI 账号（Pro / Team / Enterprise 等）。若 API 返回 403/404，请先确认账号额度。
- 选择 `gpt-5.*` 时会自动切换到 **Responses API**，无需更改 base_url，只需在 API Loader 中选择 `gpt-5.1`、`gpt-5.1-mini`、`gpt-5`、`gpt-5-mini` 或 `gpt-5-pro`。
- 节点会自动把 `max_tokens` 映射为 `max_output_tokens`，界面设置保持不变。
- TI2T（图文输入）已验证支持 `gpt-5.1`、`gpt-5.1-mini`、`gpt-5`、`gpt-5-mini`、`gpt-5-pro`，旧版 GPT-4 系列仍可兼容。

## 🚀 安装说明

### 方法一：通过 ComfyUI Manager 安装（推荐）

1. 在 ComfyUI 中打开 **Manager** 面板
2. 点击 **Install Custom Nodes**
3. 搜索 `Live Search`
4. 点击 **Install** 并重启 ComfyUI

### 方法二：Git 克隆

进入你的 ComfyUI `custom_nodes` 目录并运行：

```bash
git clone https://github.com/Zone-Roam/ComfyUI-Live-Search.git
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

### 📸 工作流示例

下图展示了两种使用方式：
- **左侧**: Legacy单节点模式 - 简单快速,所有配置集中在一个节点
- **右下方**: 新版模块化架构 - API Loader + Settings + Agent,更灵活可复用

![工作流示例](images/workflow_example.png)

---

### 方式一：新版模块化架构（推荐）⭐

#### 1. **🔑 Live Search API Loader**

配置 LLM API 和模型参数。

| 参数 | 说明 |
|------|------|
| **provider** | 选择提供商：OpenAI、硅基流动、DeepSeek、Gemini、Anthropic、Qwen、Doubao、Ollama 等 |
| **t2t_model** | 文本模型（T2T 模式使用） |
| **ti2t_model** | 视觉模型（TI2T 模式使用，无可用模型时会显示占位提示） |
| **api_key** | API密钥（可选，支持 .env） |
| **base_url** | API地址（可选，默认使用标准地址） |
| **temperature** | 温度参数 (0.0-2.0) |
| **max_tokens** | 最大输出长度 |
| **timeout** | 请求超时时间 |

#### 2. **⚙️ Live Search Settings**

配置搜索行为。

| 参数 | 说明 |
|------|------|
| **mode** | `T2T`（文本）或 `TI2T`（文本+图像）。TI2T 需连接 IMAGE 输入。 |
| **enable_web_search** | 启用/禁用联网搜索（关闭 = 作为纯 LLM 使用） |
| **num_results** | 搜索结果数量 (1-10) |
| **output_language** | 输出语言：`中文` 或 `English` |
| **optimize_query** | LLM 搜索词优化（更利于英文搜索结果召回） |
| **proxy** | 代理地址（可选） |

#### 3. **🌐 Live Search Agent**

主搜索节点，连接上述两个节点。

| 输入 | 类型 | 说明 |
|------|------|------|
| **prompt** | STRING | 你的问题 |
| **model_config** | MODEL_CONFIG | 来自 API Loader |
| **search_settings** | SEARCH_SETTINGS | 来自 Settings |
| （可选）**image** | IMAGE | 当 `mode = TI2T` 时必须连接，支持任何 ComfyUI 图像张量 |
| （可选）**role** | STRING | 自定义系统提示，注入在默认规则前 |

| 输出 | 说明 |
|------|------|
| **answer** | AI 生成的答案 |
| **source_urls** | 引用来源链接 |
| **optimized_prompt** | 优化后的搜索词 |

---

### 方式二：Legacy 单节点模式

#### 节点：**🌐 Live Search (Legacy)**

#### 参数说明

| 参数名 | 说明 |
| :--- | :--- |
| **prompt** | 你的问题。支持中英文。例如 *"北京现在的天气"* 或 *"Who won the Super Bowl?"* |
| **output_language** | 🌐 输出语言<br>• **中文**：强制中文回答<br>• **English**：强制英文回答 |
| **optimize_query** | 🔄 搜索词优化（推荐开启）<br>• **关闭**：直接使用原提示<br>• **开启**：LLM 将问题改写为更精准的英文搜索关键词（回答语言仍依据 Settings 设置）<br>  - 去冗余、保留核心信息<br>  - 输出优化前后对比 |
| **search_engine** | 🔍 **DuckDuckGo**（唯一选项）<br>• 稳定可靠，对自动化访问友好<br>• 无需额外配置即可工作<br>• 搜索质量完全满足需求 |
| **provider** | 选择 LLM 提供商：支持 `OpenAI`, `DeepSeek (官方/阿里云/火山)`, `Gemini` 等。 |
| **model** | 🎯 模型选择（下拉列表）<br>• **OpenAI**: gpt-5.1, gpt-5, gpt-4.1, o3, o3-pro 等<br>• **DeepSeek**: deepseek-v3, deepseek-chat, deepseek-reasoner<br>• **Gemini**: gemini-3-pro, gemini-2.5-pro, gemini-2.5-flash 等<br>• **Claude**: claude-sonnet-4-5, claude-haiku-4-5 等<br>• 支持搜索过滤，快速找到所需模型 |
| **api_key** | （可选）你的 API Key。留空则尝试读取配置文件。 |
| **proxy** | （可选）代理地址，如 `http://127.0.0.1:7890`。留空则直连。 |

#### 输出说明

| 输出名 | 说明 |
| :--- | :--- |
| **answer** | AI 根据搜索结果生成的答案 |
| **source_urls** | 引用的网页链接列表 |
| **optimized_prompt** | 显示提示词优化情况（是否优化、优化前后对比） |

#### 典型工作流示例

**1. 实时天气生图**
- **输入**: `"北京现在的天气"`
- **优化开关**: `开启` ✅
- **优化结果**: `"北京 实时天气 当前时间"`
- **输出**: "北京当前时间下午 3 点，晴天，气温 10°C。" 
- → [连接到提示词节点] → 生成北京晴天街景图

**2. 事实查询**
- **输入**: `"最新的奥斯卡最佳影片"`
- **优化开关**: `开启` ✅
- **输出**: 基于实时搜索结果的准确回答

**3. 跨语言查询**
- **输入**: `"What's the weather in Beijing?"` (英文问题)
- **输出语言**: `中文` 🇨🇳
- **优化开关**: `开启` ✅
- **输出**: 北京实时天气信息（**用中文回答**）

**4. 国际协作场景**
- **输入**: `"北京现在的天气"` (中文问题)
- **输出语言**: `English` 🇺🇸
- **输出**: Beijing weather info (**answered in English**)

**5. GPS 坐标搜索**
- **输入**: `"坐标 40.00023, 116.27808 的天气"`
- **优化**: `开启` ✅
- **自动转换**: 坐标 → "北京, 海淀区"
- **优化查询**: `"timeanddate Beijing Haidian"`
- **输出**: 北京海淀区的实时天气和时间信息

**6. 纯 LLM 模式（无搜索）**
- **设置**: `enable_web_search = 关闭`
- **输入**: `"解释一下量子计算"`
- **输出**: 直接 LLM 回答，不进行联网搜索（更快，无需网络）

## 🔍 为什么只支持 DuckDuckGo？

本节点使用**真实的网页爬虫**进行搜索，而非 API 调用。在实际测试中：

**✅ DuckDuckGo 的优势**：
- 对自动化访问友好，反爬虫机制相对宽松
- 即使配置代理也能稳定工作
- 搜索质量完全满足实时信息检索需求
- 开源友好，社区支持良好

**❌ Google 的问题**：
- 极其严格的反爬虫机制（验证码、IP 封锁、User-Agent 检测）
- 即使挂代理也经常返回空结果或验证码页面
- `googlesearch-python` 库在生产环境中不稳定
- 频繁访问会导致 IP 被暂时封禁

**💡 如果需要 Google 搜索质量**：
- 可以考虑使用官方的 **Google Custom Search API**（需付费）
- 或者使用 **SerpAPI** 等第三方服务（需付费）

我们选择 DuckDuckGo 是为了确保节点在各种环境下都能**稳定可靠**地工作。

---

## 💰 免费使用方案

**不想付费使用 API? 这里有完全免费的方案!**

### 推荐方案: Ollama 本地模型 ⭐

1. **安装 Ollama**: 访问 https://ollama.com/ 下载安装
2. **下载模型**: 
   ```bash
   ollama pull llama4       # 推荐: Meta Llama 4 (2025最新)
   ollama pull qwen3        # 或者: 阿里通义千问 Qwen3
   ollama pull deepseek-v3  # 或者: DeepSeek V3
   ```
3. **在节点中配置**:
   - Provider: `Ollama (Local)`
   - Model: `llama4` (或其他已下载的模型: qwen3, deepseek-v3, phi4)
   - Base URL: `http://localhost:11434/v1`
   - API Key: 留空

**优势**:
- ✅ 完全免费,无使用限制
- ✅ 数据隐私,完全本地运行
- ✅ 无网络延迟(除了搜索部分)
- ✅ 支持 llama4, qwen3, deepseek-v3, phi4 等最新模型

### 备选方案: 超低价 API

如果本地资源不足,可以选择这些几乎免费的方案:

| 提供商 | 价格 | 说明 |
|--------|------|------|
| **DeepSeek** | ¥1/百万tokens | 官方API,极致性价比 |
| **硅基流动** | 有免费额度 | 国内访问友好 |
| **Groq** | 有免费额度 | 速度极快 |

---

## ⚙️ 高级配置（可选）

如果你是在本地电脑使用，不想每次都复制粘贴 API Key，有两种配置方式：

### 方式一：使用 .env 文件（推荐）⭐

1. 将 `.env.example` 复制为 `.env`
2. 编辑 `.env` 文件并填入你的 API keys：

```bash
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_OFFICIAL_API_KEY=sk-your-deepseek-key-here
```

**优势**：
- ✅ 符合业界标准实践
- ✅ 自动被 `.gitignore` 排除，不会意外提交到 Git
- ✅ 更安全，更专业

### 方式二：使用 api_config.json

1. 将 `api_config_example.json` 重命名为 `api_config.json`
2. 编辑并填入你的 API keys：

```json
{
    "openai_api_key": "sk-...",
    "deepseek (official)_api_key": "sk-..."
}
```

### API Key 优先级

```
节点输入框 (最高) > .env 文件 > api_config.json (最低)
```

> **注意**：在云端平台使用时，请务必直接在节点输入框填写 Key，以保证安全。

## 📄 许可证

Apache 2.0 License

