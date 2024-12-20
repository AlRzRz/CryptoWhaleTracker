from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from .routes import routes, accountRoutes
from .classes import Position, Order, Trader
from .parser import positionDataParser, orderDataParser
import random


WAIT = 12
MINIWAIT = 7


def random_sleep(min_seconds, max_seconds):
  time.sleep(random.uniform(min_seconds, max_seconds))



def accountURLAccumulator(tableElement, outputSet) -> None:
  """Uses selenium to accumulate URL's of accounts of interests."""

  aTags = tableElement.find_elements(By.TAG_NAME, 'a')

  for aTag in aTags:
    href = aTag.get_attribute('href')
    outputSet.add(href)


def accumulateTable(driver, outputSet, interval: int) -> None:
  time.sleep(interval)
  
  tableElement = driver.find_element(By.XPATH, routes['TABLE_X'])
  print(' Successfully Accumulated Table! '.center(50, '_'), '\n')
  accountURLAccumulator(tableElement=tableElement, outputSet=outputSet)


def traverseDriver(driver, route):
  random_sleep(1, 3)
  traverser = driver.find_element(By.XPATH, routes[route])
  traverser.click()


def accountURLScraper() -> list:
  """Uses selenium to accumulate URL's of accounts of interests."""
  setOfAccountURLS = set()

  scanUrl = routes['BASE_URL'] + routes['LEADERBOARD_ROUTE']
  driver = webdriver.Firefox()

  driver.get(scanUrl)
  accumulateTable(driver, setOfAccountURLS, WAIT)

  traverseDriver(driver, 'PAGE2_X')
  accumulateTable(driver, setOfAccountURLS, MINIWAIT)

  traverseDriver(driver, 'LAST30BUTTON_X')
  accumulateTable(driver, setOfAccountURLS, WAIT)

  traverseDriver(driver, 'PAGE1_X')
  accumulateTable(driver, setOfAccountURLS, MINIWAIT)

  traverseDriver(driver, 'LAST7BUTTON_X')
  accumulateTable(driver, setOfAccountURLS, WAIT)

  traverseDriver(driver, 'PAGE2_X')
  accumulateTable(driver, setOfAccountURLS, MINIWAIT)

  traverseDriver(driver, 'TOP_POS_X')
  accumulateTable(driver, setOfAccountURLS, WAIT)

  traverseDriver(driver, 'PAGE2_X')
  accumulateTable(driver, setOfAccountURLS, MINIWAIT)

  print('Links accumulated:\n')
  for i in setOfAccountURLS:
    print(i)

  print('\n', f'Total amount of links: {len(setOfAccountURLS)}\n')
  print('EXPECTED: 160')

  driver.quit()

  return setOfAccountURLS


# Functions dedicated to scraping trader data found below


def accountPositionsAccumulator(tableElem) -> list[Position]:
  positionsLst = []
  
  #Each row represents a position
  rowElems = tableElem.find_elements(By.TAG_NAME, 'tr')

  for rowElem in rowElems:
    position = positionDataParser(rowElem=rowElem)
    positionsLst.append(position)

  return positionsLst


def accountOrdersAccumulator(driver) -> list[Order]:
  ordersLst = []



  tableElem = driver.find_element(By.XPATH, accountRoutes['ORD_TABLE'])
  rowElems = tableElem.find_elements(By.TAG_NAME, 'tr')

  for rowElem in rowElems:
    order = orderDataParser(rowElem=rowElem)
    ordersLst.append(order)

  return ordersLst


def positionsAndOrdersCheck(elemTuple: tuple) -> tuple:
  posElem, ordElem = elemTuple
  posBool = True
  ordBool = True

  if posElem.get_attribute('innerHTML') == 'Positions':
    posBool = False
  if ordElem.get_attribute('innerHTML') == 'Orders':
    ordBool = False

  return (posBool, ordBool)


def accountPageScraper(accountURLS: set) -> list[Trader]:

  tradersData = []
  traderIDTracker = 0

  driver = webdriver.Firefox()
  orderButtonTracker = False

  for i, URL in enumerate(accountURLS):
    print(f'Accumulating Info: Trader # {traderIDTracker}\n')
    positions = []
    orders = []

    driver.get(URL)
    driver.maximize_window()
    random_sleep(5, 8)

    positionsElem = driver.find_element(By.XPATH, accountRoutes['POSITIONS_TAB'])
    ordersElem = driver.find_element(By.XPATH, accountRoutes['ORDERS_TAB'])

    elemTuple = (positionsElem, ordersElem)
    posTrue, ordTrue = positionsAndOrdersCheck(elemTuple=elemTuple)

    if posTrue:
      if orderButtonTracker:
        positionsElem.click()
        orderButtonTracker = False
      time.sleep(3)
      tableElem = driver.find_element(By.XPATH, accountRoutes['POS_TABLE'])
      positions = accountPositionsAccumulator(tableElem=tableElem)

    if ordTrue:
      if orderButtonTracker == False:
        ordersElem.click()
        time.sleep(5)
      orders = accountOrdersAccumulator(driver=driver)
      orderButtonTracker = True

    newTrader = Trader(traderIDTracker, URL)
    newTrader.addPositionLst(positions)
    newTrader.addOrderLst(orders)

    tradersData.append(newTrader)
    traderIDTracker += 1


    if (i + 1) % 50 == 0:
      print('\nTaking a short break to avoid rate limiting!\n')
      random_sleep(15, 30)


  driver.quit()
  return tradersData




#Tests done below
# testURLNoOrder = 'https://app.gmx.io/#/accounts/0x96D140670A5d40f4242dE9ddA6ff3EDeDfA74B33?network=arbitrum&v=2'
# testURLwPos = 'https://app.gmx.io/#/accounts/0x88bf5A2E82510847E5dcBF33F44A9F611F1C1dF5?network=arbitrum&v=2'
# testURLwOrders = 'https://app.gmx.io/#/accounts/0xcFa0AB31d240e4E831c6219F62E73a38C6AAB058?network=arbitrum&v=2'

# accountURLS = [testURLwPos, testURLNoOrder, testURLwOrders]

# traderData = accountPageScraper(accountURLS=accountURLS)

# for trader in traderData:
#   print(trader)

#   for position in trader.positions:
#     print(position)
#   print('\n')
#   for order in trader.orders:
#     print(order)
#   print('\n')