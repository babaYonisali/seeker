from openai import OpenAI
import pandas as pd
from newsdata import all_articles
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

class DeepSeekAPI:
    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

    def analyze_article_importance(self, title):
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                prompt = f"""
                Rate this cryptocurrency news headline's importance from 0-10 based on these criteria:
                - Is it about fundamental industry changes or developments?
                - Does it contain groundbreaking news or significant innovations?
                - Is it focused on long-term impact rather than short-term price analysis?
                - Is it about major industry developments or regulatory changes?

                Headline: {title}

                Important: Return only a single number between 0-10 as your response.
                """
                
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Respond only with a number between 0 and 10."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=50,
                    stream=False
                )
                
                content = response.choices[0].message.content.strip()
                numeric_content = ''.join(c for c in content if c.isdigit() or c == '.')
                rating = float(numeric_content)
                rating = min(max(rating, 0), 10)
                
                print(f"Successfully rated headline with score: {rating}")
                return rating
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print("All retries failed")
                    return 0

def get_top_articles(df, num_articles=5):
    api = DeepSeekAPI()
    article_ratings = []
    
    for idx, row in df.iterrows():
        print(f"\nProcessing headline {idx + 1}/{len(df)}")
        print(f"Title: {row['TITLE'][:100]}...")
        
        # Only pass the title for analysis
        rating = api.analyze_article_importance(row['TITLE'])
        article_ratings.append(rating)
        
        time.sleep(3)  # Delay between requests
    
    df['importance_rating'] = article_ratings
    top_articles = df.nlargest(num_articles, 'importance_rating')
    result_df = top_articles[['TITLE', 'URL', 'PUBLISHED_ON', 'importance_rating']]  # Removed BODY
    
    return result_df

if __name__ == "__main__":
    # Get the top 5 most important articles
    top_articles = get_top_articles(all_articles)
    
    # Display results
    print("\nTop 5 Most Important Articles:")
    print("============================")
    for idx, row in top_articles.iterrows():
        print(f"\nTitle: {row['TITLE']}")
        print(f"Published: {row['PUBLISHED_ON']}")
        print(f"Importance Rating: {row['importance_rating']}")
        print(f"URL: {row['URL']}")
        print("----------------------------") 