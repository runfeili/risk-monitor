import logging
import pandas as pd
from tqdm import tqdm
from configs import SEARCH_PROVIDER
from context import ProjectContext
from llm.llm_agent import LLMAgent
from llm.prompts import build_news_search_prompt
from utils.excel_utils import export_to_excel, load_from_excel

logger = logging.getLogger(__name__)


class NewsSearcher:
    def __init__(self):
        self.agent = LLMAgent(
            provider=SEARCH_PROVIDER,
        )

    def search_news(
        self,
        company_df: pd.DataFrame,
        start_date,
        end_date,
        output_file,
    ) -> pd.DataFrame:

        result_df = pd.DataFrame()

        if output_file.exists():
            result_df = load_from_excel(
                output_file,
                sheet_name="LlmNews",
            )

            logger.info(
                "Loaded existing LLM news: %d records.",
                len(result_df),
            )

        searched_companies = (
            set(result_df["CompanyName"].unique()) if not result_df.empty else set()
        )

        companies = [
            c for c in company_df["CompanyName"] if c not in searched_companies
        ]

        total = len(companies)
        batch_size = 5
        logger.info(
            "Searching news for %d companies(batch-size:%d).",
            total,
            batch_size,
        )

        for i in tqdm(
            range(0, len(companies), batch_size),
            desc="Searching News Using LLM",
        ):
            batch_companies = companies[i : i + batch_size]

            news = self.search_batch(
                batch_companies,
                start_date,
                end_date,
            )

            if news:
                batch_df = pd.DataFrame(news)

                result_df = pd.concat(
                    [
                        result_df,
                        batch_df,
                    ],
                    ignore_index=True,
                )

                export_to_excel(
                    data=result_df,
                    file_path=output_file,
                    sheet_name="LlmNews",
                )

        logger.info(
            "LLM news search completed. Total records: %d",
            len(result_df),
        )

        return result_df

    def search_batch(
        self,
        companies,
        start_date,
        end_date,
    ):

        prompt = build_news_search_prompt(
            companies=companies,
            start_date=start_date.strftime("%Y/%m/%d"),
            end_date=end_date.strftime("%Y/%m/%d"),
        )

        res = self.agent.generate_json(
            prompt,
            use_search=True,
            temperature=0,
        )

        return res


    def run(
        self,
        context: ProjectContext,
        company_df: pd.DataFrame,
        force_refresh,
    ):

        if not force_refresh:
            logger.info("Loading LLM news...")
            return load_from_excel(
                context.paths.llm_news,
                sheet_name="LlmNews",
            )

        llm_news_df = self.search_news(
            company_df,
            start_date=context.period.analysis_start_date,
            end_date=context.period.analysis_end_date,
            output_file=context.paths.llm_news,
        )

        return llm_news_df
