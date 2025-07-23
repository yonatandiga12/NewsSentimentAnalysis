import asyncio
from datetime import datetime

from tqdm import tqdm

from NewsSentimentAnalysis.SentimentModels import enrich_messages_dict_with_sentiment
from NewsSentimentAnalysis.save_to_db import save_news_to_db, get_last_saved_time, getNewsFromDBInDates
from NewsSentimentAnalysis.scrapeNews import NEWS_CHANNELS_TELEGRAM, fetch_messages, date_range, fetch_messages_in_range


# def getDataFromSeveralDates(index):
#     link = NEWS_CHANNELS_TELEGRAM[index]
#     start_date = "10-06-2025"
#     end_date = "01-07-2025"
#
#     all_results = asyncio.run(fetch_messages_in_range(link, start_date, end_date))
#
#     for date in sorted(all_results.keys(), key=lambda d: datetime.strptime(d, "%d-%m-%Y")):
#         result = all_results[date]
#         if not result:
#             print(f"⚠️ No messages found for {date}.")
#             continue
#
#         last_time_in_db = get_last_saved_time(link, date)
#         last_time_in_result = max(result.keys())
#
#         if last_time_in_db == last_time_in_result:
#             print(f"⏩ Skipping {date} — already up-to-date.")
#             continue
#
#         save_news_to_db(result, link, date)
#         print(f"✅ Saved {len(result)} messages for {date}.")
#
#


def getDataFromSeveralDates(index):
    link = NEWS_CHANNELS_TELEGRAM[index]
    start_date = "25-06-2025"
    end_date = "01-07-2025"

    all_results = asyncio.run(fetch_messages_in_range(link, start_date, end_date))
    all_dates = sorted(all_results.keys(), key=lambda d: datetime.strptime(d, "%d-%m-%Y"))

    for date in tqdm(all_dates, desc=f"📅 Processing {link}"):
        result = all_results[date]

        if not result:
            tqdm.write(f"⚠️ No messages found for {date}.")
            continue

        last_time_in_db = get_last_saved_time(link, date)
        last_time_in_result = max(result.keys())

        if last_time_in_db == last_time_in_result:
            tqdm.write(f"⏩ Skipping {date} — already up-to-date.")
            continue

        enriched_result = enrich_messages_dict_with_sentiment(result)
        save_news_to_db(enriched_result, link, date)
        tqdm.write(f"✅ Saved {len(enriched_result)} messages for {date}.")



if __name__ == '__main__':

    # #Get data from all sites
    for i in range(len(NEWS_CHANNELS_TELEGRAM)):
        getDataFromSeveralDates(i)

    start_date = "18-06-2025"
    end_date = "20-06-2025"
    news_items = getNewsFromDBInDates(start_date, end_date)

    #analyze_sentiment_heBERT(news_items)

    # link = NEWS_CHANNELS_TELEGRAM[0]
    # date = "20-07-2025"  # "(DD-MM-YYYY)"
    #
    # result = asyncio.run(fetch_messages(link, date))
    #
    # save_news_to_db(result, link, date)
