import logging
from enum import Enum

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    NETRUNNER = "netrunner"
    BASIC = "basic"

# Mots-clés simples — suffisant pour commencer, pas besoin de classifier avec un LLM
NETRUNNER_KEYWORDS = [
    "nmap", "scan", "réseau", "port", "ip", "hôte", "ping",
    "network", "host", "vuln", "service", "firewall", "subnet"
]

def route(question: str) -> AgentType:
    q = question.lower()
    if any(kw in q for kw in NETRUNNER_KEYWORDS):
        logger.info("Router → NETRUNNER")
        return AgentType.NETRUNNER
    logger.info("Router → BASIC")
    return AgentType.BASIC