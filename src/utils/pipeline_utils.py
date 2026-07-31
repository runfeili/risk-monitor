import pandas as pd
from config import TOP_N
from context import ProjectContext

STOCK_3M_THRESHOLD = -0.20
RELATIVE_3M_THRESHOLD = -0.15
STOCK_6M_THRESHOLD = -0.30
RELATIVE_6M_THRESHOLD = -0.25


def build_spider_company_df(context: ProjectContext):
    bbg_df_news = context.news_metric_df.head(TOP_N)
    bbg_df_finance = context.financial_metric_df[
        (context.financial_metric_df["Stock_3M"] <= STOCK_3M_THRESHOLD)
        | (context.financial_metric_df["Relative_3M"] <= RELATIVE_3M_THRESHOLD)
        | (context.financial_metric_df["Stock_6M"] <= STOCK_6M_THRESHOLD)
        | (context.financial_metric_df["Relative_6M"] <= RELATIVE_6M_THRESHOLD)
    ].copy()
    nonbbg_df = context.nonbbg_companies_df

    # Combine both DataFrames
    combined_df = pd.concat([bbg_df_news, bbg_df_finance, nonbbg_df], ignore_index=True).drop_duplicates(
        subset=["Ticker"],
        keep="first",
    )

    return combined_df


def build_search_company_df(context: ProjectContext):

    # Bloomberg TOP_N companies
    bbg_df_news = context.news_metric_df.head(TOP_N)
    bbg_df_finance = context.financial_metric_df[
        (context.financial_metric_df["Stock_3M"] <= STOCK_3M_THRESHOLD)
        | (context.financial_metric_df["Relative_3M"] <= RELATIVE_3M_THRESHOLD)
        | (context.financial_metric_df["Stock_6M"] <= STOCK_6M_THRESHOLD)
        | (context.financial_metric_df["Relative_6M"] <= RELATIVE_6M_THRESHOLD)
    ].copy()

    # Non-Bloomberg companies with raw news
    companies_with_news = set(context.raw_news_df["CompanyName"].unique())

    nonbbg_df = context.nonbbg_companies_df[
        context.nonbbg_companies_df["CompanyName"].isin(companies_with_news)
    ]

    # Combine candidates
    combined_df = pd.concat(
        [bbg_df_news, bbg_df_finance, nonbbg_df],
        ignore_index=True,
    ).drop_duplicates(
        subset=["Ticker"],
        keep="first",
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
