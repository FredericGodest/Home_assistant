import logging
from pathlib import Path
from langchain_core.tools import tool
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)

CHROMA_BASE_PATH = Path("chroma_db")
EMBED_MODEL = "all-MiniLM-L6-v2"
N_RESULTS = 5  # chunks retournés par query


def _query_collection(collection_name: str, query: str) -> str:
    chroma_path = CHROMA_BASE_PATH / collection_name
    client = chromadb.PersistentClient(path=str(chroma_path))
    
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    collection = client.get_collection(name=collection_name, embedding_function=ef)

    results = collection.query(query_texts=[query], n_results=N_RESULTS)
    
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    if not docs:
        return "Aucun document pertinent trouvé."

    output = []
    for doc, meta in zip(docs, metas):
        output.append(f"[{meta['source']} - p.{meta['page']}]\n{doc}")
    
    return "\n\n---\n\n".join(output)


@tool
def query_maison(query: str) -> str:
    """Recherche dans les documents de la maison : contrats, factures, assurances, diagnostics, etc. "
       Utilise cet outil pour toute question sur la maison ou ses documents administratifs.
    """

    return _query_collection("maison", query)

@tool
def query_appareil(query: str) -> str:
    """Recherche dans les manuels des appareils de la maison : 
        lave linge, lave vaisselle, machine à café, appareil photo nikon et sony etc. 
        Utilise cet outil pour toute question technique sur un appareil."""
    
    return _query_collection("appareil", query)

def query_appareil_test(query: str) -> str:
    """Recherche dans les manuels des appareils de la maison : 
        lave linge, lave vaisselle, machine à café, appareil photo nikon et sony etc. 
        Utilise cet outil pour toute question technique sur un appareil."""
    
    return _query_collection("appareil", query)

print(query_appareil_test("détartrage machine à café"))