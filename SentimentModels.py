from typing import Dict, List
from collections import Counter
from transformers import pipeline

from NewsSentimentAnalysis.NewsItem import NewsItem

# Load once, globally
sentiment_model_heBERT = pipeline("sentiment-analysis", model="avichr/heBERT_sentiment_analysis")

sentiment_model_dictaBert = pipeline("text-classification", model="dicta-il/dictabert-sentiment")


def enrich_messages_dict_with_sentiment(messages_dict: dict) -> dict:
    """
    Enriches messages_dict {time_str: message_string} with sentiment and score.
    Returns a new dict {time_str: (message, sentiment_label, score)}
    """
    time_keys = list(messages_dict.keys())
    texts = list(messages_dict.values())

    # Run batch sentiment analysis
    results = sentiment_model_heBERT(texts)

    # Build enriched dict
    enriched = {}
    for i, time_str in enumerate(time_keys):
        result = results[i]
        enriched[time_str] = (
            texts[i],                  # original message
            result["label"],          # sentiment label
            round(result["score"], 2) # confidence score
        )

    return enriched




def getSecondModelPredictions(newsItems: Dict[str, List[NewsItem]], batch_size = 16):
    """
    Takes a dictionary of {date: [NewsItem, ...]} and fills each NewsItem's .sentiment field.
    """
    for date, items in newsItems.items():
        print(f"🔍 Analyzing {len(items)} items for {date}...")

        texts = [item.news_string for item in items]

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            results = sentiment_model_dictaBert(batch)

            for j, result in enumerate(results):
                items[i + j].sentiment2 = result['label']
                items[i + j].sentiment_score2 = round(result['score'], 2)  # rounded to 2 decimal places





def compareTwoModels(newsItems: Dict[str, List[NewsItem]]):
    disagree_list = []
    low_confidence_list = []

    for date, items in newsItems.items():
        for item in items:
            # Check if both sentiments are non-empty (to avoid crashing on .lower())
            if item.sentiment and item.sentiment2:
                if item.sentiment.lower() != item.sentiment2.lower():
                    disagree_list.append(item)

            # Check for low confidence
            if (item.sentiment_score is not None and item.sentiment_score < 0.7) or \
                    (item.sentiment_score2 is not None and item.sentiment_score2 < 0.7):
                low_confidence_list.append(item)

    disagree_set = set(id(x) for x in disagree_list)

    for news in disagree_list:
        print(f'Sentiment 1: {news.sentiment}, \nSentiment 2: {news.sentiment2}. \nNews Items are: {news.news_string}\n\n')

    printSomeData(newsItems)



def printSomeData(newsItems):
    sentiment1_counter = Counter()
    sentiment2_counter = Counter()

    for items in newsItems.values():
        for item in items:
            if item.sentiment:
                sentiment1_counter[item.sentiment.lower()] += 1
            if item.sentiment2:
                sentiment2_counter[item.sentiment2.lower()] += 1

    print("Model 1 Sentiment Counts:")
    for sentiment in ['positive', 'neutral', 'negative']:
        print(f"{sentiment.capitalize()}: {sentiment1_counter.get(sentiment, 0)}")

    print("\nModel 2 Sentiment Counts:")
    for sentiment in ['positive', 'neutral', 'negative']:
        print(f"{sentiment.capitalize()}: {sentiment2_counter.get(sentiment, 0)}")



#
#
#
# def analyze_sentiment_heBERT(news_items: Dict[str, List[NewsItem]], batch_size: int = 16):
#     """
#     Takes a dictionary of {date: [NewsItem, ...]} and fills each NewsItem's .sentiment field.
#     """
#     for date, items in news_items.items():
#         print(f"🔍 Analyzing {len(items)} items for {date}...")
#
#         texts = [item.news_string for item in items]
#
#         for i in range(0, len(texts), batch_size):
#             batch = texts[i:i + batch_size]
#             results = sentiment_model_heBERT(batch)
#
#             for j, result in enumerate(results):
#                 items[i + j].sentiment = result['label']
#                 items[i + j].sentiment_score = round(result['score'], 2)  # rounded to 2 decimal places

