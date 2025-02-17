##this script takes the top news articles from CCData and saves them to a dataframe
import requests
import pandas as pd  # Import pandas
from datetime import datetime, timedelta  # Import datetime for date conversion

# Calculate timestamp for 24 hours ago
current_time = datetime.now()
one_day_ago = current_time - timedelta(days=1)

# Define the endpoint URL
url = "https://data-api.cryptocompare.com/news/v1/article/list?lang=EN&limit=10&page={page}&source_ids=coindesk,cointelegraph,cryptoglobe,blockworks,decrypt,forbes,financialtimes_crypto_,yahoofinance"

# Initialize an empty DataFrame to store all articles
all_articles = pd.DataFrame()

# Loop through pages
for page in range(1, 10):
    response = requests.get(url.format(page=page))

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['Data'])
        
        # Convert PUBLISHED_ON to datetime
        df['PUBLISHED_ON'] = pd.to_datetime(df['PUBLISHED_ON'], unit='s')
        
        # Filter for articles within last 24 hours
        recent_articles = df[df['PUBLISHED_ON'] >= one_day_ago]
        
        # If no recent articles found, stop fetching more pages
        if len(recent_articles) == 0:
            print(f"No articles from last 24 hours found on page {page}, stopping...")
            break
            
        # Append only recent articles to main DataFrame
        all_articles = pd.concat([all_articles, recent_articles], ignore_index=True)
        print(f"Page {page}: Found {len(recent_articles)} articles from last 24 hours")
    else:
        print(f"Error: {response.status_code}")

# Save to CSV with timestamp
# timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# filename = f'crypto_news_{timestamp}.csv'
# all_articles.to_csv(filename, index=False)
# print(f"\nSaved news articles to: {filename}")

# Print summary
print(f"\nData Collection Summary:")
print(f"Total articles collected: {len(all_articles)}")
print(f"Time window: Last 24 hours ({one_day_ago.strftime('%Y-%m-%d %H:%M')} to {current_time.strftime('%Y-%m-%d %H:%M')})")
print(f"Date range of articles: {all_articles['PUBLISHED_ON'].min()} to {all_articles['PUBLISHED_ON'].max()}")
print(f"Sources: {all_articles['SOURCE_ID'].unique()}")

# The DataFrame is still available for other scripts to use
print(all_articles)