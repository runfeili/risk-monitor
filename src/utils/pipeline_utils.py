import pandas as pd
from config import TOP_N
from context import ProjectContext


def build_spider_company_df(context: ProjectContext):
    """
    Build a DataFrame of companies to be crawled by the news-spider.
    This includes both TOP_N Bloomberg-available and non-Bloomberg-available companies.
    """
    bbg_df = context.news_metric_df.head(TOP_N)
    nonbbg_df = context.nonbbg_companies_df

    # Combine both DataFrames
    combined_df = pd.concat([bbg_df, nonbbg_df], ignore_index=True)

    return combined_df


def build_search_company_df(context: ProjectContext):
    """
    Build a DataFrame of companies to be searched by the news-searcher.

    Includes:
    - TOP_N Bloomberg-available companies
    - Non-Bloomberg companies with raw news

    Excludes:
    - Companies already identified in risk news
    """

    # Bloomberg TOP_N companies
    bbg_df = context.news_metric_df.head(TOP_N)

    # Non-Bloomberg companies with raw news
    companies_with_news = set(context.raw_news_df["CompanyName"].unique())

    nonbbg_df = context.nonbbg_companies_df[
        context.nonbbg_companies_df["CompanyName"].isin(companies_with_news)
    ]

    # Combine candidates
    combined_df = pd.concat(
        [bbg_df, nonbbg_df],
        ignore_index=True,
    )

    # Remove companies already in risk news
    if context.risk_news_df is not None and not context.risk_news_df.empty:
        risk_companies = set(context.risk_news_df["CompanyName"].unique())
    else:
        risk_companies = set()

    combined_df = combined_df[
        ~combined_df["CompanyName"].isin(risk_companies)
    ].reset_index(drop=True)

    return combined_df
