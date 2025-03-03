##this script takes the top news articles from CCData and saves them to a dataframe
import requests
import pandas as pd  # Import pandas
from datetime import datetime, timedelta  # Import datetime for date conversion
import time

def get_news_articles(timespan='24h', max_articles=100):
    """
    Get news articles for a specific timespan
    timespan options: '24h', 'week', 'month'
    max_articles: maximum number of articles to fetch
    """
    current_time = datetime.now()
    
    if timespan == '24h':
        start_time = current_time - timedelta(days=1)
    elif timespan == 'week':
        start_time = current_time - timedelta(weeks=1)
    elif timespan == 'month':
        start_time = current_time - timedelta(days=30)
    else:
        raise ValueError("Invalid timespan. Choose '24h', 'week', or 'month'")

    ts_to = int(current_time.timestamp())
    ts_from = int(start_time.timestamp())

    url = (
        "https://data-api.cryptocompare.com/news/v1/article/list"
        "?lang=EN"
        "&sortOrder=latest"
        "&feeds=decrypt,coindesk,cointelegraph,cryptonews,bitcoinist,newsbtc,cryptopotato,ambcrypto"
        "&excludeCategories=Sponsored,Sponsored Content"
        "&toTs={to_ts}"
        "&fromTs={from_ts}"
        "&limit=100"
    )

    all_articles = pd.DataFrame()
    seen_titles = set()
    current_ts = ts_to
    no_new_articles_count = 0

    while len(all_articles) < max_articles:
        try:
            print(f"Fetching articles from {datetime.fromtimestamp(ts_from)} to {datetime.fromtimestamp(current_ts)}")
            current_url = url.format(
                to_ts=current_ts,
                from_ts=ts_from
            )
            
            response = requests.get(current_url)
            response.raise_for_status()
            data = response.json()
            
            if not data['Data']:
                print("No more articles available")
                break
                
            df = pd.DataFrame(data['Data'])
            df['PUBLISHED_ON'] = pd.to_datetime(df['PUBLISHED_ON'], unit='s')
            
            # Remove duplicates
            new_articles = df[~df['TITLE'].isin(seen_titles)]
            
            if len(new_articles) == 0:
                no_new_articles_count += 1
                if no_new_articles_count >= 3:
                    print("No new articles found in last 3 fetches, stopping...")
                    break
            else:
                no_new_articles_count = 0
                
            seen_titles.update(new_articles['TITLE'])
            all_articles = pd.concat([all_articles, new_articles], ignore_index=True)
            
            print(f"Total unique articles so far: {len(all_articles)}/{max_articles}")
            
            if len(all_articles) >= max_articles:
                all_articles = all_articles.head(max_articles)
                break
            
            # Update timestamp for next batch
            if not df.empty:
                current_ts = int(df['PUBLISHED_ON'].min().timestamp())
            
            time.sleep(0.5)  # Add small delay between requests
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")
            break

    # Sort articles by publication date (newest first)
    all_articles = all_articles.sort_values('PUBLISHED_ON', ascending=False).reset_index(drop=True)

    print(f"\nData Collection Summary:")
    print(f"Timespan: {timespan}")
    print(f"Period: {start_time} to {current_time}")
    print(f"Total unique articles: {len(all_articles)}")
    
    # Print articles
    print("\nArticle Headlines:")
    for idx, row in all_articles.iterrows():
        print(f"{idx + 1}. {row['TITLE']}")
        print(f"   Published: {row['PUBLISHED_ON']}")
    
    return all_articles

if __name__ == "__main__":
    timespan = input("Enter timespan (24h/week/month): ").lower()
    max_articles = int(input("Enter maximum number of articles to fetch: "))
    all_articles = get_news_articles(timespan, max_articles)  # Assign to all_articles
    print(all_articles)
else:
    # Default values when imported as a module
    all_articles = get_news_articles('24h', 100)

# Save to CSV with timestamp
# timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# filename = f'crypto_news_{timestamp}.csv'
# all_articles.to_csv(filename, index=False)
# print(f"\nSaved news articles to: {filename}")

# The DataFrame is still available for other scripts to use
print(all_articles)
