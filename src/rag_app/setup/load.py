import os

from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader

from src.rag_app.setup.params import AIDS_DIR


class RAGLoader:
    def __init__(self, aids_dir=AIDS_DIR):

        self.aids_dir = aids_dir
        self.list_pdf = self.get_all_pdfs(self.aids_dir)
        self.list_md = self.get_all_cards(self.aids_dir)


    def get_all_pdfs(self, dir):
        pdfs = []
        for root, _, files in os.walk(dir):
            for file in files:
                if file.endswith('.pdf'):
                    pdfs.append(os.path.join(root, file))
        return pdfs
    

    def get_all_cards(self, dir):
        markdown_cards = []
        for root, _, files in os.walk(dir):
            for file in files:
                if file.endswith('_card.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if len(lines) > 5:  # Verifica si el archivo tiene más de 5 líneas
                            markdown_cards.append(file_path)
        
        return markdown_cards
    

    def load_documents(self):
        # Leer ficheros Markdown
        markdown_docs = []
        for file in self.list_md:
            loader = TextLoader(file, encoding='utf-8')
            markdown_docs.extend(loader.load())

        # Leer ficheros PDF
        pdf_docs = []
        for file in self.list_pdf:
            loader = PyPDFLoader(file)
            pdf_docs.extend(loader.load())

        # Unir todos los documentos
        total_docs = markdown_docs + pdf_docs

        return total_docs