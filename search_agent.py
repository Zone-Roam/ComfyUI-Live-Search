"""
LiveSearch Agent Node
Main search and summarization logic
Works with API Loader and Settings nodes for modular design
"""

import base64
import io
import time
import requests
import re
import json
from bs4 import BeautifulSoup
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    print("[LiveSearch] Warning: geopy not available, coordinate reverse geocoding disabled")

try:
    from PIL import Image
except ImportError:
    Image = None
    print("[LiveSearch] Warning: Pillow not available, TI2T mode disabled")

class SearchTool:
    # Professional weather/time websites that we trust
    TRUSTED_DOMAINS = [
        'timeanddate.com',
        'accuweather.com',
        'weather.com',
        'wunderground.com',
        'openweathermap.org',
        'worldweatheronline.com',
        'weather-atlas.com',
        'weathertoday.live',
        'easeweather.com'
    ]
    
    @staticmethod
    def is_trusted_url(url):
        """Check if URL is from a trusted weather/time domain"""
        return any(domain in url.lower() for domain in SearchTool.TRUSTED_DOMAINS)
    
    @staticmethod
    def search_duckduckgo(query, num_results=3, proxy=None):
        """
        Performs a DuckDuckGo search with retry mechanism.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # DDGS supports proxy argument directly
                # Increase timeout for slower connections
                with DDGS(proxy=proxy, timeout=30) as ddgs:
                    # ddgs.text() returns a generator of dicts: {'title', 'href', 'body'}
                    results = list(ddgs.text(query, max_results=num_results))
                    
                    if results:
                        # Normalize keys and prioritize trusted domains
                        normalized_results = []
                        trusted_results = []
                        other_results = []
                        
                        for res in results:
                            url = res.get('href', '')
                            result_item = {
                                'title': res.get('title', ''),
                                'url': url,
                                'summary': res.get('body', '')
                            }
                            
                            # Prioritize trusted weather/time websites
                            if SearchTool.is_trusted_url(url):
                                trusted_results.append(result_item)
                            else:
                                other_results.append(result_item)
                        
                        # Return trusted results first, then others
                        normalized_results = trusted_results + other_results
                        return normalized_results[:num_results]
                    
                    # If results are empty but no error, maybe try again or just break
                    if attempt < max_retries - 1:
                        print(f"[LiveSearch] DDG returned empty results, retrying ({attempt + 1}/{max_retries})...")
                        time.sleep(1)
                        continue
                        
            except Exception as e:
                print(f"[LiveSearch] Search attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait a bit before retry
                    continue
                return []
        
        return []

    @staticmethod
    def get_weather_data(lat, lon, proxy=None):
        """
        Fetch precise weather and time data from Open-Meteo API (Free, No Key)
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m",
                "timezone": "auto",
                "timeformat": "iso8601"
            }
            
            # Open-Meteo usually works without proxy, but use if provided
            proxies = {"http": proxy, "https": proxy} if proxy else None
            
            # Reduce timeout to avoid hanging
            response = requests.get(url, params=params, timeout=10, proxies=proxies)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            timezone = data.get("timezone", "Unknown")
            timezone_abbr = data.get("timezone_abbreviation", "")
            
            # WMO Weather Codes interpretation
            wmo_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            weather_desc = wmo_codes.get(current.get("weather_code"), "Unknown weather code")
            
            # Format output string
            output = [
                f"--- REAL-TIME WEATHER & TIME DATA (Source: Open-Meteo) ---",
                f"Location Coordinates: {lat}, {lon}",
                f"Timezone: {timezone} ({timezone_abbr})",
                f"Current Local Time: {current.get('time', '').replace('T', ' ')}",
                f"Temperature: {current.get('temperature_2m')} °C (Apparent: {current.get('apparent_temperature')} °C)",
                f"Condition: {weather_desc}",
                f"Humidity: {current.get('relative_humidity_2m')}%",
                f"Wind Speed: {current.get('wind_speed_10m')} km/h",
                f"Cloud Cover: {current.get('cloud_cover')}%",
                f"Is Day: {'Yes' if current.get('is_day') else 'No'}",
                "--------------------------------------------------------"
            ]
            
            return "\n".join(output)
            
        except Exception as e:
            print(f"[LiveSearch] Open-Meteo fetch failed: {e}")
            return ""

    @staticmethod
    def fetch_url_content(url, timeout=10, proxy=None):
        """
        Fetches and extracts text content from a URL.
        For timeanddate.com, extract key information more precisely.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Special handling for timeanddate.com - extract key information
            if 'timeanddate.com' in url:
                # Try to extract time and weather info more precisely
                time_info = []
                weather_info = []
                
                # Look for time display (usually in specific divs/classes)
                time_elements = soup.find_all(['div', 'span'], class_=lambda x: x and ('time' in x.lower() or 'clock' in x.lower() or 'cst' in x.lower() or 'utc' in x.lower()))
                for elem in time_elements[:5]:  # Limit to first 5 matches
                    text = elem.get_text(strip=True)
                    if text and len(text) < 100:  # Time strings are usually short
                        time_info.append(text)
                
                # Look for weather info
                weather_elements = soup.find_all(['div', 'span'], class_=lambda x: x and ('weather' in x.lower() or 'temp' in x.lower() or '°f' in x.lower() or '°c' in x.lower()))
                for elem in weather_elements[:5]:
                    text = elem.get_text(strip=True)
                    if text and ('°' in text or 'weather' in text.lower() or 'forecast' in text.lower()):
                        weather_info.append(text)
                
                # Also get main content
                main_content = soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
                if main_content:
                    main_text = main_content.get_text(separator='\n', strip=True)
                else:
                    main_text = soup.get_text(separator='\n', strip=True)
                
                # Combine: prioritize time and weather info
                combined = []
                if time_info:
                    combined.append(f"Time Information: {' | '.join(time_info[:3])}")
                if weather_info:
                    combined.append(f"Weather Information: {' | '.join(weather_info[:3])}")
                combined.append(f"Main Content: {main_text[:3000]}")
                
                return '\n'.join(combined)
            
            # For other sites, use standard extraction
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
    RESPONSES_MODEL_PREFIXES = ("gpt-5",)
    
    @staticmethod
    def _should_use_responses_api(provider, model):
        if "OpenAI" not in provider:
            return False
        return model.startswith(LLMClient.RESPONSES_MODEL_PREFIXES)
    
    @staticmethod
    def _messages_to_responses_input(messages):
        """
        Convert Chat Completions style messages to Responses API format
        """
        responses_input = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            parts = []
            if isinstance(content, str):
                if content:
                    parts.append({"type": "input_text", "text": content})
            elif isinstance(content, list):
                for item in content:
                    item_type = item.get("type")
                    if item_type in ("text", "input_text"):
                        parts.append({"type": "input_text", "text": item.get("text", "")})
                    elif item_type == "image_url":
                        image_meta = item.get("image_url", {})
                        input_image = {"type": "input_image"}
                        if "url" in image_meta:
                            input_image["image_url"] = image_meta["url"]
                        if "detail" in image_meta:
                            input_image["detail"] = image_meta["detail"]
                        parts.append(input_image)
                    elif item_type == "input_image":
                        parts.append(item)
                    else:
                        if isinstance(item, dict):
                            parts.append({"type": "input_text", "text": item.get("text", json.dumps(item, ensure_ascii=False))})
                        else:
                            parts.append({"type": "input_text", "text": str(item)})
            else:
                parts.append({"type": "input_text", "text": str(content)})
            
            if not parts:
                parts.append({"type": "input_text", "text": ""})
            
            responses_input.append({
                "role": role,
                "content": parts
            })
        return responses_input
    
    @staticmethod
    def chat_completion(model_config, messages):
        """
        Generic OpenAI-compatible chat completion using config from API Loader
        Supports both T2T (LLM) and TI2T (VLM) models
        """
        api_key = model_config.get("api_key", "")
        base_url = model_config.get("base_url", "")
        model = model_config.get("model", "")
        temperature = model_config.get("temperature", 0.7)
        max_tokens = model_config.get("max_tokens", 2048)
        timeout = model_config.get("timeout", 120)
        proxy = model_config.get("proxy", None)
        provider = model_config.get("provider", "")
        
        # Ollama (Local) typically doesn't require API key
        if not api_key and "Ollama" not in provider:
            return "Error: API Key is missing."
        
        use_responses_api = LLMClient._should_use_responses_api(provider, model)
        
        # Anthropic (Claude) uses /messages endpoint instead of /chat/completions
        if "Anthropic" in provider:
            url = f"{base_url.rstrip('/')}/messages"
        elif use_responses_api:
            url = f"{base_url.rstrip('/')}/responses"
        else:
            url = f"{base_url.rstrip('/')}/chat/completions"
        
        # Provider-specific authentication and headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Anthropic (Claude) uses x-api-key header instead of Bearer token
        if "Anthropic" in provider:
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"  # Latest stable version
        # Aliyun providers (DashScope) - compatible mode supports Bearer token
        elif "Aliyun" in provider or provider in ["DeepSeek (Aliyun)", "Qwen (Aliyun)"]:
            # DashScope compatible mode uses Bearer token (OpenAI format)
            headers["Authorization"] = f"Bearer {api_key}"
        # Gemini (OpenAI-Format) - uses standard Authorization header
        elif "Gemini" in provider:
            # Gemini's OpenAI-compatible endpoint uses standard Bearer token
            headers["Authorization"] = f"Bearer {api_key}"
        # Ollama (Local) - usually no auth needed, but some setups use it
        elif "Ollama" in provider:
            # Ollama typically doesn't need auth, but if API key is provided, use it
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        # All other providers (OpenAI, DeepSeek, Grok, Volcengine) use standard Bearer token
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Anthropic (Claude) uses different payload structure
        if "Anthropic" in provider:
            # Anthropic API format: { "model": "...", "max_tokens": ..., "messages": [...] }
            # Note: Anthropic requires max_tokens (not optional)
            # Temperature is optional but supported by most models
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            # Add temperature if supported (most Claude models support it)
            if "haiku" not in model.lower():  # Some Haiku models may not support temperature
                payload["temperature"] = temperature
        elif use_responses_api:
            payload = {
                "model": model,
                "input": LLMClient._messages_to_responses_input(messages),
                "temperature": temperature
            }
            if max_tokens:
                payload["max_output_tokens"] = max_tokens
        else:
            # Standard OpenAI-compatible format
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False # Explicitly disable stream as requested
            }
            # Remove max_tokens for o1 models as they don't support it
            if model.startswith("o1-") or model == "o1" or model == "o1-pro":
                payload.pop("max_tokens", None)
                payload.pop("temperature", None) # o1 often has fixed temp
            
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout, proxies=proxies)
            
            # Better error handling for non-200 responses
            if response.status_code != 200:
                try:
                    error_json = response.json()
                    return f"Error calling LLM: HTTP {response.status_code} - {error_json}"
                except:
                    return f"Error calling LLM: HTTP {response.status_code} - {response.text}"
                    
            response.raise_for_status()
            data = response.json()
            
            # Anthropic (Claude) uses different response format
            if "Anthropic" in provider:
                if 'content' in data and len(data['content']) > 0:
                    # Claude returns content as array of text blocks
                    content_blocks = data['content']
                    text_content = ""
                    for block in content_blocks:
                        if block.get('type') == 'text':
                            text_content += block.get('text', '')
                    return text_content if text_content else str(data)
                else:
                    return f"Error: Unexpected response format from Anthropic. Response: {data}"
            elif use_responses_api:
                # Responses API returns output_text plus structured output array
                output_text = data.get("output_text")
                if isinstance(output_text, list) and output_text:
                    return "\n".join(output_text).strip()
                output_items = data.get("output", [])
                collected_text = []
                for item in output_items:
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") in ("output_text", "text", "input_text"):
                                collected_text.append(content.get("text", ""))
                    elif item.get("type") in ("output_text", "text"):
                        collected_text.append(item.get("text", ""))
                if collected_text:
                    return "\n".join(collected_text).strip()
                return str(data)
            # Standard OpenAI-compatible format (OpenAI, DeepSeek, Grok, Volcengine, Gemini, Aliyun, Ollama)
            elif 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected response format from LLM provider. Response: {data}"
                
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

class LiveSearch_Agent:
    """
    Main Search Agent Node
    Accepts MODEL_CONFIG and SEARCH_SETTINGS from separate nodes
    """
    
    # 模式分组：TI2T 需要图片输入；Dual 表示模型原生支持多模态但可向下兼容文本
    TI2T_MODELS = {
        "智谱AI": {
            "glm-4.6V-Flash",
            "glm-4V-Flash",
            "glm-4.1V-Thinking-Flash"
        },
        "OpenAI": {
            # OpenAI 视觉模型（使用 OpenAI 兼容格式，与 SiliconFlow 相同）
            "gpt-5.1",
            "gpt-5.1-mini",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-pro",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        },
        "Qwen (Aliyun)": {
            "qwen3-vl-flash",
            "qwen3-vl-flash-2025-10-15",
            "qwen3-vl-plus",
            "qwen3-vl-plus-2025-09-23"
        },
        "SiliconFlow (硅基流动)": {
            # DeepSeek VLM 系列
            "deepseek-ai/DeepSeek-OCR",
            "deepseek-ai/deepseek-vl2",
            # Qwen3 VL 系列
            "Qwen/Qwen3-VL-32B-Instruct",
            "Qwen/Qwen3-VL-32B-Thinking",
            "Qwen/Qwen3-VL-8B-Instruct",
            "Qwen/Qwen3-VL-8B-Thinking",
            "Qwen/Qwen3-VL-30B-A3B-Instruct",
            "Qwen/Qwen3-VL-30B-A3B-Thinking",
            "Qwen/Qwen3-VL-235B-A22B-Instruct",
            "Qwen/Qwen3-VL-235B-A22B-Thinking",
            # Qwen3 Omni 系列
            "Qwen/Qwen3-Omni-30B-A3B-Instruct",
            "Qwen/Qwen3-Omni-30B-A3B-Thinking",
            "Qwen/Qwen3-Omni-30B-A3B-Captioner",
            # Qwen2.5 VL 系列
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Qwen/Qwen2.5-VL-72B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
            # Qwen2 VL 系列
            "Qwen/Qwen2-VL-72B-Instruct",
            # QVQ 系列
            "Qwen/QVQ-72B-Preview",
            # GLM V 系列
            "zai-org/GLM-4.5V",
            "Pro/THUDM/GLM-4.1V-9B-Thinking",
            "THUDM/GLM-4.1V-9B-Thinking"
        },
        "Ollama (Local)": {
            "huihui_ai/qwen3-vl-abliterated:8b-instruct",
            "huihui_ai/qwen3-vl-abliterated:4b-instruct",
            "llama3.2-vision",
            "llava"
        },
        "Gemini (OpenAI-Format)": {
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash-live"
        },
        "Custom": {
            "custom-vlm-model"
        }
    }
    
    DUAL_MODE_MODELS = {
        "OpenAI": {
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano"
        },
        "Anthropic (Claude)": {
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-5",
            "claude-haiku-4-5-20251001",
            "claude-haiku-4-5",
            "claude-opus-4-1-20250805",
            "claude-opus-4-1"
        },
        "SiliconFlow (硅基流动)": {
            "Qwen/Qwen2.5-VL-72B-Instruct",
            "Qwen/Qwen3-Omni-30B-A3B-Instruct"
        }
    }
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "e.g., 北京现在的天气 / What is the weather in Beijing?"}),
                "model_config": ("MODEL_CONFIG",),
                "search_settings": ("SEARCH_SETTINGS",),
            },
            "optional": {
                "image": ("IMAGE",),
                "role": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": "", "placeholder": "Optional: Custom System Prompt (Role)"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("answer", "source_urls", "optimized_prompt")
    FUNCTION = "process_search"
    CATEGORY = "LiveSearch"
    
    def process_search(self, prompt, model_config, search_settings, image=None, role=""):
        # Extract settings
        mode = search_settings.get("mode", "T2T")
        enable_web_search = search_settings.get("enable_web_search", True)
        num_results = search_settings.get("num_results", 3)
        output_language = search_settings.get("output_language", "中文")
        # Support both old and new setting keys
        optimize_query = search_settings.get("optimize_query", search_settings.get("optimize_prompt", False))
        valid_proxy = search_settings.get("proxy")
        
        # Add proxy to model_config for API calls
        model_config_with_proxy = model_config.copy()
        model_config_with_proxy["proxy"] = valid_proxy
        provider = model_config_with_proxy.get("provider", "")
        
        # 根据 mode 选择使用哪个模型
        if mode == "TI2T":
            model = model_config_with_proxy.get("ti2t_model", "")
        else:
            model = model_config_with_proxy.get("t2t_model", "")
        
        # 设置到 config 中供后续使用
        model_config_with_proxy["model"] = model
        
        # TI2T 模式：直接走 VLM 路径
        if mode == "TI2T":
            return self._process_vlm(prompt, model_config_with_proxy, image, output_language, enable_web_search, optimize_query, num_results, role)
        
        if self._is_ti2t_model(provider, model):
            print(f"[LiveSearch] Notice: {provider} / {model} 属于 TI2T 视觉模型，当前运行于 T2T 模式，将仅使用文本能力。")
        elif self._is_dual_mode_model(provider, model):
            print(f"[LiveSearch] Notice: {provider} / {model} 支持多模态，但可向下兼容文本，目前按 T2T 模式执行。")
        
        # If web search is disabled, use LLM directly without search
        if not enable_web_search:
            print("[LiveSearch] Web search disabled, using LLM directly")
            return self._direct_llm_response(prompt, model_config_with_proxy, output_language, role)
        
        # 1. Determine Search Query
        search_query = prompt
        optimized_prompt_output = "No optimization (using original prompt)"
        
        # Extract coordinates from prompt and convert to location name
        location_name = None
        city_name = None  # Simplified city name for search
        weather_context = "" # Store precise weather data
        coordinate_pattern = r'(-?\d+\.?\d*)\s*[,，]\s*(-?\d+\.?\d*)'
        coord_match = re.search(coordinate_pattern, prompt)
        
        print(f"[LiveSearch] GEOPY_AVAILABLE: {GEOPY_AVAILABLE}, coord_match: {coord_match is not None}")
        
        if coord_match:
            try:
                lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                
                # 1. Fetch precise weather data (Open-Meteo)
                weather_context = SearchTool.get_weather_data(lat, lon, proxy=valid_proxy)
                if weather_context:
                    print(f"[LiveSearch] Precise weather data fetched for {lat}, {lon}")
                
                # 2. Reverse Geocoding (Geopy)
                if GEOPY_AVAILABLE:
                    print(f"[LiveSearch] Detected coordinates: {lat}, {lon}, attempting reverse geocoding...")
                    geolocator = Nominatim(user_agent="comfyui_live_search")
                    location = geolocator.reverse((lat, lon), timeout=10, language='en')
                    
                    if location:
                        # Extract city/country from address
                        address = location.raw.get('address', {})
                        city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
                        state = address.get('state', '') or address.get('state_district', '')
                        country = address.get('country', '')
                        location_name = f"{city}, {country}" if city else country
                        # Extract city and district for more precise search queries
                        city_name = city or state or address.get('region', '')
                        # Also extract district/suburb if available (for Beijing Haidian case)
                        district = address.get('suburb', '') or address.get('district', '')
                        if district and city_name:
                            # Store both city and district for "timeanddate Beijing Haidian" format
                            city_name = f"{city_name} {district}"
                        print(f"[LiveSearch] Reverse geocoded to: {location_name} (city: {city_name})")
            except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
                print(f"[LiveSearch] Coordinate processing failed: {e}, will rely on LLM optimization")
        
        # Apply prompt optimization if enabled
        if optimize_query:
            # If we have city name from geopy, inject simplified location info
            optimization_prompt = prompt
            if city_name:
                # Use just city name for cleaner search queries
                optimization_prompt = f"{prompt} (Location: {city_name})"
            elif location_name:
                optimization_prompt = f"{prompt} (Location: {location_name})"
            
            refine_messages = [
                {"role": "system", "content": """You are a Search Query Generator Tool.
