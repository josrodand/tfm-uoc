import os

import pandas as pd

from selenium.webdriver.common.by import By

from extractor.core.base_extractor import BaseExtractor
from extractor.params.extraction_params import (
    URL_CDTI, 
    CDTI_MAIN_DIR, 
    CDTI_MATRIX_DATA_DIR, 
    CDTI_MATRIX_FILENAME
)


class CDTIMatrixExtractor(BaseExtractor):

    def __init__(self):

        super().__init__()
        self.url_cdti = URL_CDTI
        self.persist_data_dir = self.persist_data_dir + "/" + CDTI_MAIN_DIR + "/" + CDTI_MATRIX_DATA_DIR
        self.file_name = CDTI_MATRIX_FILENAME

    
    def get_row_titles(self, section):
        row_titles = [row.text for row in section.find_elements(By.CLASS_NAME, "row-title")]
        return row_titles


    def get_column_titles(self, section):
        column_titles = [column.text for column in section.find_elements(By.CLASS_NAME, "column-title") if column.text != ""]
        return column_titles

    def run_matrix_extraction(self):
        """
        """
        print("Running CDTI Matrix Extraction")
        self.driver.get(self.url_cdti)
        self.driver.implicitly_wait(5)
        # find matrix block
        section = self.driver.find_element(By.CLASS_NAME, "block-matriz-ayudas-block")
        
        # get row titles
        row_titles = self.get_row_titles(section)
        # get_column titles
        column_titles = self.get_column_titles(section)

        aid_list = []

        # get_row_aids
        row_aids = section.find_elements(By.CLASS_NAME, "row-aids")

        # check rows
        for index_row in range(len(row_aids)):
            row_aid = row_aids[index_row]

            # get column aids
            column_aids = row_aid.find_elements(By.CLASS_NAME, "column-aids")

            # check columns
            if len(column_aids) > 0:
                for index_column in range(len(column_aids)):
                    column_aid = column_aids[index_column]

                    # get a elements
                    a_aids = column_aid.find_elements(By.TAG_NAME, "a")

                    # name and url
                    if len(a_aids) > 0:
                        for a_aid in a_aids:
                            aid_name = a_aid.text
                            aid_href = a_aid.get_attribute("href")

                            aid_data = {
                                "instrument": row_titles[index_row], 
                                "support_ambit": column_titles[index_column], 
                                "name": aid_name, 
                                "url": aid_href
                            }
        
                            aid_list.append(aid_data)
        self.driver.quit()

        # clean aid list
        aid_list = [aid for aid in aid_list if aid['name'] != "Ver video"]

        self.aid_list = aid_list
        print("CDTI Matrix Extraction Finished. found {} aids".format(len(aid_list)))

        return self


    def persist(self):
        if not os.path.exists(self.persist_data_dir):
            os.makedirs(self.persist_data_dir)
        
        self.get_aids_df().to_csv(self.persist_data_dir + "/" + self.file_name, index=False)

        return self

    
    def get_aids_json(self):
        return self.aid_list

    
    def get_aids_df(self):
        return pd.DataFrame(self.aid_list)
    


if __name__ == "__main__":
    cdti_extractor = (CDTIMatrixExtractor()
        .run_matrix_extraction()
        .persist()
    )

    aids = cdti_extractor.get_aids_json()
    print(aids)










