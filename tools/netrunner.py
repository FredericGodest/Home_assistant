import whois
import dns.resolver
import subprocess
import logging
from langchain_core.tools import tool

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


@tool
def scan_local_network(target: str = "192.168.1.0/24") -> str:
    """
    Scanne le réseau local avec nmap.
    
    Args:
        target: Cible nmap — IP unique, range CIDR ou hostname.
                Ex: '192.168.1.0/24', '192.168.1.1', '192.168.1.1-50'
    
    Returns:
        Résultat brut du scan nmap.
    """
    try:
        # -sn : ping scan (pas de port scan) — rapide pour découverte d'hôtes
        # -T4 : timing agressif
        # --open : seulement les hôtes qui répondent
        cmd = ["nmap", "-sn", "-T4", target]
        logger.info(f"Lancement nmap : {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"nmap stderr: {result.stderr}")
            return f"Erreur nmap : {result.stderr}"
        
        return result.stdout or "Aucun résultat retourné."
    
    except FileNotFoundError:
        return "nmap n'est pas installé. Installe-le : sudo apt install nmap"
    except subprocess.TimeoutExpired:
        return "Timeout : le scan a dépassé 60 secondes."
    except Exception as e:
        logger.exception("Erreur inattendue lors du scan nmap")
        return f"Erreur : {str(e)}"