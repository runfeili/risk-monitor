from datetime import date, timedelta
import pandas as pd
from pathlib import Path

from llm.news_searcher import NewsSearcher

OUTPUT_FILE = Path("test_news_add.xlsx")

def main():

    # companies = [
    #     "Southland Resources Co., Ltd",
    #     "Mitr Phol Sugar Corporation Limited",
    #     "Thantawan Industry Public Company Limited",
    #     "Thai Union Group Public Company Limited",
    #     "Panjawattana Plastic Public Company Limited",
    #     "Anglo Singapore International Co., Ltd",
    #     "COOEC (Thailand) Company Limited",
    # ]
    names = [
        "Southland Group",
        "Mr. Pherm Tirasarnvong",
        "Mid Siam Sugar Co., Ltd. Shareholding",
        "Vongkusolkit family",
        "ADPOWER INTERNATIONAL CO., LTD",
        "Nam Archhpasit",
        "Thai Union Group",
        "Anglo Singapore International Group",
        "Mr. Pariya Chunhasawatdikul",
        "Hemmondharop family"
    ]

    end_date = date.today()
    start_date = end_date - timedelta(days=180)

    searcher = NewsSearcher()

    total = len(names)

    for i, company in enumerate(names, start=1):
        print(f"[{i}/{total}] Searching {company}...")

        try:
            news = searcher.search_batch(
                companies=[company],
                start_date=start_date,
                end_date=end_date,
            )

            df = pd.DataFrame(news)

            # 没有结果也跳过
            if df.empty:
                print("  ✓ No news")
                continue

            # 第一次写入，之后追加
            if OUTPUT_FILE.exists():
                old_df = pd.read_excel(OUTPUT_FILE)
                df = pd.concat([old_df, df], ignore_index=True)

            df.to_excel(OUTPUT_FILE, index=False)

            print(f"  ✓ Appended {len(news)} news")

        except Exception as e:
            print(f"  ✗ Failed: {e}")

    if OUTPUT_FILE.exists():
        total_news = len(pd.read_excel(OUTPUT_FILE))
    else:
        total_news = 0

    print(f"\nFinished. Total news: {total_news}")


if __name__ == "__main__":
    main()