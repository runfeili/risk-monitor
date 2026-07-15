from __future__ import annotations
from datetime import date
from typing import Any
from gnews import GNews
import logging
import requests

logger = logging.getLogger(__name__)


class GoogleNewsSpider:
    def __init__(
        self,
        start_date: date,
        end_date: date,
        language: str = "en",
        country: str = "US",
        max_results: int = 100
    ):
        self.check_connection()
        self._google_news = GNews(
            start_date=start_date, 
            end_date=end_date,
            language=language,
            country=country,
            max_results=max_results
        )

    def check_connection(self):
        response = requests.get(
            "https://news.google.com/rss",
            timeout=3,
        )
        response.raise_for_status()

    def get_company_news(
        self,
        company_name: str,
    ):
        logger.debug(f"Fetching news: {company_name}")

        try:
            news = self._google_news.get_news(company_name)
            logger.debug(f"{company_name}: {len(news)} news found")

            if news is None:
                return []

            return news

        except Exception as e:
            logger.error(f"Failed to fetch news for {company_name}: {e}")

            return []

    @staticmethod
    def simplify_news(news_list: list[dict[str, Any]]) -> list[dict[str, str]]:
        results = []

        for news in news_list:
            results.append(
                {
                    "title": news.get("title", ""),
                    "publisher": (news.get("publisher", {}).get("title", "")),
                    "published_date": news.get("published date", ""),
                    "url": news.get("url", ""),
                }
            )

        return results
