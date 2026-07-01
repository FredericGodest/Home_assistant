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


def get_recent_history(max_exchanges: int = 5, max_chars: int = 4000) -> list[tuple[str, str]]:
    """
    Retourne les N derniers échanges (question, response) réussis.
    Ordonnés du plus ancien au plus récent pour injection dans le prompt.
    Tronqué si dépasse max_chars cumulés.
    """
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            rows = conn.execute(
                """
                SELECT question, response FROM conversations
                WHERE status = 'success' AND response IS NOT NULL
                ORDER BY id DESC
                LIMIT ?
                """,
                (max_exchanges,)
            ).fetchall()
        
        # Remet dans l'ordre chronologique
        rows = list(reversed(rows))
        
        # Tronque si trop verbeux
        result = []
        total_chars = 0
        for q, r in rows:
            total_chars += len(q) + len(r)
            if total_chars > max_chars:
                break
            result.append((q, r))
        
        return result

    except Exception:
        return []  # best-effort, même logique que log()