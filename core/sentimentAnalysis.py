# CLI INTERFACE VARIATION FOUND BELOW

import requests
from rich.console import Console
from rich.table import Table
from collections import defaultdict
import numpy as np
import math
import time
from rich.markdown import Markdown
import os
import datetime
import re
import webbrowser

# Initialize Rich console
console = Console(record=True)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../data')


# Caching for live prices
price_cache = {}


def manage_output_files():
    """Rotates output files and manages naming based on run history."""
    new_file = os.path.join(OUTPUT_DIR, 'new.html')
    prev_file = os.path.join(OUTPUT_DIR, 'prev.html')
    old_file = os.path.join(OUTPUT_DIR, 'old.html')

    # Delete old.html if it exists
    if os.path.exists(old_file):
        os.remove(old_file)

    # Move prev.html to old.html if it exists
    if os.path.exists(prev_file):
        os.rename(prev_file, old_file)

    # Move new.html to prev.html if it exists
    if os.path.exists(new_file):
        os.rename(new_file, prev_file)

def save_html_output():
    """Saves the current console output to new.html with timestamp information."""
    # Ensure the data directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    console.print(f"\n[b]Analysis Run Date:[/b] {date_str}\n")

    # Manage file rotation before saving the new file
    manage_output_files()

    # Save new.html file in the data directory
    new_output_path = os.path.join(OUTPUT_DIR, 'new.html')
    console.save_html(new_output_path)


