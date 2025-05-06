AIDS_DIR = "data"
EMBEDDING_MODEL = "text-embedding-3-large"

# text splitting
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# FAISS building
CHUNK_PROCESSING_SIZE = 200
SLEEP_TIME = 30
FAISS_PERSIST_PATH = "rag_data/faiss/vanilla_vectorstore"
BM25_PERSIST_PATH = "rag_data/bm25/vanilla_bm25.pkl"