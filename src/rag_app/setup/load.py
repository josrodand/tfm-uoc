import os

from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader

from src.rag_app.setup.params import AIDS_DIR


class RAGLoader:
    """
    A class to load and process documents from a specified directory. The class supports loading
    PDF files and Markdown files with a specific naming convention.
    Attributes:
        aids_dir (str): The directory containing the documents to be loaded.
        list_pdf (list): A list of paths to all PDF files in the specified directory.
        list_md (list): A list of paths to all Markdown files ending with '_card.md' in the specified directory.
    Methods:
        get_all_pdfs(dir):
            Recursively retrieves all PDF files from the given directory.
        get_all_cards(dir):
            Recursively retrieves all Markdown files ending with '_card.md' from the given directory.
            Only includes files with more than 5 lines of content.
        load_documents():
            Loads the content of all Markdown and PDF files found in the directory.
            Returns a combined list of all loaded documents.
    """
    def __init__(self, aids_dir=AIDS_DIR):

        self.aids_dir = aids_dir
        self.list_pdf = self.get_all_pdfs(self.aids_dir)
        self.list_md = self.get_all_cards(self.aids_dir)


    def get_all_pdfs(self, dir):
        """
        Retrieves a list of all PDF files within a specified directory and its subdirectories.

        Args:
            dir (str): The path to the directory to search for PDF files.

        Returns:
            list: A list of file paths to all PDF files found in the directory and its subdirectories.
        """
        pdfs = []
        for root, _, files in os.walk(dir):
            for file in files:
                if file.endswith('.pdf'):
                    pdfs.append(os.path.join(root, file))
        return pdfs
    

    def get_all_cards(self, dir):
        """
        Retrieves all markdown card files from a specified directory and its subdirectories.
        This method searches for files with names ending in '_card.md' within the given directory
        and its subdirectories. It reads each file and includes it in the result only if the file
        contains more than 5 lines.
        Args:
            dir (str): The root directory to search for markdown card files.
        Returns:
            list: A list of file paths to markdown card files that meet the criteria.
        """
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
        """
        Loads and combines documents from Markdown and PDF files.
        This method reads Markdown files and PDF files specified in the 
        `self.list_md` and `self.list_pdf` attributes, respectively. It uses 
        appropriate loaders to extract the content from these files and combines 
        them into a single list of documents.
        Returns:
            list: A list containing the content of all loaded Markdown and PDF 
            documents.
        """

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