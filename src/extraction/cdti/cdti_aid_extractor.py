import os
import subprocess

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.extraction.core.base_extractor import BaseExtractor

from src.extraction.params.extraction_params import (
    CDTI_MAIN_DIR,
    CDTI_AID_MAIN_DIR, 
    IMPLICITY_WAIT_TIME
)



class CDTIAidExtractor(BaseExtractor):
    """
    CDTIAidExtractor is a specialized extractor class designed to scrape and process aid-related data 
    from the CDTI (Centro para el Desarrollo Tecnológico y la Innovación) website. It extends the 
    BaseExtractor class and provides methods to extract descriptions, aid cards, document URLs, 
    and subpage information.
    Attributes:
        instrument (str): The instrument associated with the aid.
        support_ambit (str): The support ambit or scope of the aid.
        name (str): The name of the aid.
        url (str): The URL of the aid's main page.
        persist_data_dir (str): The directory where extracted data will be persisted.
        implicity_wait_time (int): The implicit wait time for the web driver.
    Methods:
        parse_string(string):
            Converts a string to lowercase and replaces spaces with underscores.
        extract_description(url=None):
            Extracts the title and description of the aid from the given URL.
        extract_aid_card(url=None):
            Extracts detailed information about the aid in the form of a card from the given URL.
        extract_aid_doc_url(url=None):
            Extracts the URL of the aid's associated document from the given URL.
        extract_aid_subpage(url=None):
            Extracts information about a subpage related to the aid, including its name and URL.
        run_aid_extraction(formated=True):
            Executes the full extraction process for the aid, including descriptions, cards, 
            document URLs, and subpage data. Returns the extracted data.
        format_data(aid_data):
            Formats the extracted aid data into a structured dictionary.
        persist_data(aid_data):
            Saves the extracted aid data to the local file system, including descriptions, cards, 
            documents, and metadata.
    """


    def __init__(
        self, 
        instrument,
        support_ambit,
        name,
        url):

        super().__init__()
        self.instrument=instrument
        self.support_ambit=support_ambit
        self.name=name
        self.url=url
        self.persist_data_dir = self.persist_data_dir + "/" + CDTI_MAIN_DIR + "/" + CDTI_AID_MAIN_DIR + "/" + self.parse_string(self.name)
        self.persist_data_dir = self.persist_data_dir.replace(":", "")
        self.implicity_wait_time = IMPLICITY_WAIT_TIME


    def parse_string(self, string):
        """
        Parses a given string by replacing spaces with underscores and converting 
        all characters to lowercase.

        Args:
            string (str): The input string to be parsed.

        Returns:
            str: The parsed string with spaces replaced by underscores and all 
            characters in lowercase.
        """
        return string.replace(" ", "_").lower()

    
    def extract_description(self, url = None):
        """
        Extracts the title and description from a given URL using a web driver.
        This method navigates to the specified URL (or the instance's default URL if none is provided),
        locates the title and description elements on the page, and returns their text content. If the
        description element is not found, it returns `None` for both title and description.
        Args:
            url (str, optional): The URL to extract the description from. Defaults to `self.url`.
        Returns:
            tuple:
                - aid_title_text (str): The text content of the title element, if found.
                - aid_description_md (str): The markdown-formatted text content of the description element,
                including the title as a header, if found. Returns `None, None` if the description element
                is not found.
        """

        url = url if url else self.url
        
        # driver = self.setup_driver()
        self.driver.get(url)
        # driver.implicitly_wait(self.implicity_wait_time)

        try:
            aid_title = self.driver.find_element(By.CLASS_NAME, "block-field-blocknodeayudastitle")
        except NoSuchElementException: 
            aid_title = None
        try:
            aid_description = self.driver.find_element(By.CLASS_NAME, "block-field-blocknodeayudasbody")
        except NoSuchElementException:
            aid_description = None

        if aid_description:
            aid_title_text = aid_title.text
            aid_description_text = aid_description.text  
            aid_description_md = "\n".join([chunk.strip() for chunk in aid_description_text.split("\n")])
            aid_description_md = "# " + aid_title.text + "\n" + aid_description_text

            # driver.quit()

            return aid_title_text, aid_description_md

        else:
            # driver.quit()
            return None, None


    def extract_aid_card(self, url=None):
        """
        Extracts the aid card information from a given URL or the default URL.
        This method uses a Selenium WebDriver to navigate to the specified URL and 
        extract information from an HTML element with the class name "card-body". 
        The extracted information is formatted in Markdown.
        Args:
            url (str, optional): The URL to extract the aid card from. If not provided, 
            the default URL (`self.url`) is used.
        Returns:
            str: A Markdown-formatted string containing the extracted aid card information 
            if the "card-body" element is found.
            None: If the "card-body" element is not found.
        """

        url = url if url else self.url

        # driver = self.setup_driver()
        self.driver.get(url)
        # driver.implicitly_wait(self.implicity_wait_time)
        try:
            aid_card_element = self.driver.find_element(By.CLASS_NAME, "card-body")
        except NoSuchElementException:
            aid_card_element = None

        if aid_card_element:
        
            aid_card_md = ""
            card_fields = aid_card_element.find_elements(By.CLASS_NAME, "ficha-field-wrapper")

            for card_field in card_fields:
                field_title = card_field.find_element(By.CLASS_NAME, "title").text.strip()
                field_text = card_field.find_element(By.CLASS_NAME, "text").text.strip()
                aid_card_md += f"# {field_title}\n{field_text}\n\n"

            # driver.quit()

            return aid_card_md

        else:
            # driver.quit()
            return None
        

    def extract_aid_doc_url(self, url=None):
        """
        Extracts the URL of an aid document from a given webpage.
        This method navigates to the specified URL (or a default URL if none is provided),
        searches for an HTML element containing the aid document link, and retrieves the
        hyperlink reference (href) of the document.
        Args:
            url (str, optional): The URL of the webpage to extract the aid document link from.
            If not provided, the method will use the instance's `self.url`.
        Returns:
            str or None: The URL of the aid document if found, otherwise `None`.
        Raises:
            NoSuchElementException: If the required elements are not found on the webpage.
        """

        url = url if url else self.url

        # driver = self.setup_driver()
        self.driver.get(url)
        # driver.implicitly_wait(self.implicity_wait_time)

        try:
            aid_card_element = self.driver.find_element(By.CLASS_NAME, "card-body-normativa")
        except NoSuchElementException:
            aid_card_element = None
            
        if aid_card_element:
            a_aid = aid_card_element.find_element(By.TAG_NAME, "a")
            aid_url = a_aid.get_attribute("href")

            # driver.quit()
            return aid_url
        else:
            # driver.quit()
            return None


    def extract_aid_subpage(self, url=None):
        """
        Extracts the name and URL of a subpage from the specified or default URL.
        This method navigates to the given URL (or the default URL if none is provided),
        searches for a specific HTML element containing subpage information, and extracts
        the name and URL of the subpage if available.
        Args:
            url (str, optional): The URL to navigate to. If not provided, the default `self.url` is used.
        Returns:
            tuple: A tuple containing:
                - subpage_name (str or None): The name of the subpage if found, otherwise None.
                - subpage_url (str or None): The URL of the subpage if found, otherwise None.
        Raises:
            NoSuchElementException: If the required elements are not found on the page.
        """

        url = url if url else self.url

        # driver = self.setup_driver()
        self.driver.get(url)
        # driver.implicitly_wait(self.implicity_wait_time)

        try:
            aid_card_element = self.driver.find_element(By.CLASS_NAME, "view-display-id-block_1")
        except NoSuchElementException:
            aid_card_element = None

        if aid_card_element:
            try:
                a_element = aid_card_element.find_elements(By.TAG_NAME, "a")
            except NoSuchElementException:
                a_element = None

            subpage_name = a_element[0].text
            subpage_url = a_element[0].get_attribute("href")

            # driver.quit()

            return subpage_name, subpage_url

        else:
            # driver.quit()
            return None, None


    def run_aid_extraction(self, formated=True):
        """
        Executes the aid extraction process and returns the extracted data.
        This method performs the following steps:
        1. Sets up the web driver.
        2. Extracts the description title and body of the aid.
        3. Extracts the aid card information.
        4. Extracts the document URL associated with the aid.
        5. If no document URL is found, attempts to extract information from a subpage:
            - Extracts the subpage name and URL.
            - Extracts the description title and body from the subpage.
            - Extracts the aid card information from the subpage.
            - Extracts the document URL from the subpage.
        Args:
            formated (bool): If True, formats the extracted data before returning it. Defaults to True.
        Returns:
            dict: A dictionary containing the extracted data, including:
                - 'description_title': The title of the aid description (if found).
                - 'description_body': The body of the aid description (if found).
                - 'aid_card': The aid card information (if found).
                - 'aid_doc_url': The document URL of the aid (if found).
                - 'subpage': A dictionary containing subpage-specific data (if a subpage is found), including:
                    - 'subpage_name': The name of the subpage.
                    - 'subpage_url': The URL of the subpage.
                    - 'description_title_subpage': The title of the subpage description (if found).
                    - 'description_body_subpage': The body of the subpage description (if found).
                    - 'aid_card_subpage': The aid card information from the subpage (if found).
                    - 'aid_doc_subpage_url': The document URL from the subpage (if found).
        Raises:
            Any exceptions raised during the extraction process are not explicitly handled here.
        Note:
            This method assumes the presence of helper methods such as `setup_driver`, 
            `extract_description`, `extract_aid_card`, `extract_aid_doc_url`, 
            `extract_aid_subpage`, and `format_data` within the class.
        """

        extraction_data = {}

        self.driver = self.setup_driver()

        print(f"extracting aid: {self.name} - {self.instrument}, {self.support_ambit}")
        description_title, description_body = self.extract_description()

        if description_title:
            print("extracted title:", description_title)
            extraction_data['description_title'] = description_title
        else:
            print("No description title found")
        
        if description_body:
            print("extracted description:", len(description_body))
            extraction_data['description_body'] =  description_body
        else:
            print("No description body found")

        # extract card
        aid_card = self.extract_aid_card()

        if aid_card:
            print("extracted card:", len(aid_card))
            extraction_data['aid_card'] = aid_card
        else:
            print("No card found")

        # extract doc url
        aid_doc_url = self.extract_aid_doc_url()

        if aid_doc_url:
            print("extracted aid_doc: ", aid_doc_url)
            extraction_data['aid_doc_url'] = aid_doc_url
        else:
            print("No doc url found")
            print("Extracting subpage")

            # extract subpage
            subpage_name, subpage_url = self.extract_aid_subpage()

            if subpage_name:
                print(f"found subpage: {subpage_name}, {subpage_url}")
                extraction_data['subpage'] = {
                    "subpage_name": subpage_name,
                    "subpage_url": subpage_url
                }

                print("extracting subpage")
                description_title_subpage, description_body_subpage = self.extract_description(url=subpage_url)

                if description_title_subpage:
                    print("extracted subpage title:", description_title_subpage)
                    extraction_data['subpage']['description_title_subpage'] = description_title_subpage
                else:
                    print("No title subpage found")

                if description_body_subpage:
                    print("extracted subpage description:", len(description_body_subpage))
                    extraction_data['subpage']['description_body_subpage'] = description_body_subpage
                else:
                    print("No description subpage found")

                # extract card
                aid_card_subpage = self.extract_aid_card(url=subpage_url)

                if aid_card_subpage:
                    print("extracted card:", len(aid_card_subpage))
                    extraction_data['subpage']['aid_card_subpage'] = aid_card_subpage
                else:
                    print("No card subpage found")

                # extract doc url
                aid_doc_subpage_url = self.extract_aid_doc_url(url=subpage_url)
                
                if aid_doc_subpage_url:
                    print("extracted aid_doc: ", aid_doc_subpage_url)
                    extraction_data['subpage']['aid_doc_subpage_url'] = aid_doc_subpage_url
                else:
                    print("No doc subpage url found")
            
            else:
                print("no subpage found")

        self.driver.quit()

        if formated:
            extraction_data = self.format_data(extraction_data)

        return extraction_data


    def format_data(self, aid_data):
        """
        Formats aid data by extracting and organizing relevant information from the input dictionary.
        Args:
            aid_data (dict): A dictionary containing aid-related data. It may include the following keys:
                - 'description_title' (str): The title of the aid description.
                - 'description_body' (str): The body of the aid description.
                - 'aid_card' (str): Information about the aid card.
                - 'aid_doc_url' (str): URL to the aid document.
                - 'subpage' (dict): A nested dictionary that may include:
                    - 'description_title_subpage' (str): The title of the aid description from the subpage.
                    - 'description_body_subpage' (str): The body of the aid description from the subpage.
                    - 'aid_card_subpage' (str): Information about the aid card from the subpage.
                    - 'aid_doc_subpage_url' (str): URL to the aid document from the subpage.
        Returns:
            dict: A formatted dictionary containing the following keys:
                - 'aid_url' (str): The URL of the aid (from the instance's `self.url` attribute).
                - 'description_title' (str): The formatted title of the aid description.
                - 'description_body' (str): The formatted body of the aid description.
                - 'aid_card' (str): The formatted aid card information.
                - 'aid_doc_url' (str): The formatted URL to the aid document.
        Notes:
            - If a key is missing in the main dictionary but exists in the 'subpage' dictionary, the value from the 'subpage' is used.
            - If both main and subpage values exist for 'description_body', they are concatenated with a double newline.
            - If a key is missing in both the main and subpage dictionaries, an empty string is assigned.
        """

        aid_data_formated = {}
        aid_data_formated["aid_url"] = self.url

        check_description_title = 'description_title' in aid_data.keys()
        check_description_body = 'description_body' in aid_data.keys()
        check_aid_card = 'aid_card' in aid_data.keys()
        check_aid_doc_url = 'aid_doc_url' in aid_data.keys()
        check_subpage = 'subpage' in aid_data.keys()
        check_description_title_subpage = ('description_title_subpage' in aid_data['subpage'].keys()) if check_subpage else False
        check_description_body_subpage = ('description_body_subpage' in aid_data['subpage'].keys()) if check_subpage else False
        check_aid_card_subpage = ('aid_card_subpage' in aid_data['subpage'].keys()) if check_subpage else False
        check_aid_doc_subpage_url = ('aid_doc_subpage_url' in aid_data['subpage'].keys()) if check_subpage else False

        # title
        if check_description_title:
            aid_data_formated['description_title'] = aid_data['description_title']
        elif not check_description_title and check_description_title_subpage:
            aid_data_formated['description_title'] = aid_data['subpage']['description_title_subpage']
        else:
            aid_data_formated['description_title'] = ''

        #  body
        if check_description_body and not check_description_body_subpage:
            aid_data_formated['description_body'] = aid_data['description_body']
        elif not check_description_body and check_description_body_subpage:
            aid_data_formated['description_body'] = aid_data['subpage']['description_body_subpage']
        elif check_description_body and check_description_body_subpage:
            aid_data_formated['description_body'] = aid_data['description_body'] + "\n\n" + aid_data['subpage']['description_body_subpage']
        else:
            aid_data_formated['description_body'] = ''

        # aid_card
        if check_aid_card:
            aid_data_formated['aid_card'] = aid_data['aid_card']
        elif not check_aid_card and check_aid_card_subpage:
            aid_data_formated['aid_card'] = aid_data['subpage']['aid_card_subpage']
        else:
            aid_data_formated['aid_card'] = ''

        # aid_doc_url
        if check_aid_doc_url:
            aid_data_formated['aid_doc_url'] = aid_data['aid_doc_url']
        elif not check_aid_doc_url and check_aid_doc_subpage_url:
            aid_data_formated['aid_doc_url'] = aid_data['subpage']['aid_doc_subpage_url']
        else:
            aid_data_formated['aid_doc_url'] = ''

        return aid_data_formated


    def persist_data(self, aid_data):
        """
        Persist aid data into files and directories.
        This method saves various components of the aid data (description, card, document, and metadata)
        into the specified directory. It creates the directory if it does not exist.
        Args:
            aid_data (dict): A dictionary containing the following keys:
                - 'description_body' (str): The body of the description to be saved.
                - 'description_title' (str): The title of the description, used for naming files.
                - 'aid_card' (str): The content of the aid card to be saved.
                - 'aid_doc_url' (str): The URL of the aid document to be downloaded and saved.
                - 'aid_url' (str): The URL of the aid, included in the metadata.
        Behavior:
            - Saves the description body to a markdown file if it is not empty.
            - Saves the aid card content to a markdown file if it is not empty.
            - Downloads the aid document from the provided URL and saves it locally.
            - Saves metadata (aid URL and document URL) to a markdown file.
        Notes:
            - The method uses PowerShell's `Start-BitsTransfer` command to download the document.
            - File and directory names are sanitized using the `parse_string` method.
        """
        if not os.path.exists(self.persist_data_dir):
            os.makedirs(self.persist_data_dir)

        # save description
        if aid_data['description_body'] != '':
            description_dir = self.persist_data_dir + "/" + self.parse_string(aid_data['description_title'] + "_description.md")
            # description_dir
            with open(description_dir, "w", encoding="utf-8") as file:
                file.write(aid_data['description_body'])

        # save card
        if aid_data['aid_card'] != '':
            card_dir = self.persist_data_dir + "/" + self.parse_string(aid_data['description_title'] + "_card.md")
            # card_dir
            with open(card_dir, "w", encoding="utf-8") as file:
                file.write(aid_data['aid_card'])

        # save doc
        if aid_data['aid_doc_url'] != '':
            doc_name = aid_data['aid_doc_url'].split('/')[-1]
            doc_dir = self.persist_data_dir + "/" + doc_name
            doc_dir = doc_dir.replace("/", "\\")

            # Invoke-WebRequest -uri "{aid_data['aid_doc_url']}" -OutFile "{doc_dir}"
            powershell_script = f'''
            Start-BitsTransfer -Source "{aid_data['aid_doc_url']}" -Destination "{doc_dir}"
            '''
            subprocess.run(["powershell", "-Command", powershell_script])


        #TODO save metadata (urls)
        metadata_dir = self.persist_data_dir + "/" + self.parse_string(aid_data['description_title'] + "_metadata.md")
        metadata_string = f"""# aid url\n{aid_data["aid_url"]}\n\n# doc url\n{aid_data["aid_doc_url"]}
        """
        with open(metadata_dir, "w", encoding="utf-8") as file:
            file.write(metadata_string)