Your ONLY task is to extract key terms to form a search query for a search engine (like DuckDuckGo).

CRITICAL RULES:
1. DO NOT answer the user's question.
2. DO NOT generate any data, facts, time, or weather info.
3. Output ONLY the raw search keywords string. No quotes, no prefixes.
4. **ALWAYS output the search query in ENGLISH.** Even if the input is Chinese or other languages, translate key terms to English (e.g., "北京" -> "Beijing").
   - English queries generally return better results from international sources like timeanddate.com.
5. If location name is provided in parentheses, prioritize using "City Country" format to avoid ambiguity (e.g., "Ia Greece" instead of "Ia").
6. Keep search queries SHORT - 3-6 words maximum.
7. For weather/time queries: use "current local time weather City Country".
   - Avoid using specific website names like "timeanddate" unless necessary.
   - Always include the Country name if the city is short or potentially ambiguous.

Examples:
Input: "北京现在的天气" -> Output: current weather Beijing China
Input: "What time is it in New York?" -> Output: current local time New York USA
Input: "coordinates ... (Location: New York)" -> Output: current local time weather New York USA
Input: "coordinates ... (Location: Ia Municipal Unit, Greece)" -> Output: current local time weather Ia Greece
Input: "Haidian District China current weather time (Location: Beijing Haidian)" -> Output: current local time weather Beijing Haidian China
Input: "Who won the Super Bowl 2024" -> Output: Super Bowl 2024 winner"""},
                {"role": "user", "content": optimization_prompt}
            ]
            refined_query = LLMClient.chat_completion(model_config_with_proxy, refine_messages)
            if not refined_query.startswith("Error"):
                print(f"[LiveSearch] Prompt optimized: {prompt} -> {refined_query}")
                optimized_prompt_output = f"Original: {prompt}\nOptimized: {refined_query}"
                if location_name:
                    optimized_prompt_output += f"\nLocation resolved: {location_name}"
                search_query = refined_query
            else:
                optimized_prompt_output = f"Optimization failed: {refined_query}"

        # 2. Perform Search
        print(f"[LiveSearch] Searching for: {search_query} using DuckDuckGo")
        
        search_results = SearchTool.search_duckduckgo(search_query, num_results, proxy=valid_proxy)
        
        if not search_results:
            return (f"No search results found using DuckDuckGo.", "", optimized_prompt_output)

        # 3. Extract Content (prioritize trusted domains and specific pages)
        context_data = []
        source_urls = []
        
        # Sort results: trusted domains first, and prioritize specific pages over homepages
        def sort_key(res):
            url = res.get('url', '')
            is_trusted = SearchTool.is_trusted_url(url)
            is_homepage = url.endswith('/') or url.count('/') <= 3  # Homepage has few slashes
            # Trusted + specific page = highest priority (0)
            # Trusted + homepage = medium priority (1)
            # Untrusted = lowest priority (2)
            if is_trusted and not is_homepage:
                return 0
            elif is_trusted:
                return 1
            else:
                return 2
        
        sorted_results = sorted(search_results, key=sort_key)
        
        for res in sorted_results:
            url = res.get('url', '')
            title = res.get('title', '')
            summary = res.get('summary', '')
            
            # Skip empty or invalid URLs
            if not url or not url.startswith(('http://', 'https://')):
                continue
            
            # Skip timeanddate.com homepage - we want specific location pages
            if url == 'https://www.timeanddate.com/' or url == 'https://www.timeanddate.com':
                print(f"[LiveSearch] Skipping timeanddate.com homepage, looking for specific page")
                continue
            
            print(f"[LiveSearch] Fetching: {url}")
            content = SearchTool.fetch_url_content(url, proxy=valid_proxy)
            
            if content:
                # For timeanddate.com, use more content since we extract it more precisely
                snippet_length = 3000 if 'timeanddate.com' in url else 2000
                snippet = content[:snippet_length] if content else summary
                context_data.append(f"Source: {title} ({url})\nSummary: {summary}\nContent: {snippet}\n---")
                source_urls.append(url)
                
                # If we have enough trusted sources with actual content, we can stop early
                trusted_with_content = [s for s in source_urls if SearchTool.is_trusted_url(s) and s not in ['https://www.timeanddate.com/', 'https://www.timeanddate.com']]
                if len(trusted_with_content) >= 2:
                    print("[LiveSearch] Found enough trusted sources with content, stopping early")
                    break
        
        full_context = "\n".join(context_data)
        
        # Inject precise weather data if available (Highest Priority)
        if weather_context:
            full_context = f"{weather_context}\n\n--- Web Search Results ---\n{full_context}"

        # 4. Generate Answer
        # Determine output language instruction
        language_instruction = ""
        if output_language == "English":
            language_instruction = "You MUST answer in English."
        else: # Default to Chinese
            language_instruction = "You MUST answer in Chinese (简体中文)."
        
        # Use custom role if provided, otherwise use default system prompt
        if role and role.strip():
            system_prompt = f"{role}\n\nSystem Rules:\n1. {language_instruction}\n2. Base your answer on the provided search results."
        else:
            system_prompt = f"""You are a helpful assistant with access to real-time web search results. 
