import requests
import json
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_token_data():
    # Dictionary of tokens to track
    tokens = {
        'TRUMP': '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN',
        'FART': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',
        'DOGE': '0xba2ae424d960c26247dd6c32edc70b295c744c43',
        'PEPE': '0x6982508145454ce325ddbe47a25d4ec3d2311933',
        'FLOKI': '0xcf0c122c6b73ff809c693db761e7baebe62b6a2e',
        'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
        'VINE': '6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump',
        'POPCAT': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr'
    }
    
    # MongoDB Atlas setup
    try:
        MONGO_URI = os.getenv('MONGODB_URI')
        if not MONGO_URI:
            raise ConfigurationError("MongoDB URI not found in .env file")
            
        client = MongoClient(MONGO_URI)
        db = client['crypto_data']
        collection = db['token_pairs']
        
        # Test connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB!")
        
    except (ConfigurationError, ServerSelectionTimeoutError) as e:
        print(f"MongoDB connection error: {e}")
        return None

    all_token_data = []
    
    # Fetch data for each token
    for token_name, token_address in tokens.items():
        print(f"\nFetching data for {token_name}...")
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data['pairs']:
                for pair in data['pairs']:
                    dex_info = {
                        'token_name': token_name,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'chainID': pair['chainId'],
                        'dexID': pair['dexId'],
                        'baseToken.symbol': pair['baseToken']['symbol'],
                        'pairToken.symbol': pair['quoteToken']['symbol'],
                        'priceNative': pair['priceNative'],
                        'priceUSD': pair['priceUsd'],
                        'txns.m5': pair['txns'].get('m5', {}).get('buys', 0) + pair['txns'].get('m5', {}).get('sells', 0),
                        'txns.h1': pair['txns'].get('h1', {}).get('buys', 0) + pair['txns'].get('h1', {}).get('sells', 0),
                        'txns.h6': pair['txns'].get('h6', {}).get('buys', 0) + pair['txns'].get('h6', {}).get('sells', 0),
                        'txns.h24': pair['txns'].get('h24', {}).get('buys', 0) + pair['txns'].get('h24', {}).get('sells', 0),
                        'volume.m5': pair['volume'].get('m5', 0),
                        'volume.h1': pair['volume'].get('h1', 0),
                        'volume.h6': pair['volume'].get('h6', 0),
                        'volume.h24': pair['volume'].get('h24', 0),
                        'priceChange.h1': pair['priceChange'].get('h1', 0),
                        'priceChange.h6': pair['priceChange'].get('h6', 0),
                        'priceChange.h24': pair['priceChange'].get('h24', 0),
                        'liquidity.total': pair['liquidity'].get('total', 0),
                        'fdv': pair['fdv'],
                        'marketCap': pair.get('marketCap', 'N/A'),
                        'pairCreatedAt': pair['pairCreatedAt']
                    }
                    all_token_data.append(dex_info)
            else:
                print(f"No trading pairs found for {token_name}")
                
        except Exception as e:
            print(f"Error fetching data for {token_name}: {e}")
            continue
    
    # Create DataFrame with all token data
    df = pd.DataFrame(all_token_data)
    print(df)
    
    # Save to MongoDB
    if len(all_token_data) > 0:
        result = collection.insert_many(all_token_data)
        print(f"\nInserted {len(result.inserted_ids)} documents into MongoDB")
    
    return df

if __name__ == "__main__":
    get_token_data()