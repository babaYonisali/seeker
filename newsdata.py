##this script takes the top news articles from CCData and saves them to a dataframe
import requests
import pandas as pd  # Import pandas
from datetime import datetime  # Import datetime for date conversion

# Define the endpoint URL
url = "https://data-api.cryptocompare.com/news/v1/article/list?lang=EN&limit=10&page={page}&source_ids=coindesk,cointelegraph,cryptoglobe,blockworks,decrypt,forbes,financialtimes_crypto_,yahoofinance"

# Initialize an empty DataFrame to store all articles
all_articles = pd.DataFrame()

# Loop through pages (adjust the range as needed)
for page in range(1, 10):  # Example: fetching 5 pages
    response = requests.get(url.format(page=page))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        df = pd.DataFrame(data['Data'])  # Create a DataFrame from the 'Data' key
        
        # Convert PUBLISHED_ON timestamp to a date
        df['PUBLISHED_ON'] = pd.to_datetime(df['PUBLISHED_ON'], unit='s')  # Adjust unit if necessary
        
        # Append the current page's DataFrame to the all_articles DataFrame
        all_articles = pd.concat([all_articles, df], ignore_index=True)
    else:
        print(f"Error: {response.status_code}")

# Print the combined DataFrame or process it as needed
print(all_articles)