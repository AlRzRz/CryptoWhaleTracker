from core.scraper import accountURLScraper, accountPageScraper
from core.sentimentAnalysis import mainAnalysis
import tkinter as tk


def main():
  # testURLNoOrder = 'https://app.gmx.io/#/accounts/0x96D140670A5d40f4242dE9ddA6ff3EDeDfA74B33?network=arbitrum&v=2'
  # testURLwPos = 'https://app.gmx.io/#/accounts/0x88bf5A2E82510847E5dcBF33F44A9F611F1C1dF5?network=arbitrum&v=2'
  # testURLwOrders = 'https://app.gmx.io/#/accounts/0xcFa0AB31d240e4E831c6219F62E73a38C6AAB058?network=arbitrum&v=2'
  # traderURLS = [testURLwPos, testURLNoOrder, testURLwOrders]

  traderURLS = accountURLScraper()
  lstOfTraders = accountPageScraper(traderURLS)

  # root = tk.Tk()
  mainAnalysis(lstOfTraders)
  # root.mainloop()


if __name__ == "__main__":
  main()