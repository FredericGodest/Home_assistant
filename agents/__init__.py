import os
from .basic_agent import create_basic_agents
from .netrunner_agent import create_netrunner_agents

basic_agent = create_basic_agents(os.getenv("API_KEY_MAMMOUTH"))
netrunner_agent = create_netrunner_agents(os.getenv("API_KEY_MAMMOUTH"))