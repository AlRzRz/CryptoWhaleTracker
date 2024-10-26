from core.scraper import accountURLScraper, accountPageScraper
from core.sentimentAnalysis import mainAnalysis
import tkinter as tk
import time
import os


def testData() -> list:
  traderURLS = [
                'https://app.gmx.io/#/accounts/0x591b6F096281DD7b645767C96aC34863A4Df9a89?network=arbitrum&v=2',
                'https://app.gmx.io/#/accounts/0x4Cd80aa0CE4881Eb8679EdA1f6fbe3d89AEc0F7F?network=arbitrum&v=2',
                'https://app.gmx.io/#/accounts/0xfE191897EE42D56c6b0C85C7B489C1b1cb28c1E0?network=arbitrum&v=2']

  return traderURLS



def main():

  startTime = time.time()

  data_dir = os.path.join(os.path.dirname(__file__), 'data')
  if not os.path.exists(data_dir):
    os.makedirs(data_dir)
  
  traderURLS = testData()
  # traderURLS = accountURLScraper()
  lstOfTraders = accountPageScraper(traderURLS)

  # root = tk.Tk()
  mainAnalysis(lstOfTraders)
  # root.mainloop()
  endTime = time.time()
  timeTakenMinutes = int(endTime - startTime) / 60
  
  print('Time taken:')
  print('Minutes:', timeTakenMinutes)


if __name__ == "__main__":
  main()