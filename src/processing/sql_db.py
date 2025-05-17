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
    """
    SQLiteDB is a class that provides functionality to interact with an SQLite database. 
    It allows setting up the database by reading CSV files from a specified directory 
    and storing their contents into a single table within the SQLite database.
    Attributes:
        table_dir (str): Directory where the CSV files are stored.
        sqlite_path (str): Path to the SQLite database file.
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine for interacting with the SQLite database.
    Methods:
        __init__():
            Initializes the SQLiteDB instance by setting up the paths and creating the SQLAlchemy engine.
        get_csv_files(dir: str) -> list:
            Retrieves a list of CSV file names from the specified directory.
        sqlite_setup():
            Sets up the SQLite database by:
            - Ensuring the directory for the SQLite file exists.
            - Reading all CSV files from the specified directory.
            - Combining the data from all CSV files into a single DataFrame.
            - Saving the combined data into a table named 'aids_table' in the SQLite database.
    """
    
    def __init__(self):
        self.table_dir = PROCESSING_OUTPUT_DIR
        self.sqlite_path = f"{RAG_DATA_PATH}/{SQLITE_DATA_PATH}/{SQLITE_FILE_NAME}"
        self.engine = create_engine(f"sqlite:///{self.sqlite_path}")

    
    def get_csv_files(self, dir):
        """
        Retrieves a list of CSV files from the specified directory.

        Args:
            dir (str): The directory path to search for CSV files.

        Returns:
            list: A list of filenames (str) that have a '.csv' extension within the specified directory.
        """
        csv_files = [file for file in os.listdir(self.table_dir) if file.endswith('.csv')]
        return csv_files
    

    def sqlite_setup(self):
        """
        Sets up an SQLite database by reading CSV files from a specified directory,
        combining their data into a single table, and saving it to the database.
        This method performs the following steps:
        1. Ensures the directory for the SQLite database file exists.
        2. Reads all CSV files from the specified directory.
        3. Combines the data from all CSV files into a single DataFrame.
        4. Saves the combined data into an SQLite database table.
        Attributes:
            sqlite_path (str): The file path where the SQLite database will be saved.
            table_dir (str): The directory containing the CSV files to be processed.
            engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used to connect to the SQLite database.
        Raises:
            FileNotFoundError: If the specified directory for CSV files does not exist.
            ValueError: If no CSV files are found in the specified directory.
        Notes:
            - The database table is named 'aids_table'.
            - If the table already exists, it will be replaced.
            - The index of the DataFrame is not included in the database table.
        """

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