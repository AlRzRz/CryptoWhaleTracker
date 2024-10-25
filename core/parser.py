from .classes import Position, Order
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By



def cleanAssetText(text, outputDict):
    pattern = r'(\w+)\s*(\d+\.\d+)x\s*(\w+)'
    match = re.match(pattern, text)

    if match:
        asset = match.group(1)
        leverage = float(match.group(2))
        short = match.group(3)
    else:
        # Set default values if the regex does not match
        asset = "Unknown"  # or you can set another default value
        leverage = 1.0  # default leverage if missing
        short = "Long"  # default to 'Long' if not specified

    if short == 'Short':
        short = True
    else:
        short = False

    outputDict['asset'] = asset
    outputDict['leverage'] = leverage
    outputDict['short'] = short




def cleanPnlText(text, outputDict):
  pattern = r'[-\+]?\$([\d,]+\.\d+)\s*[-\+]\$([\d,]+\.\d+)\s*\(([-\+]?\d+\.\d+)%\)'
  match = re.search(pattern, text)

  if match:
    pnl = float(match.group(2).replace(',', ''))
    if text.find('-$' + match.group(2)) != -1: 
      pnl *= -1
    percentage = float(match.group(3))
    if text.find('-' + match.group(3)) != -1:
      percentage *= -1

  outputDict['pnl'] = pnl
  outputDict['pnlPerc'] = percentage



def cleanCollatText(text, outputDict):
  pattern = r'\$([\d,]+\.\d+)'
  match = re.search(pattern, text)

  if match:
    collat = float(match.group(1).replace(',', ''))

  outputDict['collateral'] = collat



def cleanEntryText(text, outputDict):
  pattern = r'\$([\d,]+\.\d+)'
  match = re.search(pattern, text)

  if match:
    entry = float(match.group(1).replace(',', ''))

  outputDict['entry'] = entry



def cleanLiqText(text, outputDict):
  liq = None
  
  pattern = r'\$([\d,]+\.\d+)'
  match = re.search(pattern, text)

  if match:
    liq = float(match.group(1).replace(',', ''))

  outputDict['liq'] = liq



def cleanPositionBlock(rawCargo) -> dict:
  assetText, pnlText, collatText, entryText, liqText = rawCargo
  outputDict = {}
  
  cleanAssetText(assetText, outputDict)
  cleanPnlText(pnlText, outputDict)
  cleanCollatText(collatText, outputDict)
  cleanEntryText(entryText, outputDict)
  cleanLiqText(liqText, outputDict)

  return outputDict


def positionDataParser(rowElem) -> Position:
  dataElems = rowElem.find_elements(By.TAG_NAME, 'td')

  if len(dataElems) < 7:  # 7 expected elements based on your code
    raise ValueError(f"Expected at least 7 elements in dataElems, but got {len(dataElems)}. Check the page structure.")


  assetText = dataElems[0].get_attribute('innerText')
  pnlText = dataElems[2].get_attribute('innerText')
  collatText = dataElems[3].get_attribute('innerText')
  entryText = dataElems[4].get_attribute('innerText')
  liqText = dataElems[6].get_attribute('innerText')

  rawCargo = [assetText, pnlText, collatText, entryText, liqText]
  cleanCargo = cleanPositionBlock(rawCargo=rawCargo)

  return Position(cleanCargo['asset'], cleanCargo['leverage'],
                  cleanCargo['short'], cleanCargo['pnl'], cleanCargo['pnlPerc'],
                  cleanCargo['collateral'], cleanCargo['liq'], cleanCargo['entry'])





# Order data parser and helpers found below

def cleanAssetTextO(text) -> list:
  pattern = r"(Long|Short)([A-Z]+)(?=/USD)"
  match = re.match(pattern, text)

  if match:
    direction = match.group(1)
    ticker = match.group(2)

  if direction == 'Short':
    direction = True
  else:
    direction = False

  return [ticker, direction]


def cleanTypeTextO(text):
  return text


def cleanSizeTextO(text):
  pattern = r"[-+]?\$([\d,]+\.\d+)"
  match = re.search(pattern, text)

  if match:
    number = float(match.group(1).replace(',', ''))

    if text.startswith('-'):
      number *= -1

  return number


def cleanTriggerTextO(text):
  pattern = r"[<>]\s*\$([\d,]+\.\d+)"
  match = re.search(pattern, text)

  if match:
    number = float(match.group(1).replace(',', ''))

  return number



def orderDataParser(rowElem) -> Order:
  dataElems = rowElem.find_elements(By.TAG_NAME, 'td')

  assetText = dataElems[0].get_attribute('innerText')
  typeText = dataElems[1].get_attribute('innerText')
  sizeText = dataElems[2].get_attribute('innerText')
  triggerText = dataElems[3].get_attribute('innerText')

  assetO, shortO = cleanAssetTextO(assetText)
  orderType = cleanTypeTextO(typeText)
  size = cleanSizeTextO(sizeText)
  trigger = cleanTriggerTextO(triggerText)

  return Order(assetO, shortO, orderType, size, trigger)