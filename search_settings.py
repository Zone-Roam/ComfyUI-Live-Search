"""
LiveSearch Settings Node
Handles search configuration separately from API and main logic
"""

class LiveSearch_Settings:
    """
    Search Settings Node
    Configures search behavior and optimization options
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "num_results": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
                "output_language": (["Auto (跟随输入)", "中文", "English"], {"default": "Auto (跟随输入)"}),
                "optimize_prompt": ("BOOLEAN", {"default": False, "label_on": "Optimize ON", "label_off": "Optimize OFF"}),
            },
            "optional": {
                "proxy": ("STRING", {"default": "", "placeholder": "http://127.0.0.1:7890 (Optional)"}),
            }
        }
    
    RETURN_TYPES = ("SEARCH_SETTINGS",)
    RETURN_NAMES = ("search_settings",)
    FUNCTION = "load_settings"
    CATEGORY = "LiveSearch"
    
    def load_settings(self, num_results, output_language, optimize_prompt, proxy=""):
        """
        Load search settings
        Returns a settings dict that can be passed to the search agent
        """
        search_settings = {
            "num_results": num_results,
            "output_language": output_language,
            "optimize_prompt": optimize_prompt,
            "proxy": proxy.strip() if proxy else None
        }
        
        print(f"[LiveSearch Settings] Configured: {num_results} results, Language: {output_language}, Optimize: {optimize_prompt}")
        
        return (search_settings,)

NODE_CLASS_MAPPINGS = {
    "LiveSearch_Settings": LiveSearch_Settings
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_Settings": "⚙️ Live Search Settings"
}

