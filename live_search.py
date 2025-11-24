import os
import json
import requests
from bs4 import BeautifulSoup
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from .config_manager import ConfigManager

# Initialize Config Manager
config_manager = ConfigManager()

# Model configurations for different providers
MODEL_CONFIGS = {
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
    "DeepSeek (Volcengine)": [
        "deepseek-chat",
        "deepseek-v3"
    ],
    "Gemini (OpenAI-Format)": [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ],
    "Custom": [
        "custom-model"
    ]
}

class SearchTool:
    @staticmethod
    def search_duckduckgo(query, num_results=3, proxy=None):
        """
        Performs a DuckDuckGo search.
        """
        try:
            # DDGS supports proxy argument directly
            with DDGS(proxy=proxy, timeout=20) as ddgs:
                # ddgs.text() returns a generator of dicts: {'title', 'href', 'body'}
                # Try default backend first, fallback to 'html' or 'lite' if needed manually if we were managing requests directly,
                # but ddgs library handles backends. We explicitly request 'api' or default.
                # If result is empty, it might be a strict region/bot issue.
                results = list(ddgs.text(query, max_results=num_results))
                
                # Fallback mechanism: sometimes first request fails or returns empty in strict envs
                if not results:
                    print("[LiveSearch] DDG default backend returned empty, trying 'html' backend simulation...")
                    # Some versions of ddgs support backend='html', others don't via .text()
                    # We'll just rely on the default for now, but print warning.
            
            # Normalize keys to match Google
            normalized_results = []
            for res in results:
                normalized_results.append({
                    'title': res.get('title', ''),
                    'url': res.get('href', ''),
                    'summary': res.get('body', '')
                })
            return normalized_results
        except Exception as e:
            print(f"[LiveSearch] DuckDuckGo Search error: {e}")
            return []

    @staticmethod
    def fetch_url_content(url, timeout=10, proxy=None):
        """
        Fetches and extracts text content from a URL.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid context overflow (simple truncation)
            return text[:5000] 
            
        except Exception as e:
            print(f"[LiveSearch] Fetch error for {url}: {e}")
            return ""

class LLMClient:
    @staticmethod
    def chat_completion(api_key, base_url, model, messages, temperature=0.7, proxy=None):
        """
        Generic OpenAI-compatible chat completion
        """
        if not api_key:
            return "Error: API Key is missing."
            
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        try:
            # Increased timeout to 120s as DeepSeek R1/V3 can be slow sometimes
            response = requests.post(url, headers=headers, json=payload, timeout=120, proxies=proxies)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

class LiveSearchNode:
    """
    A ComfyUI node that performs a web search and summarizes the results using an LLM.
    Ideal for retrieving real-time information like weather, news, etc.
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        # Get all unique models across all providers for the dropdown
        all_models = []
        for provider_models in MODEL_CONFIGS.values():
            all_models.extend(provider_models)
        # Remove duplicates while preserving order
        unique_models = []
        seen = set()
        for model in all_models:
            if model not in seen:
                unique_models.append(model)
                seen.add(model)
        
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "e.g., 北京现在的天气 / What is the weather in Tokyo?"}),
                "output_language": (["Auto (跟随输入)", "中文", "English"], {"default": "Auto (跟随输入)"}),
                "optimize_prompt": ("BOOLEAN", {"default": False, "label_on": "Optimize ON", "label_off": "Optimize OFF"}),
                "provider": ([
                    "OpenAI", 
                    "DeepSeek (Official)", 
                    "DeepSeek (Aliyun)", 
                    "DeepSeek (Volcengine)",
                    "Gemini (OpenAI-Format)", 
                    "Custom"
                ], {"default": "DeepSeek (Official)"}),
                "model": (unique_models, {"default": "deepseek-chat"}),
                "num_results": ("INT", {"default": 3, "min": 1, "max": 10}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "placeholder": "Leave empty to use config file"}),
                "custom_base_url": ("STRING", {"default": "", "placeholder": "Required for Custom/Gemini/DeepSeek"}),
                "proxy": ("STRING", {"default": "", "placeholder": "http://127.0.0.1:7890 (Optional)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("answer", "source_urls", "optimized_prompt")
    FUNCTION = "process_search"
    CATEGORY = "LiveSearch"

    def process_search(self, prompt, output_language, optimize_prompt, provider, model, num_results, api_key, custom_base_url, proxy):
        # 1. Resolve Proxy
        valid_proxy = proxy.strip() if proxy and proxy.strip() else None
        
        # 2. Resolve API Key and Base URL
        resolved_api_key = api_key.strip()
        if not resolved_api_key:
             # Fallback to config file if UI input is empty
             resolved_api_key = config_manager.get_api_key(provider, "")
        
        # Default to OpenAI
        base_url = "https://api.openai.com/v1"
        final_model = model

        # --- Provider Logic ---
        if provider == "DeepSeek (Official)":
            base_url = "https://api.deepseek.com"
            # Official usually uses 'deepseek-chat' or 'deepseek-reasoner'
        
        elif provider == "DeepSeek (Aliyun)":
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            # Aliyun might need specific model mapping if user didn't input exact one, 
            # but usually we trust the user's input or provide a smart default.
            # If user left default 'deepseek-chat', Aliyun calls it 'deepseek-v3' usually.
            if final_model == "deepseek-chat":
                final_model = "deepseek-v3"

        elif provider == "DeepSeek (Volcengine)":
            base_url = "https://ark.cn-beijing.volces.com/api/v3"
            # Volcengine uses Endpoint IDs (e.g. ep-2025...) as model names usually, 
            # or mapped names if configured. The user needs to input the correct endpoint ID or model name.
            
        elif provider == "Gemini (OpenAI-Format)":
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        
        if custom_base_url.strip():
            base_url = custom_base_url.strip()
        
        # 2. Determine Search Query
        search_query = prompt
        optimized_prompt_output = "No optimization (using original prompt)"
        
        # Apply prompt optimization if enabled
        if optimize_prompt:
            refine_messages = [
                {"role": "system", "content": """You are a search engine expert. Convert the user's input into the best search query.
Rules:
1. Keep the same language as the input (Chinese→Chinese, English→English)
2. Remove unnecessary words, keep key information
3. For weather/time queries, preserve location and time context
4. Return ONLY the optimized query, no quotes or explanations

Examples:
- "北京现在的天气和时间" → "北京 实时天气 当前时间"
- "What's the weather in Tokyo?" → "Tokyo weather now"
- "外面冷吗" → "当地天气 温度"
- "Who won the Super Bowl?" → "Super Bowl winner latest"
"""},
                {"role": "user", "content": prompt}
            ]
            refined_query = LLMClient.chat_completion(resolved_api_key, base_url, final_model, refine_messages, proxy=valid_proxy)
            if not refined_query.startswith("Error"):
                print(f"[LiveSearch] Prompt optimized: {prompt} -> {refined_query}")
                optimized_prompt_output = f"Original: {prompt}\nOptimized: {refined_query}"
                search_query = refined_query
            else:
                optimized_prompt_output = f"Optimization failed: {refined_query}"

        # 3. Perform Search
        print(f"[LiveSearch] Searching for: {search_query} using DuckDuckGo")
        
        search_results = SearchTool.search_duckduckgo(search_query, num_results, proxy=valid_proxy)
        
        if not search_results:
            return (f"No search results found using DuckDuckGo.", "", optimized_prompt_output)

        # 4. Extract Content
        context_data = []
        source_urls = []
        
        for res in search_results:
            url = res['url']
            title = res['title']
            summary = res['summary']
            
            print(f"[LiveSearch] Fetching: {url}")
            content = SearchTool.fetch_url_content(url, proxy=valid_proxy)
            
            if content:
                snippet = content[:2000] if content else summary
                context_data.append(f"Source: {title} ({url})\nSummary: {summary}\nContent: {snippet}\n---")
                source_urls.append(url)
        
        full_context = "\n".join(context_data)

        # 5. Generate Answer
        # Determine output language instruction
        language_instruction = ""
        if output_language == "中文":
            language_instruction = "You MUST answer in Chinese (简体中文)."
        elif output_language == "English":
            language_instruction = "You MUST answer in English."
        else:  # Auto (跟随输入)
            language_instruction = "Answer in the SAME LANGUAGE as the user's question."
        
        system_prompt = f"""You are a helpful assistant with access to real-time web search results. 
Rules:
1. {language_instruction}
2. Base your answer ONLY on the provided search results
3. If results contain time/weather info, be precise with numbers and units
4. Keep the answer concise and well-structured"""

        final_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {prompt}\n\nSearch Results:\n{full_context}"}
        ]

        answer = LLMClient.chat_completion(resolved_api_key, base_url, final_model, final_messages, proxy=valid_proxy)
        
        return (answer, "\n".join(source_urls), optimized_prompt_output)
