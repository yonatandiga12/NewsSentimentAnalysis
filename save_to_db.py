import sqlite3
import re
from typing import Dict



def clean_channel_name(link: str) -> str:
    """Convert Telegram channel link or @name to a valid SQLite table name"""
    name = link.split('/')[-1] if '/' in link else link
    name = name.replace('@', '')
    name = re.sub(r'\W+', '_', name)  # replace non-alphanumeric with _
    return name.lower()


def save_news_to_db(news_dict: Dict[str, str], channel_link: str, date_str: str, db_path="news.db"):
    """Save a dictionary of news to a table named after the Telegram channel"""
    table_name = clean_channel_name(channel_link)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table if not exists
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            message TEXT
        )
    """)

    # Insert rows
    for time_str in sorted(news_dict.keys()):
        message = news_dict[time_str]
        c.execute(f"""
            INSERT INTO {table_name} (date, time, message)
            VALUES (?, ?, ?)
        """, (date_str, time_str, message))

    conn.commit()
    conn.close()




def get_last_saved_time(channel_link: str, date_str: str, db_path="news.db") -> str:
    """Return the latest saved time string (HH:MM) for a given channel and date"""
    table_name = clean_channel_name(channel_link)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute(f"""
            SELECT time FROM {table_name}
            WHERE date = ?
            ORDER BY time DESC
            LIMIT 1
        """, (date_str,))
        row = c.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()