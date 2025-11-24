import os
from .api_loader import LiveSearch_API_Loader
from .search_settings import LiveSearch_Settings
from .search_agent import LiveSearch_Agent

NODE_CLASS_MAPPINGS = {
    "LiveSearch_API_Loader": LiveSearch_API_Loader,
    "LiveSearch_Settings": LiveSearch_Settings,
    "LiveSearch_Agent": LiveSearch_Agent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearch_API_Loader": "🔑 Live Search API Loader",
    "LiveSearch_Settings": "⚙️ Live Search Settings",
    "LiveSearch_Agent": "🌐 Live Search Agent",
}

# Web directory for frontend extensions
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

