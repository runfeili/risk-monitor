from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from utils.date_utils import TimePeriod


@dataclass
class FilePaths:
    input: Path
    output_dir: Path
    financial_metric: Path
    news_metric: Path
    raw_news: Path
    risk_news: Path
    llm_news: Path
    report: Path


@dataclass
class ProjectContext:
    period: TimePeriod
    paths: FilePaths
    bbg_companies_df: pd.DataFrame
    nonbbg_companies_df: pd.DataFrame
    financial_metric_df: pd.DataFrame | None = None
    news_metric_df: pd.DataFrame | None = None
    raw_news_df: pd.DataFrame | None = None
    risk_news_df: pd.DataFrame | None = None
    llm_news_df: pd.DataFrame | None = None
    spider_company_df: pd.DataFrame | None = None
    search_company_df: pd.DataFrame | None = None