from src.rag_app.setup.setup_rag import RAGSetup
from src.processing.sql_db import SQLiteDB

if __name__ == "__main__":
    
    # rag data setup
    rag_setup = RAGSetup()
    rag_setup.run()
    # sql data setup
    sqlite_db = SQLiteDB()
    sqlite_db.sqlite_setup()