Rules:
1. {language_instruction}
2. Base your answer ONLY on the provided search results
3. Prioritize information from professional weather/time websites (timeanddate.com, accuweather.com, openweathermap.org, weather.com, wunderground.com)
4. If you see timeanddate.com results, extract the EXACT time and weather data from the content:
   - Look for time patterns like "12:31:03 am CST", "Tuesday, November 25, 2025", "UTC+8", "CST (China Standard Time)"
   - Look for weather patterns like "36 °F", "Chilly", "47 / 29 °F", "Partly cloudy", temperature forecasts, weather descriptions
   - Extract ALL numerical values (temperatures, times, dates) exactly as shown in the content
5. If results contain time/weather info, be precise with numbers and units - include the exact values you see
6. If search results don't contain real-time data, clearly state that and suggest using a dedicated weather service
7. Keep the answer concise and well-structured, but include all relevant time and weather details"""

        final_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {prompt}\n\nSearch Results:\n{full_context}"}
        ]

        answer = LLMClient.chat_completion(model_config_with_proxy, final_messages)
        
        return (answer, "\n".join(source_urls), optimized_prompt_output)
    
    def _direct_llm_response(self, prompt, model_config, output_language, role=""):
        """
        Direct LLM response without web search
        Used when enable_web_search is False
        """
        # Determine output language instruction
        language_instruction = ""
        if output_language == "English":
            language_instruction = "You MUST answer in English."
        else: # Default to Chinese
            language_instruction = "You MUST answer in Chinese (简体中文)."
        
        # Use custom role if provided, otherwise use default system prompt
        if role and role.strip():
            system_prompt = f"{role}\n\nSystem Rules:\n1. {language_instruction}"
        else:
            system_prompt = f"""You are a helpful assistant.
