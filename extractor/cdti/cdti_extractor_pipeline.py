from extractor.cdti.cdti_matrix_extractor import CDTIMatrixExtractor
from extractor.cdti.cdti_aid_extractor import CDTIAidExtractor


class CDTIExtractorPipeline:

    def __init__(self):
        pass

    def run_pipeline(self):

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