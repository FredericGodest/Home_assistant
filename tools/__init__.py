from .weather import get_weather
from .search import search_tool
from .netrunner import scan_domain, scan_local_network
from .utils import current_date
from .camera import capture_and_detect
from .retriever import query_maison, query_appareil

STANDARD_TOOL_LIST = [get_weather, search_tool, current_date, capture_and_detect, query_maison, query_appareil]
NETRUNNER_TOOL_LIST = [scan_domain, scan_local_network, current_date]