Rules:
1. {language_instruction}
2. Answer the user's question directly based on your knowledge
3. Be concise and well-structured"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        answer = LLMClient.chat_completion(model_config, messages)
        
        if answer.startswith("Error"):
            return (f"Error: {answer}", "", "No optimization (direct LLM mode)")
        
        return (answer, "", "No optimization (direct LLM mode, web search disabled)")
    
    def _process_vlm(self, prompt, model_config, image, output_language, enable_web_search, optimize_query, num_results, role=""):
        """
        Handle TI2T 模式：将 ComfyUI IMAGE 编码为 base64 并调用 VLM
        Supports Web Search by calling VLM twice: 1. Extract Keywords 2. Final Answer
        """
        provider = model_config.get("provider", "")
        model = model_config.get("model", "")
        valid_proxy = model_config.get("proxy")
        
        if Image is None:
            return ("当前环境缺少 Pillow 库，无法处理图像输入。请安装 pillow>=9.0 后重试。", "", "TI2T mode unavailable (Pillow missing)")
        
        if not self._is_ti2t_model(provider, model):
            # Get all supported TI2T models for current provider
            provider_models = self.TI2T_MODELS.get(provider, set())
            if provider_models:
                supported = ", ".join(sorted(provider_models))
                message = f"TI2T 模式：{provider} 的 {model} 不支持视觉输入。该供应商支持的视觉模型：{supported}"
            else:
                # List all providers that support TI2T
                supported_providers = [p for p, models in self.TI2T_MODELS.items() if models]
                providers_str = ", ".join(supported_providers)
                message = f"TI2T 模式：{provider} 不支持视觉模型。支持的供应商：{providers_str}"
            print(f"[LiveSearch] {message}")
            return (message, "", "TI2T mode unsupported model")
        
        if image is None:
            return ("TI2T 模式需要连接 IMAGE 输入端口，请提供图片后再试。", "", "TI2T mode missing image")
        
        image_b64 = self._image_to_base64(image)
        if not image_b64:
            return ("无法读取或编码输入图像，请确认图像张量有效。", "", "TI2T mode image encoding failed")
        
        # Determine language instruction
        language_instruction = ""
        if output_language == "English":
            language_instruction = "You MUST answer in English."
        else: # Default to Chinese
            language_instruction = "你必须使用简体中文回答。"
            
        # Reverse Geocoding for VLM
        location_hint = ""
        weather_context = "" # Store precise weather data
        coordinate_pattern = r'(-?\d+\.?\d*)\s*[,，]\s*(-?\d+\.?\d*)'
        coord_match = re.search(coordinate_pattern, prompt)
        
        if coord_match:
            try:
                lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                
                # 1. Fetch precise weather data (Open-Meteo)
                weather_context = SearchTool.get_weather_data(lat, lon, proxy=valid_proxy)
                if weather_context:
                    print(f"[LiveSearch VLM] Precise weather data fetched for {lat}, {lon}")
                
                # 2. Reverse Geocoding
                if GEOPY_AVAILABLE:
                    print(f"[LiveSearch VLM] Detected coordinates: {lat}, {lon}, attempting reverse geocoding...")
                    geolocator = Nominatim(user_agent="comfyui_live_search_vlm")
                    location = geolocator.reverse((lat, lon), timeout=10, language='en')
                    if location:
                        address = location.raw.get('address', {})
                        city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
                        country = address.get('country', '')
                        if city:
                            location_name = f"{city}, {country}" if country else city
                            location_hint = f" (Location identified from coordinates: {location_name})"
                            print(f"[LiveSearch VLM] Reverse geocoded: {location_name}")
            except Exception as e:
                print(f"[LiveSearch VLM] Coordinate processing failed: {e}")

        # --- Web Search Logic ---
        if enable_web_search:
            search_query = prompt
            optimized_prompt_output = "No optimization (VLM Search mode)"
            
            # Step 1: Generate Search Query using VLM (if optimization enabled)
            if optimize_query:
                print("[LiveSearch] VLM Step 1: Analyzing image to generate search query...")
                query_gen_system = """You are a Visual Search Assistant.
Your task is to analyze the image and the user's question to generate a search query for a search engine.
Rules:
1. Output ONLY the search keywords in ENGLISH.
2. Identify the main subject in the image (e.g., landmarks, plants) and combine it with the user's intent.
3. For weather/time queries: ALWAYS use format "current local time weather [Subject/Location] [Country]".
   - Example: "current local time weather Eiffel Tower Paris France"
4. Keep the query precise (avoid full sentences), but include necessary location details (City, Country).
5. **FORBIDDEN**: Do not use vague terms like "this location", "here", "the image". You MUST replace them with the specific identified entity name (e.g., "Eiffel Tower").
6. Do not answer the question yet."""
                
                query_gen_content = [
                    self._build_image_content(image_b64, provider, model),
                    {"type": "text", "text": f"User Question: {prompt}{location_hint}\nGenerate a search query:"}
                ]
                
                query_messages = [
                    {"role": "system", "content": query_gen_system},
                    {"role": "user", "content": query_gen_content}
                ]
                
                generated_query = LLMClient.chat_completion(model_config, query_messages)
                
                if not generated_query.startswith("Error"):
                    search_query = generated_query.strip()
                    print(f"[LiveSearch] VLM Generated Query: {search_query}")
                    optimized_prompt_output = f"User Prompt: {prompt}\nVLM Generated Query: {search_query}"
                else:
                    print(f"[LiveSearch] VLM Query Generation failed: {generated_query}")
            
            # Step 2: Perform Search
            print(f"[LiveSearch] Searching for: {search_query} using DuckDuckGo")
            search_results = SearchTool.search_duckduckgo(search_query, num_results, proxy=valid_proxy)
            
            context_data = []
            source_urls = []
            
            if search_results:
                # Sort results: trusted domains first, and prioritize specific pages over homepages
                def sort_key(res):
                    url = res.get('url', '')
                    is_trusted = SearchTool.is_trusted_url(url)
                    is_homepage = url.endswith('/') or url.count('/') <= 3
                    if is_trusted and not is_homepage:
                        return 0
                    elif is_trusted:
                        return 1
                    else:
                        return 2
                
                sorted_results = sorted(search_results, key=sort_key)
                
                for res in sorted_results:
                    url = res.get('url', '')
                    title = res.get('title', '')
                    summary = res.get('summary', '')
                    
                    # Skip empty or invalid URLs
                    if not url or not url.startswith(('http://', 'https://')):
                        continue
                    
                    # Skip timeanddate.com homepage
                    if url == 'https://www.timeanddate.com/' or url == 'https://www.timeanddate.com':
                        continue
                    
                    print(f"[LiveSearch] Fetching: {url}")
                    content = SearchTool.fetch_url_content(url, proxy=valid_proxy)
                    
                    if content:
                        snippet_length = 3000 if 'timeanddate.com' in url else 2000
                        snippet = content[:snippet_length] if content else summary
                        context_data.append(f"Source: {title} ({url})\nSummary: {summary}\nContent: {snippet}\n---")
                        source_urls.append(url)
                        
                        # Early stop if we have enough trusted content
                        trusted_with_content = [s for s in source_urls if SearchTool.is_trusted_url(s) and s not in ['https://www.timeanddate.com/', 'https://www.timeanddate.com']]
                        if len(trusted_with_content) >= 2:
                            print("[LiveSearch] Found enough trusted sources with content, stopping early")
                            break
                    else:
                         # Fallback to summary if fetch fails
                         context_data.append(f"Source: {title} ({url})\nSummary: {summary}\n(Content fetch failed)\n---")
                         source_urls.append(url)
            
            full_context = "\n".join(context_data) if context_data else "No search results found."
            
            # Inject precise weather data if available (Highest Priority)
            if weather_context:
                full_context = f"{weather_context}\n\n--- Web Search Results ---\n{full_context}"
            
            # Step 3: Final Answer
            print("[LiveSearch] VLM Step 2: Generating final answer with search context...")
            
            # Enhanced language instruction
            lang_suffix = ""
            if output_language == "中文":
                language_instruction = "Answer in Chinese (简体中文). 必须使用中文回答。"
                lang_suffix = "(请用中文回答)"
            elif output_language == "English":
                language_instruction = "Answer in English."
                lang_suffix = "(Please answer in English)"
            
            final_system_prompt = f"""You are a vision-language assistant with access to web search results.
Rules:
1. {language_instruction}
2. Answer the user's question by combining visual information from the image and the provided search results.
3. If search results contain specific data (time, temperature), include them in your answer.
4. **CONFLICT RESOLUTION**: The image is static/historical. If the search results (real-time data) contradict the image (e.g., image shows day, search says night), **TRUST THE SEARCH RESULTS** for current status.
5. If the search results are summaries without specific data, summarize what is available but try to be helpful.
6. Be concise."""
            
            if role and role.strip():
                 final_system_prompt = f"{role}\n\nSystem Rules:\n1. {language_instruction}\n2. Use provided search results and image."

            final_user_content = [
                self._build_image_content(image_b64, provider, model),
                {"type": "text", "text": f"User Question: {prompt} {lang_suffix}\n\nSearch Results:\n{full_context}"}
            ]
            
            final_messages = [
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": final_user_content}
            ]
            
            answer = LLMClient.chat_completion(model_config, final_messages)
            return (answer, "\n".join(source_urls), optimized_prompt_output)

        # --- Direct VLM (No Search) ---
        else:
            print("[LiveSearch] VLM Direct Mode (No Search)")
            system_prompt = f"""You are a vision-language assistant.
Rules:
1. {language_instruction}
2. Describe or analyze the provided image based on the user's request.
3. Be concise but cover all visible facts. Avoid hallucinating invisible details."""
            
            if role and role.strip():
                system_prompt = f"{role}\n\nSystem Rules:\n1. {language_instruction}"

            user_content = [
                self._build_image_content(image_b64, provider, model),
                {"type": "text", "text": prompt} if prompt.strip() else {"type": "text", "text": "Describe this image."}
            ]
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            answer = LLMClient.chat_completion(model_config, messages)
            return (answer, "", "TI2T mode (direct vision response)")
    
    def _image_to_base64(self, image_tensor):
        """
        Convert ComfyUI IMAGE tensor to base64 encoded PNG
        """
        try:
            if isinstance(image_tensor, list):
                image_tensor = image_tensor[0]
            
            if image_tensor is None:
                return None
            
            tensor = image_tensor
            if hasattr(tensor, "cpu"):
                tensor = tensor.detach().cpu()
            else:
                return None
            
            if tensor.ndim == 4:
                tensor = tensor[0]
            
            # Ensure channel-last for Pillow
            if tensor.ndim == 3 and tensor.shape[0] in (1, 3, 4) and tensor.shape[-1] not in (1, 3, 4):
                tensor = tensor.permute(1, 2, 0)
            
            array = tensor.clamp(0, 1).mul(255).byte().numpy()
            if array.ndim == 2 or array.shape[-1] == 1:
                array = array.squeeze()
            
            mode = "RGB"
            if array.ndim == 2:
                mode = "L"
            elif array.shape[-1] == 4:
                mode = "RGBA"
            
            pil_image = Image.fromarray(array, mode=mode)
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"[LiveSearch] Failed to encode image for TI2T: {e}")
            return None
    
    @staticmethod
    def _build_image_content(image_b64, provider, model):
        """
        Build image content for different providers
        Returns the appropriate image_url format based on provider
        """
        base64_url = f"data:image/png;base64,{image_b64}"
        
        # Check if model supports base64 (GLM-4V-Flash does not support base64)
        if "智谱AI" in provider or "Zhipu" in provider:
            # GLM-4V-Flash does not support base64 encoding
            if "glm-4v-flash" in model.lower():
                print(f"[LiveSearch] Warning: {model} does not support base64 encoding. Image upload may fail.")
            
            # Zhipu AI format: no 'detail' parameter
            return {
                "type": "image_url",
                "image_url": {"url": base64_url}
            }
        
        # OpenAI format (includes 'detail' parameter)
        return {
            "type": "image_url",
            "image_url": {"url": base64_url, "detail": "auto"}
        }
    
    @classmethod
    def _is_ti2t_model(cls, provider, model):
        return model in cls.TI2T_MODELS.get(provider, set())
    
    @classmethod
    def _is_dual_mode_model(cls, provider, model):
        return model in cls.DUAL_MODE_MODELS.get(provider, set())
    

NODE_CLASS_MAPPINGS = {
    "LiveSearch_Agent": LiveSearch_Agent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_Agent": "🌐 Live Search Agent"
}

