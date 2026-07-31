import logging
import time
import pandas as pd
import requests
from datetime import date
from gnews import GNews
from tqdm import tqdm
from context import ProjectContext
from utils.excel_utils import export_to_excel, load_from_excel

logger = logging.getLogger(__name__)


class NewsSpider:
    def __init__(
        self,
        language: str = "en",
        country: str = "US",
        max_results: int = 100,
    ):
        self._check_connection()

        self._language = language
        self._country = country
        self._max_results = max_results

        self._google_news = None

    @staticmethod
    def _check_connection():
        response = requests.get(
            "https://news.google.com/rss",
            timeout=3,
        )
        response.raise_for_status()

    def get_company_news(self, company_name: str) -> list[dict]:
        try:
            return self._google_news.get_news(company_name) or []

        except Exception as e:
            logger.error(f"Failed to fetch news for {company_name}: {e}")
            return []

    def get_news(
        self,
        company_df: pd.DataFrame,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:

        results = []

        pbar = tqdm(
            company_df.iterrows(),
            total=len(company_df),
            desc="Fetching News",
        )

        for _, row in pbar:
            company = row["CompanyName"]
            pbar.set_postfix_str(company[:30])

            news_list = self.get_company_news(company)

            time.sleep(0.5)

            if not news_list:
                continue

            for news in news_list:
                try:
                    published_date = pd.to_datetime(news.get("published date")).date()
                except Exception:
                    continue

                if not (start_date <= published_date <= end_date):
                    continue

                results.append(
                    {
                        "CompanyName": company,
                        "BloombergAvailable": row["BloombergAvailable"],
                        "Date": published_date,
                        "Title": news.get("title", ""),
                        "Source": news.get("publisher", {}).get("title", ""),
                        "Url": news.get("url", ""),
                    }
                )

        logger.info(
            "News crawling completed: "
            f"collected {len(results)} news "
            f"from {len(company_df)} companies."
        )

        return pd.DataFrame(results)

    def run(
        self,
        context: ProjectContext,
        company_df: pd.DataFrame,
    ) -> pd.DataFrame:

        if context.paths.raw_news.exists():
            raw_news_df = load_from_excel(
                context.paths.raw_news,
                sheet_name="RawNews",
            )

            if not raw_news_df.empty:
                logger.info("Loading raw news...")
                return raw_news_df

        self._google_news = GNews(
            start_date=context.period.analysis_start_date,
            end_date=context.period.analysis_end_date,
            language=self._language,
            country=self._country,
            max_results=self._max_results,
        )

        raw_news_df = self.get_news(
            company_df=company_df,
            start_date=context.period.analysis_start_date,
            end_date=context.period.analysis_end_date,
        )

        export_to_excel(
            data=raw_news_df,
            file_path=context.paths.raw_news,
            sheet_name="RawNews",
        )

        return raw_news_df
