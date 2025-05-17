
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.rag_app.setup.params import CHUNK_SIZE, CHUNK_OVERLAP

class RAGProcessing:
    """
    A class for processing data for Retrieval-Augmented Generation (RAG) applications.
    Attributes:
        data (list): The input data to be processed, typically a list of documents.
        chunk_size (int): The size of each chunk when splitting the documents.
        chunk_overlap (int): The overlap size between consecutive chunks.
    Methods:
        standard_processing():
            Splits the input data into chunks using a RecursiveCharacterTextSplitter.
            Returns a list of text splits.
        contextual_processing():
            Placeholder method for future implementation of contextual processing.
    """

    def __init__(self, data):
        self.data = data
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP


    def standard_processing(self):
        """
        Perform standard processing on the input data by splitting it into smaller chunks.
        This method uses a RecursiveCharacterTextSplitter to divide the input documents 
        into smaller text chunks based on the specified chunk size and overlap.
        Returns:
            list: A list of text chunks obtained after splitting the input documents.
        """

        text_splitter=RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,chunk_overlap=self.chunk_overlap)
        text_splits=text_splitter.split_documents(self.data)

        return text_splits
    

    def contextual_processing(self):
        pass

