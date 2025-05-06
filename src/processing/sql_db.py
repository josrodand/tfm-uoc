import os
import pandas as pd
from sqlalchemy import create_engine

from src.processing.params import (
    PROCESSING_OUTPUT_DIR, 
    RAG_DATA_PATH, 
    SQLITE_DATA_PATH, 
    SQLITE_FILE_NAME
)

class SQLiteDB:
    
    def __init__(self):
        self.table_dir = PROCESSING_OUTPUT_DIR
        self.sqlite_path = f"{RAG_DATA_PATH}/{SQLITE_DATA_PATH}/{SQLITE_FILE_NAME}"
        self.engine = create_engine(f"sqlite:///{self.sqlite_path}")

    
    def get_csv_files(self, dir):
        csv_files = [file for file in os.listdir(self.table_dir) if file.endswith('.csv')]
        return csv_files
    

    def sqlite_setup(self):

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        csv_files = self.get_csv_files(self.table_dir)

        table_data = []

        for file in csv_files:
            filepath = f"{self.table_dir}{file}"
            print(f"loading {filepath}")
            df = pd.read_csv(filepath)
            table_data.append(df)

        table_data = pd.concat(table_data)

        df.to_sql('aids_table', con=self.engine, if_exists='replace', index=False)
        print(f"SQLite DB saved in: {self.sqlite_path}")