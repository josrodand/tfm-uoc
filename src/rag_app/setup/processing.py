
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.rag_app.setup.params import CHUNK_SIZE, CHUNK_OVERLAP

class RAGProcessing:

    def __init__(self, data):
        self.data = data
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP


    def standard_processing(self):

        text_splitter=RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,chunk_overlap=self.chunk_overlap)
        text_splits=text_splitter.split_documents(self.data)

        return text_splits
    

    def contextual_processing(self):
        pass

