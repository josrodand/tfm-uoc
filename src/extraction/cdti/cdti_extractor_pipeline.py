from src.extraction.cdti.cdti_matrix_extractor import CDTIMatrixExtractor
from src.extraction.cdti.cdti_aid_extractor import CDTIAidExtractor


class CDTIExtractorPipeline:
    """
    A pipeline class for extracting and processing data from CDTI (Centre for the Development of Industrial Technology).
    Methods
    -------
    __init__():
        Initializes the pipeline instance.
    run_pipeline():
        Executes the pipeline for extracting and processing data. This includes:
        - Extracting a matrix of data using `CDTIMatrixExtractor`.
        - Persisting the extracted matrix data.
        - Iterating through each aid in the matrix to extract detailed information using `CDTIAidExtractor`.
        - Persisting the extracted aid data.
    """

    def __init__(self):
        pass

    def run_pipeline(self):
        """
        Executes the CDTI extraction pipeline.
        This method performs the following steps:
        1. Extracts the CDTI matrix data using the `CDTIMatrixExtractor` class.
        - The extracted matrix data is persisted for future use.
        2. Iterates through each aid in the extracted matrix data:
        - Logs the progress of the extraction process.
        - Initializes a `CDTIAidExtractor` instance for the current aid using its details 
            (instrument, support ambit, name, and URL).
        - Runs the aid extraction process for the current aid.
        - Persists the extracted aid data.
        Note:
            - The `CDTIMatrixExtractor` and `CDTIAidExtractor` classes are assumed to handle 
            the specifics of matrix and aid extraction, respectively.
            - The persistence methods save the extracted data for later use.
        Raises:
            Any exceptions raised during the matrix or aid extraction process are not handled 
            within this method and will propagate to the caller.
        """

        # matrix extraction
        cdti_matrix_extractor = (CDTIMatrixExtractor()
            .run_matrix_extraction()
            .persist()
        )

        # aids extraction
        matrix_data = cdti_matrix_extractor.get_aids_df()
        n_aids = matrix_data.shape[0]
        for i in range(n_aids):
            print(f"-- extracting aid {i}/{n_aids}")
            aid_matrix_data = matrix_data.iloc[i]
            print(aid_matrix_data)

            cdti_aid_extractor = CDTIAidExtractor(
                instrument=aid_matrix_data['instrument'],
                support_ambit=aid_matrix_data['support_ambit'],
                name=aid_matrix_data['name'],
                url=aid_matrix_data['url']
            )

            aid_data = cdti_aid_extractor.run_aid_extraction()
            cdti_aid_extractor.persist_data(aid_data)