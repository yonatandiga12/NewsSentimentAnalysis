from typing import Dict, List

from transformers import pipeline

from NewsSentimentAnalysis.NewsItem import NewsItem

# Load once, globally
sentiment_model_heBERT = pipeline("sentiment-analysis", model="avichr/heBERT_sentiment_analysis")




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