def strip_html_tags(text):
    """Removes HTML tags from the given text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)



def compare_output_files():
    """Compares prev.html and new.html, opens both files in the browser without printing differences to the console."""
    new_file = os.path.join(OUTPUT_DIR, 'new.html')
    prev_file = os.path.join(OUTPUT_DIR, 'prev.html')

    # Open HTML files in the browser if they exist
    if os.path.exists(new_file):
        webbrowser.open(f'file://{os.path.abspath(new_file)}')
    if os.path.exists(prev_file):
        webbrowser.open(f'file://{os.path.abspath(prev_file)}')

    # Display message if prev.html does not exist
    if not os.path.exists(prev_file):
        console.print("[yellow]No previous output file found to compare with.[/yellow]")
        return

    # Remove the console print of differences
    with open(prev_file, 'r', encoding='utf-8') as file:
        prev_content = strip_html_tags(file.read()).splitlines()
    with open(new_file, 'r', encoding='utf-8') as file:
        new_content = strip_html_tags(file.read()).splitlines()

    # Find differences without printing them
    differences = [line for line in new_content if line not in prev_content]

    # Optionally, you can log differences to a file or simply omit this step



def convert_asset_ticker(asset):
    """Converts asset ticker from 'BTC/USD' to 'bitcoin' for CoinGecko."""
    asset_mapping = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "LINK": "chainlink",
        "DOGE": "dogecoin", "ARB": "arbitrum", "GMX": "gmx", "WIF": "wrapped-fantom",
        "AAVE": "aave", "PEPE": "pepe", "UNI": "uniswap", "XRP": "ripple",
        "NEAR": "near", "AVAX": "avalanche-2", "LTC": "litecoin", "BNB": "binancecoin",
        "OP": "optimism", "ATOM": "cosmos", "EIGEN": "eigen", "SHIB": "shiba-inu",
        "SUI": "sui", "SEI": "sei", "POL": "polymath", "ORDI": "ordi",
        "SATS": "sats", "STX": "stacks", "APE": "apecoin"
    }
    ticker = asset.split("/")[0]
    return asset_mapping.get(ticker, ticker.lower()), ticker  # Return both formats


def fetch_live_prices(assets, delay=3):
    global price_cache
    asset_mapping = {ticker: convert_asset_ticker(ticker)[0] for ticker in assets}
    coingecko_ids = ','.join(set(asset_mapping.values()))

    cached_prices = {ticker: price_cache[ticker] for ticker in asset_mapping if ticker in price_cache}
    remaining_assets = {ticker: asset_mapping[ticker] for ticker in asset_mapping if ticker not in price_cache}

    if not remaining_assets:
        return cached_prices

    time.sleep(delay)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(set(remaining_assets.values()))}&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for original_ticker, coingecko_ticker in remaining_assets.items():
            price = data.get(coingecko_ticker, {}).get("usd")
            if price is not None:
                price_cache[original_ticker] = price
                cached_prices[original_ticker] = price
    return cached_prices


def calculate_liquidation_risk(tradersLst, threshold_percent=5):
    risk_positions = []
    assets_in_use = set(pos.asset for trader in tradersLst for pos in trader.positions)
    prices = fetch_live_prices(assets_in_use)

    for trader in tradersLst:
        for pos in trader.positions:
            live_price = prices.get(pos.asset)
            if pos.liq is not None and live_price is not None:
                liquidation_diff = abs((pos.liq - live_price) / live_price) * 100
                if liquidation_diff <= threshold_percent:
                    risk_positions.append({
                        "trader_id": trader.traderID,
                        "trader_url": trader.url,
                        "asset": pos.asset,
                        "leverage": pos.leverage,
                        "size": pos.size,
                        "pnl": pos.pnl,
                        "collateral": pos.collateral,
                        "liq_price": pos.liq,
                        "current_price": live_price,
                        "difference_percent": liquidation_diff
                    })

    return risk_positions


# Print function for liquidation risk using Rich
def print_liquidation_risk(risk_positions):
    if not risk_positions:
        console.print("[yellow]No positions are close to liquidation.[/yellow]")
        return

    table = Table(title="Liquidation Risk")
    table.add_column("Trader ID", justify="right", style="cyan")
    table.add_column("Asset", justify="right", style="magenta")
    table.add_column("Leverage", justify="right", style="green")
    table.add_column("Position Size", justify="right", style="yellow")
    table.add_column("PnL", justify="right", style="red")
    table.add_column("Collateral", justify="right", style="cyan")
    table.add_column("Liq Price", justify="right", style="blue")
    table.add_column("Current Price", justify="right", style="green")
    table.add_column("Difference %", justify="right", style="magenta")
    table.add_column("URL", justify="right", style="blue")

    for pos in risk_positions:
        # Use Rich's hyperlink syntax with smaller text styling
        url_link = f"[link={pos['trader_url']}] [small]{pos['trader_url']}[/small] [/link]"
        table.add_row(
            str(pos["trader_id"]),
            pos["asset"],
            f"{pos['leverage']}x",
            f"${pos['size']:.2f}",
            f"${pos['pnl']:.2f}",
            f"${pos['collateral']:.2f}",
            f"${pos['liq_price']:.2f}",
            f"${pos['current_price']:.2f}",
            f"{pos['difference_percent']:.2f}%",
            url_link
        )
    console.print(table)


# Example of integration in the main analysis
def mainAnalysis(tradersLst):
    # Fetch and print live prices for assets in positions
    assets_in_use = set(pos.asset for trader in tradersLst for pos in trader.positions)
    console.print("[bold cyan]Live Prices for Tracked Assets[/bold cyan]")
    
    # Fetch prices for all assets at once
    prices = fetch_live_prices(assets_in_use)

    for asset, price in prices.items():
        console.print(f"{asset}: ${price:.2f}")

    # Market Data Section
    console.print("\n[bold cyan]Market Data[/bold cyan]")
    long_vs_short, long_vs_short_size = calculate_long_short_ratios(tradersLst)
    leverage_dist = calculate_leverage_distribution(tradersLst)
    pnl_stats = calculate_pnl_stats(tradersLst)
    collateral_dist = calculate_collateral_distribution(tradersLst)
    
    # Print Market Data
    print_long_short_data(long_vs_short, long_vs_short_size)
    print_leverage_distribution(leverage_dist)
    print_pnl_distribution(pnl_stats)
    print_collateral_distribution(collateral_dist)
    
    # Trader Data Section
    console.print("\n[bold cyan]Trader Data[/bold cyan]")
    top_10_profitable_traders = get_top_traders(tradersLst, top=True)
    top_10_losing_traders = get_top_traders(tradersLst, top=False)
    largest_position_holders = get_largest_position_holders(tradersLst)
    top_leveraged_traders = get_top_leveraged_traders(tradersLst)
    
    # Print Trader Data
    print_top_traders(top_10_profitable_traders, "Most Profitable Traders")
    print_top_traders(top_10_losing_traders, "Most Losing Traders")
    print_largest_position_holders(largest_position_holders)
    print_top_leveraged_traders(top_leveraged_traders)
    
    # Asset Data Section
    console.print("\n[bold cyan]Asset Data[/bold cyan]")
    asset_data = calculate_asset_stats(tradersLst)
    pending_orders = calculate_pending_orders(tradersLst)
    
    # Print Asset Data
    print_asset_data(asset_data)
    print_pending_orders(pending_orders)

    # Order Hotspot Analysis
    console.print("\n[bold cyan]Order Hotspot Analysis[/bold cyan]")
    hotspots = calculate_order_hotspots(tradersLst)
    print_order_hotspots(hotspots)

    # Liquidation Risk Analysis
    console.print("\n[bold cyan]Liquidation Risk Analysis[/bold cyan]")
    risk_positions = calculate_liquidation_risk(tradersLst, threshold_percent=5)
    print_liquidation_risk(risk_positions)

    save_html_output()
    compare_output_files()

# Helper functions

def calculate_long_short_ratios(tradersLst):
    long_count, short_count = 0, 0
    long_size, short_size = 0, 0

    for trader in tradersLst:
        for pos in trader.positions:
            if pos.short:
                short_count += 1
                short_size += pos.size
            else:
                long_count += 1
                long_size += pos.size

    long_short_ratio = long_count / short_count if short_count != 0 else np.inf
    long_short_size_ratio = long_size / short_size if short_size != 0 else np.inf
    return (long_count, short_count, long_short_ratio), (long_size, short_size, long_short_size_ratio)

def calculate_leverage_distribution(tradersLst):
    # Filter out positions with leverage above 50
    leverage_values = [pos.leverage for trader in tradersLst for pos in trader.positions if pos.leverage <= 50]
    if not leverage_values:
        return None
    return {
        'average_leverage': np.mean(leverage_values),
        'max_leverage': np.max(leverage_values)
    }

def calculate_pnl_stats(tradersLst):
    # Only keep Average PnL and Median PnL
    pnls = [pos.pnl for trader in tradersLst for pos in trader.positions]
    if not pnls:
        return None
    return {
        'average_pnl': np.mean(pnls),
        'median_pnl': np.median(pnls),
    }

def calculate_collateral_distribution(tradersLst):
    collateral_values = [pos.collateral for trader in tradersLst for pos in trader.positions]
    if not collateral_values:
        return None
    return {
        'total_collateral': np.sum(collateral_values),
        'average_collateral': np.mean(collateral_values)
    }

def get_top_traders(tradersLst, top=True, n=10):
    all_traders = [(trader, sum([pos.pnl for pos in trader.positions])) for trader in tradersLst]
    all_traders.sort(key=lambda x: x[1], reverse=top)
    return all_traders[:n]

def get_largest_position_holders(tradersLst, n=10):
    traders_positions = [(trader, max([pos.size for pos in trader.positions], default=0)) for trader in tradersLst]
    traders_positions.sort(key=lambda x: x[1], reverse=True)
    return traders_positions[:n]

def get_top_leveraged_traders(tradersLst, n=10):
    # Exclude traders with positions having leverage above 50
    traders_leverage = [
        (trader, max([pos.leverage for pos in trader.positions if pos.leverage <= 50], default=0))
        for trader in tradersLst
    ]
    traders_leverage = [item for item in traders_leverage if item[1] <= 50]
    traders_leverage.sort(key=lambda x: x[1], reverse=True)
    return traders_leverage[:n]

def calculate_asset_stats(tradersLst):
    asset_stats = defaultdict(lambda: {'longs': 0, 'shorts': 0, 'positions': 0, 'leverage': [], 'pnl': []})
    
    for trader in tradersLst:
        for pos in trader.positions:
            if pos.asset == "Unknown":  # Skip assets marked as "Unknown"
                continue
            asset_data = asset_stats[pos.asset]
            asset_data['positions'] += 1
            asset_data['leverage'].append(pos.leverage)
            asset_data['pnl'].append(pos.pnl)
            if pos.short:
                asset_data['shorts'] += 1
            else:
                asset_data['longs'] += 1

    # Compute average leverage and pnl for each asset
    for asset, data in asset_stats.items():
        data['average_leverage'] = np.mean(data['leverage']) if data['leverage'] else None
        data['average_pnl'] = np.mean(data['pnl']) if data['pnl'] else None

    return asset_stats

def calculate_pending_orders(tradersLst):
    pending_orders = defaultdict(lambda: {'longs': 0, 'shorts': 0, 'orders': []})
    
    for trader in tradersLst:
        for order in trader.orders:
            asset_data = pending_orders[order.asset]
            asset_data['orders'].append(order)
            if order.short:
                asset_data['shorts'] += 1
            else:
                asset_data['longs'] += 1

    return pending_orders


def calculate_order_hotspots(tradersLst, price_range_percent=3, min_traders=3):
    """
    Identifies hotspot zones where traders have placed orders within a specified price range.
    Parameters:
    - tradersLst: List of Trader objects
    - price_range_percent: The range within which prices are considered a cluster
    - min_traders: Minimum number of traders for a cluster to be considered a hotspot
    
    Returns:
    A dictionary with asset as keys and clusters of prices with associated order statistics.
    """
    # Dictionary to track hotspots by asset
    hotspots = defaultdict(lambda: defaultdict(lambda: {'Long': [], 'Short': []}))

    # Process each trader's orders
    for trader in tradersLst:
        for order in trader.orders:
            # Determine the price range for clustering
            trigger_price = order.trigger
            lower_bound = trigger_price * (1 - price_range_percent / 100)
            upper_bound = trigger_price * (1 + price_range_percent / 100)

            # Add order to relevant hotspot cluster
            direction = "Short" if order.short else "Long"
            clusters = hotspots[order.asset]
            found_cluster = False

            for cluster_price, data in clusters.items():
                if lower_bound <= cluster_price <= upper_bound:
                    data[direction].append({'trader_id': trader.traderID, 'price': trigger_price, 'type': order.orderType})
                    found_cluster = True
                    break

            if not found_cluster:
                # Create a new cluster if none matched
                clusters[trigger_price][direction].append({'trader_id': trader.traderID, 'price': trigger_price, 'type': order.orderType})

    # Filter clusters to identify hotspots
    final_hotspots = {}
    for asset, clusters in hotspots.items():
        for cluster_price, data in clusters.items():
            long_traders = len({order['trader_id'] for order in data['Long']})
            short_traders = len({order['trader_id'] for order in data['Short']})
            if long_traders >= min_traders or short_traders >= min_traders:
                if asset not in final_hotspots:
                    final_hotspots[asset] = []
                final_hotspots[asset].append({
                    'cluster_price': cluster_price,
                    'Long': data['Long'],
                    'Short': data['Short']
                })
    return final_hotspots


# Output formatting functions using Rich
def print_long_short_data(long_short, long_short_size):
    table = Table(title="Long vs Short")
    table.add_column("Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Ratio", justify="right", style="yellow")

    long_count, short_count, long_short_ratio = long_short
    long_size, short_size, long_short_size_ratio = long_short_size

    table.add_row("Long", str(long_count), str(long_size), f"{long_short_ratio:.2f}")
    table.add_row("Short", str(short_count), str(short_size), f"{long_short_size_ratio:.2f}")
    console.print(table)

def print_leverage_distribution(leverage_dist):
    if not leverage_dist:
        console.print("[yellow]No leverage data available[/yellow]")
        return
    table = Table(title="Leverage Distribution")
    table.add_column("Average Leverage", justify="right", style="cyan")
    table.add_column("Max Leverage", justify="right", style="green")
    table.add_row(f"{leverage_dist['average_leverage']:.2f}", f"{leverage_dist['max_leverage']:.2f}")
    console.print(table)

def print_pnl_distribution(pnl_stats):
    if not pnl_stats:
        console.print("[yellow]No PnL data available[/yellow]")
        return
    table = Table(title="PnL Distribution")
    table.add_column("Average PnL", justify="right", style="cyan")
    table.add_column("Median PnL", justify="right", style="magenta")
    table.add_row(f"{pnl_stats['average_pnl']:.2f}", f"{pnl_stats['median_pnl']:.2f}")
    console.print(table)

def print_collateral_distribution(collateral_dist):
    if not collateral_dist:
        console.print("[yellow]No collateral data available[/yellow]")
        return
    table = Table(title="Collateral Distribution")
    table.add_column("Total Collateral", justify="right", style="cyan")
    table.add_column("Average Collateral", justify="right", style="green")
    table.add_row(f"{collateral_dist['total_collateral']:.2f}", f"{collateral_dist['average_collateral']:.2f}")
    console.print(table)

def print_top_traders(traders, title):
    table = Table(title=title)
    table.add_column("Trader ID", justify="right", style="cyan")
    table.add_column("PnL", justify="right", style="magenta")
    table.add_column("URL", justify="right", style="blue")

    for trader, pnl in traders:
        url_link = f"[{trader.url}]({trader.url})"  # Markdown formatted link
        table.add_row(str(trader.traderID), f"{pnl:.2f}", url_link)

    console.print(table)

def print_largest_position_holders(traders):
    table = Table(title="Largest Position Holders")
    table.add_column("Trader ID", justify="right", style="cyan")
    table.add_column("Position Size", justify="right", style="green")
    table.add_column("URL", justify="right", style="blue")

    for trader, size in traders:
        url_link = f"[{trader.url}]({trader.url})"  # Markdown formatted link
        table.add_row(str(trader.traderID), f"{size:.2f}", url_link)

    console.print(table)

def print_top_leveraged_traders(traders):
    table = Table(title="Top 10 Leveraged Traders (<= 50x)")
    table.add_column("Trader ID", justify="right", style="cyan")
    table.add_column("Leverage", justify="right", style="green")
    table.add_column("URL", justify="right", style="blue")

    for trader, leverage in traders:
        url_link = f"[{trader.url}]({trader.url})"
        table.add_row(str(trader.traderID), f"{leverage:.2f}", url_link)

    console.print(table)

def print_asset_data(asset_data):
    table = Table(title="Asset Data (Excluding 'Unknown')")
    table.add_column("Asset", justify="right", style="cyan")
    table.add_column("Longs", justify="right", style="magenta")
    table.add_column("Shorts", justify="right", style="green")
    table.add_column("Average Leverage", justify="right", style="yellow")
    table.add_column("Average PnL", justify="right", style="blue")

    sorted_data = sorted(asset_data.items(), key=lambda x: x[1]['average_pnl'], reverse=True)
    for asset, data in sorted_data:
        table.add_row(asset, str(data['longs']), str(data['shorts']), 
                      f"{data['average_leverage']:.2f}", f"{data['average_pnl']:.2f}")
    console.print(table)


def print_pending_orders(pending_orders):
    table = Table(title="Pending Orders")
    table.add_column("Asset", justify="right", style="cyan")
    table.add_column("Long Orders", justify="right", style="magenta")
    table.add_column("Short Orders", justify="right", style="green")
    table.add_column("Total Orders", justify="right", style="yellow")

    sorted_orders = sorted(pending_orders.items(), key=lambda x: len(x[1]['orders']), reverse=True)
    for asset, data in sorted_orders:
        table.add_row(asset, str(data['longs']), str(data['shorts']), str(len(data['orders'])))
    console.print(table)


def print_order_hotspots(hotspots):
    """
    Prints out hotspots with details on traders and orders within each cluster.
    """
    if not hotspots:
        console.print("[yellow]No order hotspots identified.[/yellow]")
        return

    for asset, clusters in hotspots.items():
        table = Table(title=f"{asset} Order Hotspots")
        table.add_column("Cluster Price", justify="right", style="cyan")
        table.add_column("Direction", justify="right", style="magenta")
        table.add_column("Trader ID", justify="right", style="green")
        table.add_column("Order Type", justify="right", style="yellow")
        table.add_column("Price", justify="right", style="blue")

        for cluster in clusters:
            for direction, orders in cluster.items():
                if direction not in ["Long", "Short"]:
                    continue
                for order in orders:
                    table.add_row(
                        f"{cluster['cluster_price']:.2f}",
                        direction,
                        str(order['trader_id']),
                        order['type'],
                        f"{order['price']:.2f}"
                    )
        console.print(table)



# GUI INTERFACE VARIATION FOUND BELOW WIP

# import requests
# import tkinter as tk
# from tkinter import ttk
# from collections import defaultdict
# import numpy as np
# import time

# # Caching for live prices
# price_cache = {}

# def convert_asset_ticker(asset):
#     asset_mapping = {
#         "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "LINK": "chainlink",
#         "DOGE": "dogecoin", "ARB": "arbitrum", "GMX": "gmx", "WIF": "wrapped-fantom",
#         "AAVE": "aave", "PEPE": "pepe", "UNI": "uniswap", "XRP": "ripple",
#         "NEAR": "near", "AVAX": "avalanche-2", "LTC": "litecoin", "BNB": "binancecoin",
#         "OP": "optimism", "ATOM": "cosmos", "EIGEN": "eigen", "SHIB": "shiba-inu",
#         "SUI": "sui", "SEI": "sei", "POL": "polymath", "ORDI": "ordi",
#         "SATS": "sats", "STX": "stacks", "APE": "apecoin"
#     }
#     ticker = asset.split("/")[0]
#     return asset_mapping.get(ticker, ticker.lower()), ticker  # Return both formats

# def fetch_live_prices(assets, delay=3):
#     global price_cache
#     asset_mapping = {ticker: convert_asset_ticker(ticker)[0] for ticker in assets}
#     coingecko_ids = ','.join(set(asset_mapping.values()))

#     cached_prices = {ticker: price_cache[ticker] for ticker in asset_mapping if ticker in price_cache}
#     remaining_assets = {ticker: asset_mapping[ticker] for ticker in asset_mapping if ticker not in price_cache}

#     if not remaining_assets:
#         return cached_prices

#     time.sleep(delay)
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(set(remaining_assets.values()))}&vs_currencies=usd"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         for original_ticker, coingecko_ticker in remaining_assets.items():
#             price = data.get(coingecko_ticker, {}).get("usd")
#             if price is not None:
#                 price_cache[original_ticker] = price
#                 cached_prices[original_ticker] = price
#     return cached_prices

# def calculate_liquidation_risk(tradersLst, threshold_percent=5):
#     risk_positions = []
#     assets_in_use = set(pos.asset for trader in tradersLst for pos in trader.positions)
#     prices = fetch_live_prices(assets_in_use)

#     for trader in tradersLst:
#         for pos in trader.positions:
#             live_price = prices.get(pos.asset)
#             if live_price is not None:
#                 liquidation_diff = abs((pos.liq - live_price) / live_price) * 100
#                 if liquidation_diff <= threshold_percent:
#                     risk_positions.append({
#                         "trader_id": trader.traderID,
#                         "trader_url": trader.url,
#                         "asset": pos.asset,
#                         "leverage": pos.leverage,
#                         "size": pos.size,
#                         "pnl": pos.pnl,
#                         "collateral": pos.collateral,
#                         "liq_price": pos.liq,
#                         "current_price": live_price,
#                         "difference_percent": liquidation_diff
#                     })

#     return risk_positions

# def create_sortable_table(parent, columns, data):
#     tree = ttk.Treeview(parent, columns=columns, show="headings")
#     for col in columns:
#         tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
#     for row in data:
#         tree.insert("", "end", values=row)
#     tree.pack(fill=tk.BOTH, expand=True)
#     return tree

# def sort_column(tree, col, reverse):
#     data_list = [(tree.set(child, col), child) for child in tree.get_children("")]
#     data_list.sort(reverse=reverse)
#     for index, (val, item) in enumerate(data_list):
#         tree.move(item, "", index)
#     tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

# # Display Functions for each table
# def display_liquidation_risk(root, risk_positions):
#     columns = ["Trader ID", "Asset", "Leverage", "Position Size", "PnL", "Collateral", "Liq Price", "Current Price", "Difference %", "URL"]
#     data = [(pos['trader_id'], pos['asset'], f"{pos['leverage']}x", f"${pos['size']:.2f}", 
#              f"${pos['pnl']:.2f}", f"${pos['collateral']:.2f}", f"${pos['liq_price']:.2f}",
#              f"${pos['current_price']:.2f}", f"{pos['difference_percent']:.2f}%", pos['trader_url']) 
#             for pos in risk_positions]
#     create_sortable_table(root, columns, data)

# def display_long_short_data(root, long_short_data):
#     columns = ["Type", "Count", "Size", "Ratio"]
#     data = [("Long", *long_short_data['long']), ("Short", *long_short_data['short'])]
#     create_sortable_table(root, columns, data)

# def display_leverage_distribution(root, leverage_dist):
#     columns = ["Average Leverage", "Max Leverage"]
#     data = [(leverage_dist['average_leverage'], leverage_dist['max_leverage'])]
#     create_sortable_table(root, columns, data)

# def display_pnl_distribution(root, pnl_stats):
#     columns = ["Average PnL", "Median PnL", "PnL Variance"]
#     data = [(pnl_stats['average_pnl'], pnl_stats['median_pnl'], pnl_stats['variance_pnl'])]
#     create_sortable_table(root, columns, data)

# def display_collateral_distribution(root, collateral_dist):
#     columns = ["Total Collateral", "Average Collateral"]
#     data = [(collateral_dist['total_collateral'], collateral_dist['average_collateral'])]
#     create_sortable_table(root, columns, data)

# def display_trader_ranking(root, trader_rankings, title):
#     columns = ["Trader ID", "PnL", "URL"]
#     data = [(trader.traderID, pnl, trader.url) for trader, pnl in trader_rankings]
#     create_sortable_table(root, columns, data)

# def display_asset_data(root, asset_data):
#     columns = ["Asset", "Longs", "Shorts", "Average Leverage", "Average PnL"]
#     data = [(asset, data['longs'], data['shorts'], data['average_leverage'], data['average_pnl'])
#             for asset, data in asset_data.items()]
#     create_sortable_table(root, columns, data)


# def get_top_traders(tradersLst, top=True, n=10):
#     all_traders = [(trader, sum([pos.pnl for pos in trader.positions])) for trader in tradersLst]
#     all_traders.sort(key=lambda x: x[1], reverse=top)
#     return all_traders[:n]


# def calculate_collateral_distribution(tradersLst):
#     collateral_values = [pos.collateral for trader in tradersLst for pos in trader.positions]
#     if not collateral_values:
#         return {'total_collateral': 0, 'average_collateral': 0}
#     return {
#         'total_collateral': np.sum(collateral_values),
#         'average_collateral': np.mean(collateral_values)
#     }

# def calculate_pnl_stats(tradersLst):
#     pnls = [pos.pnl for trader in tradersLst for pos in trader.positions]
#     if not pnls:
#         return {'average_pnl': 0, 'median_pnl': 0, 'variance_pnl': 0}
#     return {
#         'average_pnl': np.mean(pnls),
#         'median_pnl': np.median(pnls),
#         'variance_pnl': np.var(pnls)
#     }

# def calculate_long_short_ratios(tradersLst):
#     long_count, short_count = 0, 0
#     long_size, short_size = 0, 0

#     for trader in tradersLst:
#         for pos in trader.positions:
#             if pos.short:
#                 short_count += 1
#                 short_size += pos.size
#             else:
#                 long_count += 1
#                 long_size += pos.size

#     long_short_ratio = long_count / short_count if short_count != 0 else np.inf
#     long_short_size_ratio = long_size / short_size if short_size != 0 else np.inf
#     return {'long': (long_count, long_size, long_short_ratio), 'short': (short_count, short_size, long_short_size_ratio)}


# def calculate_leverage_distribution(tradersLst):
#     leverage_values = [pos.leverage for trader in tradersLst for pos in trader.positions]
#     if not leverage_values:
#         return {'average_leverage': 0, 'max_leverage': 0}
#     return {
#         'average_leverage': np.mean(leverage_values),
#         'max_leverage': np.max(leverage_values)
#     }



# # Main analysis function to calculate and display all tables
# def mainAnalysis(tradersLst, root):
#     root.title("Trader Analysis")
#     root.geometry("1000x700")
    
#     # Calculate metrics based on the actual traders data
#     long_short_data = calculate_long_short_ratios(tradersLst)
#     leverage_dist = calculate_leverage_distribution(tradersLst)
#     pnl_stats = calculate_pnl_stats(tradersLst)
#     collateral_dist = calculate_collateral_distribution(tradersLst)
#     risk_positions = calculate_liquidation_risk(tradersLst)

#     # Top 10 traders (profitable or losing based on PnL)
#     top_traders = get_top_traders(tradersLst, top=True)

#     # Display all the calculated data
#     display_long_short_data(root, long_short_data)
#     display_leverage_distribution(root, leverage_dist)
#     display_pnl_distribution(root, pnl_stats)
#     display_collateral_distribution(root, collateral_dist)
#     display_trader_ranking(root, top_traders, "Most Profitable Traders")
#     display_liquidation_risk(root, risk_positions)

