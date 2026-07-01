import whois
import dns.resolver
import subprocess
import logging
from langchain_core.tools import tool
import time
import re
import pandas as pd
import requests
import json

logger = logging.getLogger(__name__)

@tool
def scan_domain(domain: str) -> str:
    """Effectue une reconnaissance sur un domaine : WHOIS + enregistrements DNS (A, MX, NS)."""

    if "www" in domain:
        domain = domain.split("www.")[-1]

    result = []

    # --- WHOIS ---
    try:
        w = whois.whois(domain)
        result.append("=== WHOIS ===")
        result.append(f"Registrar   : {w.registrar}")
        result.append(f"Créé le     : {w.creation_date}")
        result.append(f"Expire le   : {w.expiration_date}")
        result.append(f"Propriétaire: {w.org or w.name or 'N/A'}")
        result.append(f"Pays        : {w.country or 'N/A'}")
    except Exception as e:
        result.append(f"WHOIS indisponible : {e}")

    # --- DNS ---
    result.append("\n=== DNS ===")
    for record_type in ["A", "MX", "NS"]:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            values = [r.to_text() for r in answers]
            result.append(f"{record_type:4} : {', '.join(values)}")
        except Exception:
            result.append(f"{record_type:4} : N/A")

    return "\n".join(result)


def get_vendor(mac: str) -> str:
    if mac == "<incomplet>":
        return "?"
    try:
        r = requests.get(f"https://api.macvendors.com/{mac}", timeout=3)
        return r.text if r.status_code == 200 else "inconnu"
    except:
        return "erreur"


@tool
def scan_local_network() -> str:
    """
    Scanne le réseau local avec arp. 
    Retourne un JSON string consommable par un agent.

    Returns:
        Tableau des appareils sur le réseau local avec hostname, IP, MAC et vendor.
    """
    for i in range(1, 255):
        subprocess.Popen(
            ["ping", "-c", "1", "-W", "1", f"192.168.1.{i}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    
    result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    
    devices = {
        "hostname": [],
        "ip": [],
        "mac": [],
        "vendor": []
    }
    for line in result.stdout.splitlines():
        match = re.search(r'^(\S+)\s+\(([\d.]+)\)\s+[àa]\s+(\S+)', line)
        hostname = match.group(1)
        ip = match.group(2)
        mac = match.group(3)
        
        if match:
            if hostname == "?" and mac == "<incomplet>":
                continue
            elif mac == "<incomplet>":
                vendor = "?"
            else:
                vendor = get_vendor(mac)
                time.sleep(1)  # rate limit API gratuite
            
            devices["hostname"].append(hostname)
            devices["ip"].append(ip)
            devices["mac"].append(mac)
            devices["vendor"].append(vendor)
    
    df = pd.DataFrame(devices)
    
    result = df.to_json(orient="records")

    return result
