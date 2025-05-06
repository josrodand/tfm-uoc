# azure openai from langchain
import pandas as pd

from src.processing.utils import get_aid_list
from src.processing.params import PROCESSING_VARIABLES

from src.processing.cdti.loaders import CDTILoader
from src.processing.cdti.chains import CDTIChainBuilder
from src.processing.cdti.params import DATA_PATH, OUTPUT_FILE
from src.processing.cdti.prompts import RAG_PROMPTS

from time import sleep
from random import randint


class CDTIProcessingPipeline:

    def __init__(self):
        self.data_path = DATA_PATH


    def aid_processing(self, aid_name):

        print(f"Extracting aid: {aid_name}")
        cdti_loader = CDTILoader(aid_name)
        cdti_chain_builder = CDTIChainBuilder()
        
        # markdown extraction
        print("Excracting from markdown...")
        try:
            markdown_document = cdti_loader.load_markdown()
        except FileNotFoundError: 
            print("No markdown document found, proceeding without it.")
            markdown_document = None

        extraction_chain = cdti_chain_builder.build_extraction_chain()
        for attempt in range(3):  # Retry up to 3 times
            try:
                extraction_chain_result = extraction_chain.invoke({"document": markdown_document})
                break  # Exit the retry loop if successful
            except Exception as e:
                print(f"Attempt {attempt + 1} for markdown extraction failed: {e}")
                if attempt < 2:  # If not the last attempt, wait before retrying
                    sleep(2 + randint(0, 2))  # Add some randomness to delay
                else:
                    raise

        # pdf extraction
        print("Excracting from pdf...")
        try:
            pdf_document = cdti_loader.load_pdf()
        except FileNotFoundError:
            print("No PDF document found, proceeding without it.")
            pdf_document = None

        try:
            rag_chain = cdti_chain_builder.build_dynamic_rag_chain(pdf_document)
        except Exception as e:
            print(f"Failed to create rag_chain: {e}")
            rag_chain = None

        extraction_rag_result = {}
        if rag_chain is None:
            print("rag_chain is None, returning empty values for RAG_PROMPTS keys.")
            extraction_rag_result = {key: '' for key in RAG_PROMPTS.keys()}
        else:
            for key, prompt in RAG_PROMPTS.items():
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        extraction_rag_result[key] = rag_chain.invoke(prompt)
                        break  # Exit the retry loop if successful
                    except Exception as e:
                        print(f"Attempt {attempt + 1} for key '{key}' failed: {e}")
                        if attempt < 2:  # If not the last attempt, wait before retrying
                            sleep(2 + randint(0, 2))  # Add some randomness to delay
                        else:
                            raise
        
        # Combine
        extraction_result = {**extraction_chain_result, **extraction_rag_result}

        return extraction_result
    

    def adjust_lines(self, df):

        rest_aids = df[df["nombre"] != "Proyectos de I + D"].copy()
        rest_aids["linea"] = ""

        aid_i_d = df[df["nombre"] == "Proyectos de I + D"].copy()

        lines = aid_i_d.iloc[0]['linea']
        lines = eval(lines) if isinstance(lines, str) and lines.startswith("[") and lines.endswith("]") else lines

        aid_i_d_repeated = pd.concat([aid_i_d] * len(lines), ignore_index=True)
        aid_i_d_repeated["linea"] = lines

        df_cleaned = pd.concat([aid_i_d_repeated, rest_aids], ignore_index=True)

        return df_cleaned


    def run_pipeline(self, persist = True):

        aid_list = get_aid_list(self.data_path)
        print("aids found:", len(aid_list))

        results = [self.aid_processing(aid_name) for aid_name in aid_list]

        df = pd.DataFrame(results)
        df = df[PROCESSING_VARIABLES]

        # hay que hacer lo de las lineas de proyectos de i+d
        df = self.adjust_lines(df)

        print("persisting results...")
        if persist:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Results persisted to {OUTPUT_FILE}")

        return df










