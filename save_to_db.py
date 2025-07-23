import sqlite3
import re
from datetime import datetime
from typing import Dict, Tuple, List

from NewsSentimentAnalysis.NewsItem import NewsItem


def clean_channel_name(link: str) -> str:
    """Convert Telegram channel link or @name to a valid SQLite table name"""
    name = link.split('/')[-1] if '/' in link else link
    name = name.replace('@', '')
    name = re.sub(r'\W+', '_', name)  # replace non-alphanumeric with _
    return name.lower()


def save_news_to_db(news_dict: Dict[str, Tuple[str, str, float]], channel_link: str, date_str: str, db_path="news.db"):
    """Save enriched news (message, sentiment, score) to a table named after the Telegram channel."""
    table_name = clean_channel_name(channel_link)

    # Convert to ISO format for DB (YYYY-MM-DD)
    iso_date_str = datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table if not exists with sentiment columns
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            message TEXT,
            sentiment TEXT,
            sentiment_score REAL
        )
    """)

    for time_str in sorted(news_dict.keys(), reverse=True):
        message, sentiment, score = news_dict[time_str]
        c.execute(f"""
            INSERT INTO {table_name} (date, time, message, sentiment, sentiment_score)
            VALUES (?, ?, ?, ?, ?)
        """, (iso_date_str, time_str, message, sentiment, score))

    conn.commit()
    conn.close()




#
# def save_news_to_db(news_dict: Dict[str, str], channel_link: str, date_str: str, db_path="news.db"):
#     """Save a dictionary of news to a table named after the Telegram channel"""
#     table_name = clean_channel_name(channel_link)
#
#     conn = sqlite3.connect(db_path)
#     c = conn.cursor()
#
#     # Create table if not exists
#     c.execute(f"""
#         CREATE TABLE IF NOT EXISTS {table_name} (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT,
#             time TEXT,
#             message TEXT
#         )
#     """)
#
#     # Insert rows
#     for time_str in sorted(news_dict.keys()):
#         message = news_dict[time_str]
#         c.execute(f"""
#             INSERT INTO {table_name} (date, time, message)
#             VALUES (?, ?, ?)
#         """, (date_str, time_str, message))
#
#     conn.commit()
#     conn.close()



def get_last_saved_time(channel_link: str, date_str: str, db_path="news.db") -> str:
    """Return the latest saved time string (HH:MM) for a given channel and date"""
    table_name = clean_channel_name(channel_link)

    # Convert date_str from "DD-MM-YYYY" to "YYYY-MM-DD"
    iso_date_str = datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute(f"""
            SELECT time FROM {table_name}
            WHERE date = ?
            ORDER BY time DESC
            LIMIT 1
        """, (iso_date_str,))
        row = c.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()



def getNewsFromDBInDates(start_date: str, end_date: str, db_path="news.db") -> Dict[str, List[NewsItem]]:
    """Read news from all tables between given dates (inclusive) and return as dict[date] = List[NewsItem]"""
    result_dict = {}

    # Convert input dates from DD-MM-YYYY to YYYY-MM-DD for DB filtering
    start_iso = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    end_iso = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get all table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in c.fetchall()]

    for table in table_names:
        try:
            c.execute(f"""
                SELECT date, time, message, sentiment, sentiment_score FROM {table}
                WHERE date >= ? AND date <= ?
            """, (start_iso, end_iso))

            rows = c.fetchall()
            for date_str, time_str, msg, sentiment, score in rows:
                # Convert date from YYYY-MM-DD to DD-MM-YYYY for output
                display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")

                news_item = NewsItem(
                    news_site=table,
                    date=display_date,
                    time=time_str,
                    news_string=msg,
                    sentiment=sentiment or "",
                    sentiment_score=round(score, 2) if score is not None else None
                )

                if display_date not in result_dict:
                    result_dict[display_date] = []
                result_dict[display_date].append(news_item)
        except Exception as e:
            print(f"⚠️ Skipping table {table}: {e}")
            continue

    conn.close()
    return result_dict