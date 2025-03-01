# 🚀 Crypto Whale Tracker

## 📌 Overview
Crypto Whale Tracker is a **Python-based** tool that scrapes a decentralized exchange's leaderboard, performs calculations on the collected data, and presents insights into the trading activities of top traders (**"whales"**).

---

## ✨ Features
✅ **Leaderboard Scraping**: Uses Selenium to extract trader positions and orders from a decentralized exchange.  
✅ **Data Parsing & Cleaning**: Extracts relevant trading details, including assets, leverage, PnL, collateral, and liquidation prices.  
✅ **Analysis & Insights**:
- 📈 Identifies top profitable and losing traders.
- 🔍 Analyzes long vs. short positions and leverage distributions.
- 🚨 Monitors pending orders and liquidation risks.
- 📊 Detects order hotspots where multiple traders cluster around key price levels.
✅ **CLI Interface**: Provides a terminal-based output using **Rich** tables for enhanced readability.  
✅ **Live Price Fetching**: Integrates with **CoinGecko API** to fetch real-time asset prices.  
✅ **Automated Report Generation**: Saves **HTML reports** of market insights and compares them with previous reports.  

---

## 🛠 Installation
### 🔹 Prerequisites
Ensure you have the following installed:
- Python **3.8+**
- `pip` (Python package manager)
- Firefox & **Geckodriver** (for Selenium)

### 🔹 Install Dependencies
Run the following command:
```bash
pip install selenium rich requests numpy pandas
```

---

## 🚀 Usage
### ▶ Running the Scraper
```bash
python main.py
```
### 📌 CLI Commands
- The script **automatically scrapes** the leaderboard, extracts trader data, and runs an analysis.
- Outputs are displayed in the terminal using **Rich** tables.
- Generates an **HTML report** saved in the `data/` directory.

### 📂 Output Files
- 🆕 **`data/new.html`**: Latest analysis report.
- 📊 **`data/prev.html`**: Previous analysis report for comparison.
- 📜 **`data/old.html`**: Archived report.

---

## 🔍 Components
### 📁 Modules
- **`scraper.py`** 🕵️‍♂️: Handles Selenium-based leaderboard scraping.
- **`parser.py`** 🔎: Cleans and extracts trading data from scraped HTML elements.
- **`sentimentAnalysis.py`** 📊: Performs market analysis and generates insights.

---

## 📊 Example Output
### 📌 Live Prices
```
BTC: $67100.00
ETH: $2478.69
SOL: $172.65
```
### 📌 Long vs Short Positions
```
Type   Count   Size       Ratio
Long   28      16,673,173  0.22
Short  130     51,133,791  0.33
```
### 📌 Liquidation Risk
```
Trader ID | Asset | Leverage | Liq Price | Current Price | Difference %
2         | BTC   | 17.49x   | $67966.17 | $67100.00     | 1.29%
```

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 🤝 Contributing
Contributions are welcome! 🎉
- Open an **issue** if you find a bug or have a feature request.
- Submit a **pull request** to contribute improvements.

---

🚀 **Happy Tracking!** 📊🐳
