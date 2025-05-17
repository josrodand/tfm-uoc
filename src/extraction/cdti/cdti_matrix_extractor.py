import os

import pandas as pd

from selenium.webdriver.common.by import By

from src.extraction.core.base_extractor import BaseExtractor
from src.extraction.params.extraction_params import (
    URL_CDTI, 
    CDTI_MAIN_DIR, 
    CDTI_MATRIX_DATA_DIR, 
    CDTI_MATRIX_FILENAME,
    IMPLICITY_WAIT_TIME
)


class CDTIMatrixExtractor(BaseExtractor):
    """
    A class to extract matrix data from the CDTI website.
    This class is responsible for navigating to the CDTI website, extracting
    matrix data (row titles, column titles, and associated aids), and persisting
    the extracted data in a structured format.
    Attributes:
        url_cdti (str): The URL of the CDTI website.
        persist_data_dir (str): The directory where the extracted data will be saved.
        file_name (str): The name of the file where the extracted data will be saved.
        implicity_wait_time (int): The implicit wait time for the web driver.
        aid_list (list): A list of dictionaries containing the extracted aid data.
    Methods:
        get_row_titles(section):
            Extracts row titles from the specified section of the webpage.
        get_column_titles(section):
            Extracts column titles from the specified section of the webpage.
        run_matrix_extraction():
            Executes the matrix extraction process, including navigating to the
            website, extracting data, and storing it in memory.
        persist():
            Saves the extracted data to a CSV file in the specified directory.
        get_aids_json():
            Returns the extracted aid data as a JSON-compatible list.
        get_aids_df():
            Returns the extracted aid data as a pandas DataFrame.
    """


    def __init__(self):
        super().__init__()
        self.url_cdti = URL_CDTI
        self.persist_data_dir = self.persist_data_dir + "/" + CDTI_MAIN_DIR + "/" + CDTI_MATRIX_DATA_DIR
        self.file_name = CDTI_MATRIX_FILENAME

        self.implicity_wait_time = IMPLICITY_WAIT_TIME

    
    def get_row_titles(self, section):
        """
        Extracts the text content of elements with the class name "row-title" 
        within a given section.
        Args:
            section (WebElement): The web element representing the section 
            containing the row titles.
        Returns:
            list: A list of strings, where each string is the text content of 
            a "row-title" element found in the section.
        """

        row_titles = [row.text for row in section.find_elements(By.CLASS_NAME, "row-title")]
        return row_titles


    def get_column_titles(self, section):
        """
        Extracts and returns the column titles from a given section.

        Args:
            section: A web element representing the section from which to extract column titles.
            It is expected to contain elements with the class name "column-title".

        Returns:
            list: A list of strings representing the non-empty text of column titles found in the section.
        """
        column_titles = [column.text for column in section.find_elements(By.CLASS_NAME, "column-title") if column.text != ""]
        return column_titles


    def run_matrix_extraction(self):
        """
        Executes the extraction process for the CDTI matrix.
        This method automates the process of extracting data from a specific section
        of a webpage using Selenium. It retrieves information about aids, including
        their instrument, support ambit, name, and URL, and stores the results in
        the `aid_list` attribute.
        Steps performed:
        1. Initializes a Selenium WebDriver and navigates to the specified URL.
        2. Locates the matrix block section on the webpage.
        3. Extracts row titles and column titles from the matrix.
        4. Iterates through the rows and columns of the matrix to extract aid data.
        5. Cleans the extracted data by removing unwanted entries (e.g., "Ver video").
        6. Stores the cleaned data in the `aid_list` attribute.
        Returns:
            self: The instance of the class with the extracted data stored in the
            `aid_list` attribute.
        Attributes:
            aid_list (list): A list of dictionaries containing the extracted aid data.
            Each dictionary has the following keys:
            - "instrument": The row title (instrument name).
            - "support_ambit": The column title (support ambit).
            - "name": The name of the aid.
            - "url": The URL associated with the aid.
        Prints:
            - A message indicating the start and completion of the extraction process.
            - The total number of aids found after cleaning.
        Note:
            - The method assumes the webpage structure remains consistent with the
            expected class names and tags.
            - The WebDriver is closed after the extraction process is complete.
        """

        print("Running CDTI Matrix Extraction")

        driver = self.setup_driver()
        driver.get(self.url_cdti)
        driver.implicitly_wait(self.implicity_wait_time)
        # find matrix block
        section = driver.find_element(By.CLASS_NAME, "block-matriz-ayudas-block")
        
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
        driver.quit()

        # clean aid list
        aid_list = [aid for aid in aid_list if aid['name'] != "Ver video"]

        self.aid_list = aid_list
        print("CDTI Matrix Extraction Finished. found {} aids".format(len(aid_list)))

        return self


    def persist(self):
        """
        Persists the extracted data to a CSV file.
        This method ensures that the directory specified by `persist_data_dir` exists,
        creating it if necessary. Then, it saves the DataFrame returned by `get_aids_df()`
        as a CSV file in the specified directory with the name provided by `file_name`.
        Returns:
            self: The instance of the class, allowing method chaining.
        """
        if not os.path.exists(self.persist_data_dir):
            os.makedirs(self.persist_data_dir)
        
        self.get_aids_df().to_csv(self.persist_data_dir + "/" + self.file_name, index=False)

        return self

    
    def get_aids_json(self):
        """
        Retrieves the list of aids in JSON format.

        Returns:
            list: A list containing aid information.
        """
        return self.aid_list

    
    def get_aids_df(self):
        """
        Converts the list of aids into a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the aid_list attribute.
        """
        return pd.DataFrame(self.aid_list)
    


if __name__ == "__main__":
    cdti_extractor = (CDTIMatrixExtractor()
        .run_matrix_extraction()
        .persist()
    )

    aids = cdti_extractor.get_aids_json()
    print(aids)










