from datetime import datetime
from pathlib import Path

from context import FilePaths


def build_file_paths(
    input_dir: str | Path = Path("input"),
    output_root: str | Path = Path("output"),
) -> FilePaths:

    run_date = datetime.now().strftime("%Y%m%d")
    output_dir = Path(output_root) / run_date

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return FilePaths(
        company_list=input_dir / "company_list.xlsx",
        index_mapping=input_dir / "index_mapping.xlsx",
        output_dir=output_dir,
        financial_metric=output_dir / "financial_metrics.xlsx",
        news_metric=output_dir / "news_metrics.xlsx",
        raw_news=output_dir / "raw_news.xlsx",
        risk_news=output_dir / "risk_news.xlsx",
        llm_news=output_dir / "llm_news.xlsx",
        report=output_dir / "final_report.xlsx",
    )
