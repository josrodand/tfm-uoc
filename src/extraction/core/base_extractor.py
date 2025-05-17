from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from src.extraction.params.extraction_params import CHROMEDRIVE_ROUTE, PERSIST_DATA_DIR


class BaseExtractor:
    """
    BaseExtractor is a base class designed to handle the setup and configuration of a Selenium WebDriver 
    for web scraping or automation tasks. It provides methods and attributes to manage the driver setup 
    and configuration.
    Attributes:
        chromedrive_route (str): Path to the ChromeDriver executable.
        persist_data_dir (str): Directory path for persisting data.
    Methods:
        setup_driver():
            Configures and initializes a Selenium WebDriver instance with predefined options, such as 
            headless mode and security settings. Returns the configured WebDriver instance.
    """

    def __init__(self):

        self.chromedrive_route = CHROMEDRIVE_ROUTE
        self.persist_data_dir = PERSIST_DATA_DIR
        # self.driver = self.setup_driver()
        # TODO: cambiarlo para que sea un metodo que levanta el driver y se use en la pipeline
        # general. Estando aqui provoca que al crear la clase se levante el driver (el bot)
        # en la pipeline pegar un setup_driver y al final driver.quit()
    
    def setup_driver(self):

        service = Service(self.chromedrive_route)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        # chrome_options.add_argument("--window-position=-2400,-2400")  # start minimized
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-usb")
        chrome_options.add_argument('--log-level=3')
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver