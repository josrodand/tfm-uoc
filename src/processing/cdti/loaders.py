import os
from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader

from src.processing.cdti.params import DATA_PATH

class CDTILoader:
    """
    A class to load and process data related to CDTI (Centre for the Development of Industrial Technology) aids.
    Attributes:
        aid_name (str): The name of the aid.
        aid_path (str): The base path for the aid's data.
        description_path (str): The path to the markdown file containing the aid's description.
        card_path (str): The path to the markdown file containing the aid's card information.
        metadata_path (str): The path to the markdown file containing the aid's metadata.
        pdf_path (str): The path to the PDF file associated with the aid.
    Methods:
        find_pdf():
            Searches for the first PDF file in the aid's directory and returns its name.
            Returns None if no PDF is found.
        load_markdown():
            Loads and combines the content of the description, card, and metadata markdown files.
            Returns:
                str: A single string containing the combined content of the markdown files.
        load_pdf():
            Loads the content of the PDF file associated with the aid.
            Returns:
                list: A list of documents representing the content of the PDF file.
    """

    def __init__(self, aid_name):

        self.aid_name = aid_name

        self.aid_path = f"{DATA_PATH}/{self.aid_name}"
        self.description_path = f"{self.aid_path}/{self.aid_name}_description.md"
        self.card_path = f"{self.aid_path}/{self.aid_name}_card.md"
        self.metadata_path = f"{self.aid_path}/{self.aid_name}_metadata.md"

        pdf_name = self.find_pdf()
        self.pdf_path = f"{self.aid_path}/{pdf_name}"


    def find_pdf(self):
        """
        Searches for the first PDF file in the directory specified by `self.aid_path`.

        Returns:
            str: The name of the first PDF file found in the directory.
            None: If no PDF file is found in the directory.
        """
        for archivo in os.listdir(self.aid_path):
            if archivo.endswith(".pdf"):
                return archivo  # Devuelve el nombre del primer PDF encontrado
        return None  # Si no se encuentra ningún PDF


    def load_markdown(self):
        """
        Loads and combines markdown content from three separate files: description, card, and metadata.
        This method reads the content of three files specified by `description_path`, `card_path`, 
        and `metadata_path` attributes. It uses the `TextLoader` class to load the content of each file, 
        extracts the text from the first document in each file, and concatenates them into a single 
        markdown document.
        Returns:
            str: A single markdown document containing the combined content of the description, 
            card, and metadata files.
        """
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
        """
        Loads a PDF document from the specified file path.
        This method uses the PyPDFLoader to load the PDF document located at 
        the path specified by `self.pdf_path`.
        Returns:
            pdf_document: The loaded PDF document object.
        """
        loader = PyPDFLoader(self.pdf_path)
        pdf_document = loader.load()

        return pdf_document





