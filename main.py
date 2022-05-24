#imports
from distutils.log import error
from fileinput import filename
from operator import truediv
from re import I
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import date
from config import *
import os

#Global variables
WINDOW_SIZE = 800
TIME = 30 #seconds
#ARG = f"--window-size={WINDOW_SIZE},{WINDOW_SIZE}"
ARG = "--headless"
#DOWNLOAD_DIR = "./Downloads"
FILENAME = f"report_{date.today()}.csv"

def repeat(driver, host, loop=1):
    shadowRoot = driver.execute_script(DATE_SCRIPT, host)
    while 1:
        try: bool = shadowRoot.find_element(By.CSS_SELECTOR, DATE_CSS_SELECTOR).is_enabled()
        except:
            print(f"Error: {error}")
        if bool:
            return
        else:
            driver.refresh()
            repeat(driver, host, loop+1)

def main():
    #setup webdriver
    options = Options()

    prefs = {"download.default_directory" : DOWNLOAD_DIR}
    options.add_experimental_option("prefs",prefs)
    options.add_argument(ARG)
    driver = webdriver.Chrome(options=options)

    
    #login
    print(f"Logging into {LOGIN_URL}")
    driver.get(LOGIN_URL)
    driver.implicitly_wait(TIME)
    driver.find_element(By.ID, USERNAME[0]).send_keys(USERNAME[1])
    driver.find_element(By.ID, PASSWORD[0]).send_keys(PASSWORD[1])
    driver.find_element(By.ID, SIGN_IN_BUTTON).click()
    print(f"Logged into {USERNAME[1]} on {LOGIN_URL} successfully.")

    #navigate and download
    print(f"Navigating to {DESTINATION_URL}...")
    driver.get(BASE_URL)
    driver.get(DESTINATION_URL)
    #wait for page to load
    wait = WebDriverWait(driver, TIME)
    wait.until(lambda driver: driver.current_url == DESTINATION_URL)
    #load shadow dom and select term
    driver.implicitly_wait(TIME)
    host = driver.find_element(By.XPATH, DATE_XPATH)
    shadowRoot = driver.execute_script(DATE_SCRIPT, host)
    
    repeat(driver, host)
    shadowRoot.find_element(By.CSS_SELECTOR, DATE_CSS_SELECTOR).click()
    print("Downloading report...")
    driver.implicitly_wait(TIME)
    driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div/div[2]/a").click()
    os.rename("./Downloads/report.csv", f"./Downloads/{FILENAME}")
    print(f'Report saved as "{FILENAME}" in "{DOWNLOAD_DIR}".')

def check_date(directory):
    for file in os.listdir(directory):
        if file == FILENAME:
            print(f"Report available at {directory}/{FILENAME}")
            exit()
    return False

def loop():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    #while not os.listdir(DOWNLOAD_DIR):
    while not check_date(DOWNLOAD_DIR): 
        try:
            main()
        except:
            print(f"Error: {error}")
            print("Trying again...")
            loop()

if __name__ == '__main__':
    loop()
