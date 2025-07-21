import asyncio
from datetime import datetime

from NewsSentimentAnalysis.save_to_db import save_news_to_db, get_last_saved_time
from NewsSentimentAnalysis.scrapeNews import NEWS_CHANNELS_TELEGRAM, fetch_messages, date_range, fetch_messages_in_range


def getDataFromSeveralDates():
    link = NEWS_CHANNELS_TELEGRAM[3]
    start_date = "01-06-2024"
    end_date = "01-07-2025"

    all_results = asyncio.run(fetch_messages_in_range(link, start_date, end_date))

    for date in sorted(all_results.keys(), key=lambda d: datetime.strptime(d, "%d-%m-%Y")):
        result = all_results[date]
        if not result:
            print(f"⚠️ No messages found for {date}.")
            continue

        last_time_in_db = get_last_saved_time(link, date)
        last_time_in_result = max(result.keys())

        if last_time_in_db == last_time_in_result:
            print(f"⏩ Skipping {date} — already up-to-date.")
            continue

        save_news_to_db(result, link, date)
        print(f"✅ Saved {len(result)} messages for {date}.")


    # link = NEWS_CHANNELS_TELEGRAM[0]
    # start_date = "13-06-2025"
    # end_date = "20-06-2025"
    #
    # for date in date_range(start_date, end_date):
    #     print(f"\n📥 Fetching news for {date} from {link}")
    #     result = asyncio.run(fetch_messages(link, date))
    #
    #     if not result:
    #         print("⚠️ No messages found.")
    #         continue
    #
    #     last_time_in_db = get_last_saved_time(link, date)
    #     last_time_in_result = max(result.keys()) if result else None
    #
    #     if last_time_in_db == last_time_in_result:
    #         print(f"⏩ Skipping save — DB already up-to-date (last time: {last_time_in_db})")
    #         continue
    #
    #     save_news_to_db(result, link, date)
    #     print(f"✅ Saved {len(result)} messages to the DB.")


if __name__ == '__main__':

    getDataFromSeveralDates()

    # link = NEWS_CHANNELS_TELEGRAM[0]
    # date = "20-07-2025"  # "(DD-MM-YYYY)"
    #
    # result = asyncio.run(fetch_messages(link, date))
    #
    # save_news_to_db(result, link, date)
