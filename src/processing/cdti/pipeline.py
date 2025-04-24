# azure openai from langchain
import pandas as pd

from src.processing.utils import get_aid_list

from src.processing.cdti.loaders import CDTILoader
from src.processing.cdti.chains import CDTIChainBuilder


from src.processing.cdti.params import DATA_PATH
from src.processing.cdti.prompts import RAG_PROMPTS

from src.processing.params import PROCESSING_VARIABLES


class CDTIProcessingPipeline:

    def __init__(self):
        self.data_path = DATA_PATH


    def aid_processing(self, aid_name):

        print(f"Extracting aid: {aid_name}")
        cdti_loader = CDTILoader(aid_name)
        cdti_chain_builder = CDTIChainBuilder()
        # load documents
        print("loading documents...")
        markdown_document = cdti_loader.load_markdown()
        pdf_document = cdti_loader.load_pdf()
        # chains
        print("Building chains...")
        extraction_chain = cdti_chain_builder.build_extraction_chain()
        rag_chain = cdti_chain_builder.build_dynamic_rag_chain(pdf_document)
        # extraction
        print("Excracting from markdown...")
        extraction_chain_result = extraction_chain.invoke({"document": markdown_document})
        print("Extracting from pdf...")
        extraction_rag_result = {key: rag_chain.invoke(prompt) for key, prompt in RAG_PROMPTS.items()}
        # Combine
        extraction_result = {**extraction_chain_result, **extraction_rag_result}

        return extraction_result


    def run_pipeline(self):

        aid_list = get_aid_list(self.data_path)[:2]
        print("aids found:", len(aid_list))

        results = [self.aid_processing(aid_name) for aid_name in aid_list]

        df = pd.DataFrame(results)[PROCESSING_VARIABLES]

        return df










