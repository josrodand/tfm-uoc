from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from extractor.params.extraction_params import CHROMEDRIVE_ROUTE, PERSIST_DATA_DIR


class BaseExtractor:

    def __init__(self):

        self.chromedrive_route = CHROMEDRIVE_ROUTE
        self.persist_data_dir = PERSIST_DATA_DIR
        self.driver = self.setup_driver()

    
    def setup_driver(self):

        service = Service(self.chromedrive_route)
        driver = webdriver.Chrome(service=service)

        return driver