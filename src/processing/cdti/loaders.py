import os
from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader

from src.processing.cdti.params import DATA_PATH

class CDTILoader:

    def __init__(self, aid_name):

        self.aid_name = aid_name

        self.aid_path = f"{DATA_PATH}/{self.aid_name}"
        self.description_path = f"{self.aid_path}/{self.aid_name}_description.md"
        self.card_path = f"{self.aid_path}/{self.aid_name}_card.md"
        self.metadata_path = f"{self.aid_path}/{self.aid_name}_metadata.md"

        pdf_name = self.find_pdf()
        self.pdf_path = f"{self.aid_path}/{pdf_name}"


    def find_pdf(self):
        for archivo in os.listdir(self.aid_path):
            if archivo.endswith(".pdf"):
                return archivo  # Devuelve el nombre del primer PDF encontrado
        return None  # Si no se encuentra ningún PDF


    def load_markdown(self):
        # description
        loader = TextLoader(self.description_path, encoding="utf-8")
        docs = loader.load()
        description = docs[0].page_content

        # card
        loader = TextLoader(self.card_path, encoding="utf-8")
        docs = loader.load()
        card = docs[0].page_content

        # metadata
        loader = TextLoader(self.metadata_path, encoding="utf-8")
        docs = loader.load()
        metadata = docs[0].page_content

        # join
        markdown_document = description + "\n\n" + card + "\n\n" + metadata

        return markdown_document
    

    def load_pdf(self):
        loader = PyPDFLoader(self.pdf_path)
        pdf_document = loader.load()

        return pdf_document





