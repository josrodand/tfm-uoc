from extractor.cdti.cdti_matrix_extractor import CDTIMatrixExtractor

if __name__ == "__main__":
    cdti_extractor = CDTIMatrixExtractor()
    cdti_extractor.run_matrix_extraction()

    aids = cdti_extractor.get_aids_json()
    print(aids)
