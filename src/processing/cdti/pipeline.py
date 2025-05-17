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
    """
    CDTIProcessingPipeline is a class designed to process and extract information from various aid-related documents 
    (markdown and PDF) and organize the results into a structured format.
    Methods:
        __init__():
            Initializes the pipeline with the required data path.
        aid_processing(aid_name):
            Processes a specific aid by extracting information from markdown and PDF documents.
            - Extracts data from markdown documents using an extraction chain with retry logic.
            - Extracts data from PDF documents using a dynamic RAG chain with retry logic.
            - Combines the results from markdown and PDF extractions into a single dictionary.
        adjust_lines(df):
            Adjusts the "linea" column in the DataFrame for specific aids.
            - Splits the "Proyectos de I + D" aid into multiple rows based on its "linea" values.
            - Ensures other aids remain unchanged.
        run_pipeline(persist=True):
            Executes the entire processing pipeline.
            - Retrieves a list of aids to process.
            - Processes each aid and organizes the results into a DataFrame.
            - Adjusts the "linea" column for specific aids.
            - Optionally persists the results to a CSV file.
            - Returns the final processed DataFrame.
    Attributes:
        data_path:
            Path to the directory containing the aid-related data.
    Constants (assumed to be defined elsewhere in the code):
        DATA_PATH:
            The base path for data files.
        RAG_PROMPTS:
            A dictionary of prompts used for RAG chain processing.
        PROCESSING_VARIABLES:
            A list of variables to include in the final DataFrame.
        OUTPUT_FILE:
            The file path where the processed results will be saved.
    """

    def __init__(self):
        self.data_path = DATA_PATH


    def aid_processing(self, aid_name):
        """
        Processes aid data by extracting information from markdown and PDF documents.
        Args:
            aid_name (str): The name of the aid to process.
        Returns:
            dict: A dictionary containing the combined extraction results from both
                markdown and PDF documents. Keys and values depend on the extraction
                logic and prompts defined in the pipeline.
        Workflow:
            1. Extracts data from a markdown document using a chain-based extraction process.
                - Retries up to 3 times in case of failure.
                - Handles missing markdown documents gracefully.
            2. Extracts data from a PDF document using a dynamic RAG (Retrieval-Augmented Generation) chain.
                - Retries up to 3 times for each prompt in case of failure.
                - Handles missing PDF documents gracefully.
            3. Combines the results from markdown and PDF extractions into a single dictionary.
        Exceptions:
            - Raises exceptions if all retry attempts fail during markdown or PDF extraction.
            - Handles `FileNotFoundError` for missing markdown or PDF documents by proceeding without them.
        Notes:
            - Introduces random delays between retries to avoid potential rate-limiting issues.
            - Relies on external components like `CDTILoader`, `CDTIChainBuilder`, and `RAG_PROMPTS`.
        """

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
        """
        Adjusts the "linea" column in the given DataFrame based on specific conditions.
        This function processes a DataFrame by separating rows where the "nombre" column 
        equals "Proyectos de I + D" and expanding those rows based on the values in the 
        "linea" column. For other rows, it clears the "linea" column.
        Args:
            df (pd.DataFrame): The input DataFrame containing at least the columns 
                            "nombre" and "linea".
        Returns:
            pd.DataFrame: A new DataFrame where rows with "nombre" equal to 
                        "Proyectos de I + D" are expanded based on the "linea" column, 
                        and other rows have their "linea" column cleared.
        """

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
        """
        Executes the data processing pipeline.
        This method processes a list of aids, applies transformations, and optionally
        persists the results to a CSV file.
        Args:
            persist (bool, optional): If True, the resulting DataFrame will be saved 
                to a CSV file. Defaults to True.
        Returns:
            pd.DataFrame: A DataFrame containing the processed results.
        Steps:
            1. Retrieves a list of aids from the specified data path.
            2. Processes each aid using the `aid_processing` method.
            3. Constructs a DataFrame from the results and filters it using 
            `PROCESSING_VARIABLES`.
            4. Adjusts the DataFrame using the `adjust_lines` method.
            5. Optionally persists the DataFrame to a CSV file.
        """

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










