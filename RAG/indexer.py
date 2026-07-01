# rag/indexer.py
import logging
from pathlib import Path
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
CHROMA_BASE_PATH = Path("chroma_db")
EMBED_MODEL = "all-MiniLM-L6-v2"  # léger, local, bon rapport qualité/perf

COLLECTIONS = {
    "maison":   Path("documents/maison"),
    "appareil": Path("documents/appareil"),
}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def get_collection(client: chromadb.PersistentClient, name: str) -> chromadb.Collection:
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_or_create_collection(name=name, embedding_function=ef)


def ingest_folder(collection_name: str, folder: Path) -> None:
    if not folder.exists():
        logger.error(f"Dossier introuvable : {folder}")
        return

    pdfs = list(folder.glob("*.pdf"))
    if not pdfs:
        logger.warning(f"Aucun PDF dans {folder}")
        return

    chroma_path = CHROMA_BASE_PATH / collection_name
    chroma_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(chroma_path))
    collection = get_collection(client, collection_name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    for pdf_path in pdfs:
        logger.info(f"Ingestion : {pdf_path.name}")
        try:
            loader = PyPDFLoader(str(pdf_path))
            pages  = loader.load()
            chunks = splitter.split_documents(pages)

            # IDs déterministes → idempotent si on re-run
            ids  = [f"{pdf_path.stem}_chunk_{i}" for i in range(len(chunks))]
            docs = [c.page_content for c in chunks]
            metas = [
                {
                    "source": pdf_path.name,
                    "page":   c.metadata.get("page", 0),
                }
                for c in chunks
            ]

            collection.upsert(ids=ids, documents=docs, metadatas=metas)
            logger.info(f"  → {len(chunks)} chunks indexés")

        except Exception as e:
            logger.error(f"Erreur sur {pdf_path.name} : {e}")

    logger.info(f"✅ Collection '{collection_name}' prête ({collection.count()} chunks total)")


if __name__ == "__main__":
    for name, folder in COLLECTIONS.items():
        logger.info(f"=== Collection : {name} ===")
        ingest_folder(name, folder)
