import requests
import json
from datetime import datetime
import pandas as pd  # Import pandas for DataFrame

def get_token_data():
    # Trump coin address on Solana
    token_address = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"
    
    # DexScreener API endpoint
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        
        # Print the full API response
        print(json.dumps(data, indent=4))  # Added line to print full results
        
        # Create a list to hold the extracted data
        dex_data = []
        
        # Iterate through each pair in the data
        for pair in data['pairs']:
            # Extract relevant information for the DataFrame
            dex_info = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'chainID': pair['chainId'],
                'dexID': pair['dexId'],
                'baseToken.symbol': pair['baseToken']['symbol'],
                'pairToken.symbol': pair['quoteToken']['symbol'],
                'priceNative': pair['priceNative'],
                'priceUSD': pair['priceUsd'],
                'txns.m5': pair['txns'].get('m5', {}).get('buys', 0) + pair['txns'].get('m5', {}).get('sells', 0),  # Total transactions in the last 5 minutes
                'txns.h1': pair['txns'].get('h1', {}).get('buys', 0) + pair['txns'].get('h1', {}).get('sells', 0),  # Total transactions in the last hour
                'txns.h6': pair['txns'].get('h6', {}).get('buys', 0) + pair['txns'].get('h6', {}).get('sells', 0),  # Total transactions in the last 6 hours
                'txns.h24': pair['txns'].get('h24', {}).get('buys', 0) + pair['txns'].get('h24', {}).get('sells', 0),  # Total transactions in the last 24 hours
                'volume.m5': pair['volume'].get('m5', 0),
                'volume.h1': pair['volume'].get('h1', 0),
                'volume.h6': pair['volume'].get('h6', 0),
                'volume.h24': pair['volume'].get('h24', 0),
                'priceChange.h1': pair['priceChange'].get('h1', 0),
                'priceChange.h6': pair['priceChange'].get('h6', 0),
                'priceChange.h24': pair['priceChange'].get('h24', 0),
                'liquidity.total': pair['liquidity'].get('total', 0),
                'fdv': pair['fdv'],  # Fully Diluted Valuation
                'marketCap': pair.get('marketCap', 'N/A'),
                'pairCreatedAt': pair['pairCreatedAt']
            }
            dex_data.append(dex_info)
        
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(dex_data)
        print(df)  # Print the DataFrame
        
        return df  # Return the DataFrame
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    get_token_data()