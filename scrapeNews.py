import re

import pytz
from dotenv import load_dotenv
import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta
import asyncio


load_dotenv()  # loads the .env file

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
#openai_key = os.getenv("OPENAI_API_KEY")

NEWS_CHANNELS_TELEGRAM = ["@N12_News", "@amitsegal", "@ynetalerts", "@lieldaphna"]




# Timezone setup
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")
UTC_TZ = pytz.utc

# Main async function to fetch messages on a specific date
async def fetch_messages(link: str, target_date_str: str):
    # Parse input date (assumed to be in Israel time)
    target_date_dt = ISRAEL_TZ.localize(datetime.strptime(target_date_str, "%d-%m-%Y"))
    next_day_dt = target_date_dt + timedelta(days=1)

    messages_dict = {}

    async with TelegramClient('session_name', api_id, api_hash) as client:
        entity = await client.get_entity(link)

        offset_id = 0
        limit = 100

        while True:
            history = await client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            for message in history.messages:
                if not message.message:
                    continue

                # message.date is in naive UTC, make it timezone-aware
                msg_date_utc = message.date.astimezone(pytz.utc)
                msg_date_local = msg_date_utc.astimezone(ISRAEL_TZ)

                # Filter by local Israel date
                if target_date_dt.date() <= msg_date_local.date() < next_day_dt.date():
                    time_str = msg_date_local.strftime("%H:%M")
                    messages_dict[time_str] = clean_news_text(message.message)
                elif msg_date_local < target_date_dt:
                    return messages_dict  # Done fetching relevant messages

            offset_id = history.messages[-1].id

    return messages_dict, link, msg_date_local


async def fetch_messages_in_range(link: str, start_date_str: str, end_date_str: str):
    start_dt = ISRAEL_TZ.localize(datetime.strptime(start_date_str, "%d-%m-%Y"))
    end_dt = ISRAEL_TZ.localize(datetime.strptime(end_date_str, "%d-%m-%Y")) + timedelta(days=1)

    all_messages = {}  # {date_str: {time_str: message}}

    async with TelegramClient('session_name', api_id, api_hash) as client:
        entity = await client.get_entity(link)

        offset_id = 0
        limit = 100

        while True:
            history = await client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            for message in history.messages:
                if not message.message:
                    continue

                if len(message.message) > 500:
                    continue

                msg_date_local = message.date.astimezone(ISRAEL_TZ)

                # Stop early if we’ve gone before the start
                if msg_date_local < start_dt:
                    return all_messages

                if start_dt <= msg_date_local < end_dt:
                    date_str = msg_date_local.strftime("%d-%m-%Y")
                    time_str = msg_date_local.strftime("%H:%M")

                    clean_msg = clean_news_text(message.message)

                    if date_str not in all_messages:
                        all_messages[date_str] = {}

                    all_messages[date_str][time_str] = clean_msg

            offset_id = history.messages[-1].id

    return all_messages

def date_range(start_date_str, end_date_str, fmt="%d-%m-%Y"):
    """Generate list of date strings in range [start, end]"""
    start_dt = datetime.strptime(start_date_str, fmt)
    end_dt = datetime.strptime(end_date_str, fmt)
    delta = timedelta(days=1)

    current = start_dt
    while current <= end_dt:
        yield current.strftime(fmt)
        current += delta



def clean_news_text(text: str) -> str:
    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    # Remove hashtags
    text = re.sub(r"#\w+", " ", text)
    # Keep only Hebrew, English, and basic ASCII
    # Hebrew: \u0590–\u05FF, English letters: a-zA-Z, digits and basic punctuation
    text = re.sub(r"[^\u0590-\u05FFa-zA-Z0-9 .,!?\"'()\[\]{}:;@#$%&*-+=/\\]", " ", text)
    # Normalize whitespace
    return re.sub(r"\s+", " ", text).strip()













if __name__ == '__main__':
    link = NEWS_CHANNELS_TELEGRAM[0]
    date = "20-07-2025"   #"(DD-MM-YYYY)"

    result = asyncio.run(fetch_messages(link, date))

    print(f"\nNews for {date} from {link}:\n")
    for time, text in sorted(result.items()):
        print(f"[{time}] {text}")














