import sqlite3
from contextlib import closing
from pathlib import Path

# Chemin absolu pour éviter les surprises selon le répertoire de lancement
DB_PATH = Path(__file__).parent / "history_chat.db"


def init_db() -> None:
    """Crée la table si elle n'existe pas. Idempotent — appelé au démarrage."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime')),
                question TEXT NOT NULL,
                response TEXT,
                status TEXT DEFAULT 'success'
            )
            """
        )
        conn.commit()


def log(question: str, response: str | None, status: str = "success") -> None:
    """Log une conversation. Best-effort : ne casse jamais l'API."""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.execute(
                "INSERT INTO conversations (question, response, status) VALUES (?, ?, ?)",
                (question, response, status),
            )
            conn.commit()
    except Exception:
        pass  # logging best-effort, on ne fait pas planter /ask pour un log raté