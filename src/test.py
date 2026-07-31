from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from llm.news_searcher import NewsSearcher
from utils.excel_utils import export_to_excel

OUTPUT_FILE = Path("news0730COMPANY.xlsx")

def main():
    names = [
       "KEX EXPRESS(TH)PCL",
       "HONGLIN ELECTRIC POWER TECHNOLOGY (th) co.,ltd",
       "dingheng new materials co.,ltd"
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
            
            if df.empty:
                print("  ✓ No news")
                continue

            if OUTPUT_FILE.exists():
                old_df = pd.read_excel(OUTPUT_FILE)
                df = pd.concat([old_df, df], ignore_index=True)

            export_to_excel(
                data=df,
                file_path=OUTPUT_FILE
            )

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