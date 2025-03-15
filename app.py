from extractor.cdti.cdti_matrix_extractor import CDTIMatrixExtractor

if __name__ == "__main__":
    cdti_extractor = (CDTIMatrixExtractor()
        .run_matrix_extraction()
        .persist()
    )

    # cdti_extractor = CDTIMatrixExtractor()
    # cdti_extractor.run_matrix_extraction()
    # cdti_extractor.persist()

    # aids = cdti_extractor.get_aids_json()
    # print(aids)
    # print(cdti_extractor.persist_data_dir)
    # print(cdti_extractor.file_name)


