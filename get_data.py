from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from twocaptcha import TwoCaptcha
import requests
import time
import ast
from PIL import Image
from io import BytesIO
from seleniumbase import Driver

class selenium_API_scrapper():
    def setup_method(self):
        # chrome_options = Options()
        # chrome_options.add_experimental_option("detach", True)
        # # chrome_options.add_argument('--headless')  # Run Chrome in headless mode
        # chrome_options.add_argument('--no-sandbox')
        # # chrome_options.add_argument('--disable-dev-shm-usage')
        # self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver = uc.Chrome()
        self.driver = Driver(uc=True, headless=True)
        self.vars = {}
        self.response =''
    
    def captcha_Response(self,processed_image):
        captcha_parameters = {'numeric': 4,
                                    'minLength': 6,
                                    'maxLength': 6,
                                    'phrase': 0,
                                    'caseSensitive': 1,
                                    'calc': 0,
                                    'lang': 'en'}

        # export APIKEY_2CAPTCHA=1abc234de56fab7c89012d34e56fa7b8 on Linux or macOS
        # set APIKEY_2CAPTCHA=1abc234de56fab7c89012d34e56fa7b8 on Windows
        # in this example we store the API key inside environment variables that can be set like:
        # export APIKEY_2CAPTCHA=1abc234de56fab7c89012d34e56fa7b8 on Linux or macOS
        # set APIKEY_2CAPTCHA=1abc234de56fab7c89012d34e56fa7b8 on Windows
        # you can just set the API key directly to it's value like:
        # api_key="1abc234de56fab7c89012d34e56fa7b8"
        api_key = os.getenv('1abc234de56fab7c89012d34e56fa7b8', '9ab4de74da11f917e1943b105f0d6935')

        solver = TwoCaptcha(api_key)

        try:
            result = solver.normal(processed_image,**captcha_parameters)

        except Exception as e:
            print(e)
            result = "False"
        result =str(result)
        print(result)
        return result
    
    
    def preprocess_and_save_image(self):
        
        
        captcha_img_element = self.driver.find_element(By.CSS_SELECTOR, '.captcha-img img')

        # Get the position and size of the element
        location = captcha_img_element.location
        size = captcha_img_element.size

        # Take a screenshot of the entire page
        screenshot = self.driver.get_screenshot_as_png()

        # Crop the screenshot to the area of the captcha image
        captcha_image = Image.open(BytesIO(screenshot))
        captcha_area = (
            int(location['x']),
            int(location['y']),
            int(location['x'] + size['width']),
            int(location['y'] + size['height'])
        )
        captcha_image = captcha_image.crop(captcha_area)

        # Save the cropped image to a file
        captcha_image.save("captcha_screenshot.png")

        value = self.captcha_Response("captcha_screenshot.png")
        result_dict = ast.literal_eval(value)
        code = result_dict.get("code", "False")
        
        print(code)
        return code  
    
    
    def extract_info(self):
        try:
            wait = WebDriverWait(self.driver, 5)

            # Use XPath or other locators to extract data
            # image_link = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="card-body"]/img'))).get_attribute("src")
            cnic_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//td'))).text
            person_name =wait.until(EC.visibility_of_element_located((By.XPATH, '//td[2]'))).text
            father_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//td[3]'))).text
            city_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//tr[2]/td'))).text
            license_number = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr/td').text
            issue_date = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr/td[2]').text
            valid_from = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr/td[3]').text
            valid_to = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr[2]/td[3]').text
            allowed_vehicles = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr[2]/td[2]').text
            status = self.driver.find_element(By.XPATH, '//table[2]/tbody/tr[2]/td').text
       
        except Exception as e:
            print(e)
               
        return {
                "cnic_name": cnic_name,
                "person_name": person_name,
                "father_name": father_name,
                "city_name": city_name,
                "license_number": license_number,
                "issue_date": issue_date,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "allowed_vehicles": allowed_vehicles,
                "status": status
            }
    
    def launchWebsite(self):
        while True:
            url='https://dlims.punjab.gov.pk/verify'
            self.driver.get(url)
            self.driver.maximize_window()
            

            self.driver.find_element(By.XPATH,'//*[@id="cnicInput"]').send_keys('3440293014149')
            self.driver.find_element(By.XPATH,'//*[@id="licenseNumber"]').send_keys('MN-23-3297')
            time.sleep(5)
        
            # captcha_img_url = self.driver.find_element(By.CSS_SELECTOR, '.captcha-img img').get_attribute('src')
            # print(captcha_img_url)
            captcha_text  = self.preprocess_and_save_image()
            
            if captcha_text != "False":
                try:
                    self.driver.implicitly_wait(30)
                    self.driver.find_element(By.XPATH,'//*[@id="captcha"]').send_keys(captcha_text)
                    self.driver.implicitly_wait(10)
                    self.driver.find_element(By.XPATH,'//*[@id="submit-btn"]').click()
                    self.driver.implicitly_wait(5)
                    output = self.extract_info()
                    print(output)
                    self.driver.quit()
                    return False
                except Exception as e:
                    print(e)
                    print("first unsuccessful")    
            else:
                print("second unsuccessful")          
            

obj = selenium_API_scrapper()
obj.setup_method()
obj.launchWebsite()