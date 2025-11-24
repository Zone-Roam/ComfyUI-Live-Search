from .live_search import LiveSearchNode
from .api_loader import LiveSearch_API_Loader
from .search_settings import LiveSearch_Settings
from .search_agent import LiveSearch_Agent

NODE_CLASS_MAPPINGS = {
    "LiveSearchNode": LiveSearchNode,  # Keep for backward compatibility
    "LiveSearch_API_Loader": LiveSearch_API_Loader,
    "LiveSearch_Settings": LiveSearch_Settings,
    "LiveSearch_Agent": LiveSearch_Agent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LiveSearchNode": "🌐 Live Search (Legacy)",  # Mark as legacy
    "LiveSearch_API_Loader": "🔑 Live Search API Loader",
    "LiveSearch_Settings": "⚙️ Live Search Settings",
    "LiveSearch_Agent": "🌐 Live Search Agent",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

