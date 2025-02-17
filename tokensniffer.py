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
    # MongoDB Atlas setup
    try:
        MONGO_URI = os.getenv('MONGODB_URI')  # Get connection string from .env file
        if not MONGO_URI:
            raise ConfigurationError("MongoDB URI not found in .env file")
            
        client = MongoClient(MONGO_URI)
        db = client['crypto_data']  # Your database name
        collection = db['token_pairs']  # Your collection name
        
        # Test connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB!")
        
    except (ConfigurationError, ServerSelectionTimeoutError) as e:
        print(f"MongoDB connection error: {e}")
        return None

    #       Trump coin address on Solana
    token_address = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"
    
    # DexScreener API endpoint
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
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
            dex_data.append(dex_info)
        
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(dex_data)
        print(df)  # Print the DataFrame
        
        # Convert DataFrame to MongoDB documents
        records = df.to_dict('records')
        
        # Insert into MongoDB with timestamp
        result = collection.insert_many(records)
        print(f"\nInserted {len(result.inserted_ids)} documents into MongoDB")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    get_token_data()