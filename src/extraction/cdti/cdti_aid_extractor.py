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
        return string.replace(" ", "_").lower()

    
    def extract_description(self, url = None):

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

