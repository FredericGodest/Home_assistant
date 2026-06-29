from langchain.tools import tool
from datetime import datetime

@tool
def current_date() -> str:
    """Récupére la date d'aujourd'hui au format dd/MM/YYY"""

    current_date = datetime.today().strftime('%d-%m-%Y')

    return current_date