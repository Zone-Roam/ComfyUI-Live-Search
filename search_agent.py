"""
LiveSearch Agent Node
Main search and summarization logic
Works with API Loader and Settings nodes for modular design
"""

import requests
import re
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
        except Exception as e:
            print(f"[LiveSearch] DuckDuckGo Search error: {e}")
            return []

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
    @staticmethod
    def chat_completion(llm_config, messages):
        """
        Generic OpenAI-compatible chat completion using config from API Loader
        """
        api_key = llm_config.get("api_key", "")
        base_url = llm_config.get("base_url", "")
        model = llm_config.get("model", "")
        temperature = llm_config.get("temperature", 0.7)
        max_tokens = llm_config.get("max_tokens", 2048)
        timeout = llm_config.get("timeout", 120)
        proxy = llm_config.get("proxy", None)
        provider = llm_config.get("provider", "")
        
        if not api_key:
            return "Error: API Key is missing."
            
        url = f"{base_url.rstrip('/')}/chat/completions"
        
        # Standard headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Volcengine specific adjustment: ensure no extra headers interfere, strictly follow OpenAI format
        if "Volcengine" in provider:
            # Volcengine (Ark) supports standard OpenAI format with Bearer token
            # Just ensuring stream is False is the key
            pass
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False # Explicitly disable stream as requested
        }
        
        # Remove max_tokens for o1 models as they don't support it
        if model.startswith("o1-"):
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
            
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected response format from LLM provider. Response: {data}"
                
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

class LiveSearch_Agent:
    """
    Main Search Agent Node
    Accepts LLM_CONFIG and SEARCH_SETTINGS from separate nodes
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "e.g., 北京现在的天气 / What is the weather in Beijing?"}),
                "llm_config": ("LLM_CONFIG",),
                "search_settings": ("SEARCH_SETTINGS",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("answer", "source_urls", "optimized_prompt")
    FUNCTION = "process_search"
    CATEGORY = "LiveSearch"
    
    def process_search(self, prompt, llm_config, search_settings):
        # Extract settings
        num_results = search_settings.get("num_results", 3)
        output_language = search_settings.get("output_language", "Auto (跟随输入)")
        optimize_prompt = search_settings.get("optimize_prompt", False)
        valid_proxy = search_settings.get("proxy")
        
        # Add proxy to llm_config for LLM calls
        llm_config_with_proxy = llm_config.copy()
        llm_config_with_proxy["proxy"] = valid_proxy
        
        # 1. Determine Search Query
        search_query = prompt
        optimized_prompt_output = "No optimization (using original prompt)"
        
        # Extract coordinates from prompt and convert to location name
        location_name = None
        city_name = None  # Simplified city name for search
        coordinate_pattern = r'(-?\d+\.?\d*)\s*[,，]\s*(-?\d+\.?\d*)'
        coord_match = re.search(coordinate_pattern, prompt)
        
        print(f"[LiveSearch] GEOPY_AVAILABLE: {GEOPY_AVAILABLE}, coord_match: {coord_match is not None}")
        
        if coord_match and GEOPY_AVAILABLE:
            try:
                lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
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
                print(f"[LiveSearch] Reverse geocoding failed: {e}, will rely on LLM optimization")
        
        # Apply prompt optimization if enabled
        if optimize_prompt:
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
4. If location name is provided in parentheses, use ONLY the city/district name (keep it simple).
5. Keep search queries SHORT - 2-3 words maximum.
6. For weather queries: use "city weather" (e.g., "Beijing weather" or "Haidian weather")
7. For time queries: use "city time" (e.g., "Beijing time" or "Haidian time")
8. For combined weather+time queries: ALWAYS use "timeanddate city district" format if district is provided
   (e.g., "timeanddate Beijing Haidian" or "timeanddate New York Manhattan")
   If only city is provided, use "timeanddate city" (e.g., "timeanddate Beijing")
   This ensures we find timeanddate.com which provides both weather and time information.

Examples:
Input: "What is the weather in Beijing?" -> Output: Beijing weather
Input: "What time is it in New York?" -> Output: New York time
Input: "coordinates 40.7128, -74.0060 weather time (Location: New York)" -> Output: timeanddate New York
Input: "Haidian District China current weather time (Location: Beijing Haidian)" -> Output: timeanddate Beijing Haidian
Input: "Who won the Super Bowl 2024" -> Output: Super Bowl 2024 winner"""},
                {"role": "user", "content": optimization_prompt}
            ]
            refined_query = LLMClient.chat_completion(llm_config_with_proxy, refine_messages)
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

        # 4. Generate Answer
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

        answer = LLMClient.chat_completion(llm_config_with_proxy, final_messages)
        
        return (answer, "\n".join(source_urls), optimized_prompt_output)

NODE_CLASS_MAPPINGS = {
    "LiveSearch_Agent": LiveSearch_Agent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_Agent": "🌐 Live Search Agent"
}

