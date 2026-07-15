import pandas as pd
import logging
import time
from datetime import date
from tqdm import tqdm
from context import ProjectContext
from spiders.google_news import GoogleNewsSpider
from utils.excel_utils import export_to_excel, load_from_excel


logger = logging.getLogger(__name__)


class NewsSpider:
    def __init__(self):
        self._spider = None

    def get_news(
        self,
        company_df: pd.DataFrame,
        start_date: date,
        end_date: date
    ):
        results = []

        pbar = tqdm(
            company_df.iterrows(),
            total=len(company_df),
            desc="Fetching News",
        )

        for _, row in pbar:
            company = row["CompanyName"]
            pbar.set_postfix_str(company[:30])
            news = self._spider.get_company_news(company)
            time.sleep(0.5)
            news = self._spider.simplify_news(news)

            if not news:
                continue

            for item in news:
                date = pd.to_datetime(item["published_date"]).date()
                if not (start_date <= date <= end_date):
                    continue

                title = item["title"]

                results.append(
                    {
                        "CompanyName": company,
                        "BloombergAvailable": row["BloombergAvailable"],
                        "Date": date,
                        "Title": title,
                        "Source": item["publisher"],
                        "Url": item["url"],
                    }
                )

        logger.info(
            f"News crawling completed: "
            f"collected {len(results)} news "
            f"from {len(company_df)} companies."
        )

        return pd.DataFrame(results)

    def run(
        self,
        context: ProjectContext,
        company_df: pd.DataFrame,
    ):  
        if context.paths.raw_news.exists():
            raw_news_df = load_from_excel(context.paths.raw_news, sheet_name="RawNews")
            if not raw_news_df.empty:
                logger.info("Loading raw news...")
                return raw_news_df

        self._spider = GoogleNewsSpider(
            start_date=context.period.analysis_start_date, 
            end_date=context.period.analysis_end_date
        )
        raw_news_df = self.get_news(
            company_df=company_df, 
            start_date=context.period.analysis_start_date, 
            end_date=context.period.analysis_end_date
        )
        export_to_excel(
            data=raw_news_df,
            file_path=context.paths.raw_news, 
            sheet_name="RawNews"
        )
        return raw_news_df
