from dataclasses import dataclass

@dataclass
class NewsItem:
    news_site: str
    date: str
    time: str
    news_string: str
    sentiment: str = ""
    sentiment_score: float = None  # new field
