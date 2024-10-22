import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

BASE_URL = "https://app.gmx.io/"
LEADERBOARD_ROUTE = '#/leaderboard'


def basePageURLAccumulator(tableElement, outputList) -> list:
  """Uses selenium to accumulate URL's of accounts of interests."""
  


def mainScraper() -> list:
  """Uses selenium to accumulate URL's of accounts of interests."""
  
  scanUrl = BASE_URL + LEADERBOARD_ROUTE
  driver = webdriver.Firefox()

  driver.get(scanUrl)
  time.sleep(8)
  tableElement = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[1]/div[5]/div/div[2]/div[2]/table/tbody')
  
  tableHTML = tableElement.get_attribute('innerHTML')

  print(tableHTML, '\n\n\n', 'NEXT\n\n')

  links = tableElement.find_elements(By.TAG_NAME, 'a')
  print(links, '\n\n')

  for link in links:
    href = link.get_attribute('href')
    print(href)


  driver.quit()

mainScraper()

def pageScraper():
  pass

def traderScraper():
  pass