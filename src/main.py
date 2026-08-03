import logging
from context import ProjectContext
from llm.news_classifier import NewsClassifier
from llm.news_searcher import NewsSearcher
from utils.date_utils import build_period
from metrics.bbg_client import BloombergClient
from utils.path_utils import build_file_paths
from utils.excel_utils import export_to_excel, load_from_excel
from utils.logger import setup_logger
from spiders.news_spider import NewsSpider
from config import (
    ANALYSIS_LOOKBACK,
    BASELINE_LOOKBACK,
    PERIODICITY,
    RUN_LLM_NEWS_SEARCH,
    RUN_NEWS_CLASSIFIER
)
from utils.pipeline_utils import build_search_company_df, build_spider_company_df


logger = logging.getLogger(__name__)


def main():
    success = False

    try:
        setup_logger()
        logger.info(">>> RiskMonitor Started >>>")

        period = build_period(
            periodicity=PERIODICITY,
            analysis_lookback=ANALYSIS_LOOKBACK,
            baseline_lookback=BASELINE_LOOKBACK,
        )
        paths = build_file_paths()
        companies = load_from_excel(paths.company_list)
        bbg_companies_df = companies["bbg_avaliable"]
        bbg_companies_df["BloombergAvailable"] = True
        nonbbg_companies_df = companies["bbg_unavailable"]
        nonbbg_companies_df["BloombergAvailable"] = False

        context = ProjectContext(
            period=period,
            paths=paths,
            bbg_companies_df=bbg_companies_df,
            nonbbg_companies_df=nonbbg_companies_df,
        )

        bbg = BloombergClient()
        news_spider = NewsSpider()
        news_classifier = NewsClassifier()
        news_searcher = NewsSearcher()

        logger.info(
            f"Analyzing data from {context.period.analysis_start_date} to {context.period.analysis_end_date}."
        )
        context.news_metric_df = bbg.run_news(context=context)
        context.financial_metric_df = bbg.run_financial(context=context)

        context.spider_company_df = build_spider_company_df(context)
        context.raw_news_df = news_spider.run(
            context=context,
            company_df=context.spider_company_df,
        )

        context.risk_news_df = news_classifier.run(
            context=context,
            raw_news_df=context.raw_news_df,
            force_refresh=RUN_NEWS_CLASSIFIER,
        )

        context.search_company_df = build_search_company_df(context)
        context.llm_news_df = news_searcher.run(
            company_df=context.search_company_df,
            context=context,
            force_refresh=RUN_LLM_NEWS_SEARCH,
        )

        export_to_excel(
            {
                "NewsMetrics": context.news_metric_df,
                "FinancialMetrics": context.financial_metric_df,
                "RawNews": context.raw_news_df,
                "RiskNews": context.risk_news_df,
                "LlmNews": context.llm_news_df,
            },
            context.paths.report,
            disclaimer_path=context.paths.disclaimer,
        )
        logger.info(f"Result exported to: {context.paths.report}")

        success = True

    except Exception:
        logger.exception("Error occurred:")
        return

    finally:
        if success:
            logger.info("<<< RiskMonitor Finished <<<\n")
        else:
            logger.error("<<< RiskMonitor Failed <<<\n")


if __name__ == "__main__":
    main()
