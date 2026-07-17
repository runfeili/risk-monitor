import logging
import pandas as pd
from tqdm import tqdm
from configs import CLASSIFIER_PROVIDER
from context import ProjectContext
from llm.llm_agent import LLMAgent
from llm.prompts import build_news_classifier_prompt
from utils.excel_utils import export_to_excel, load_from_excel
from utils.llm_utils import calculate_batch_size


logger = logging.getLogger(__name__)


class NewsClassifier:
    def __init__(self):
        self.agent = LLMAgent(
            provider=CLASSIFIER_PROVIDER,
            usage_tag="classifier"
        )

    def classify_batch(
        self,
        news_df: pd.DataFrame,
    ) -> pd.DataFrame:
        news_records = []

        for i, (_, row) in enumerate(news_df.iterrows()):
            news_records.append(
                {
                    "id": i,
                    "company": row["CompanyName"],
                    "headline": row["Title"],
                }
            )

        prompt = build_news_classifier_prompt(news_records)

        res = self.agent.generate_json(prompt, use_search=False, temperature=0)

        rows = []

        for item in res:
            source_row = news_df.iloc[item["id"]]

            rows.append(
                {
                    "CompanyName": source_row["CompanyName"],
                    "Date": source_row["Date"],
                    "Category": item.get("category"),
                    "Severity": item.get("severity"),
                    "Title": source_row["Title"],
                    "TitleCN": item.get("title_cn"),
                    "Reason": item.get("reason"),
                    "ReasonCN": item.get("reason_cn"),
                    "Source": source_row["Source"],
                    "Url": source_row["Url"],
                }
            )

        return pd.DataFrame(rows)

    def classify_news(
        self,
        news_df: pd.DataFrame,
        context: ProjectContext,
    ):
        if news_df.empty:
            return pd.DataFrame()

        result_df = pd.DataFrame()

        total = len(news_df)

        batch_size = calculate_batch_size(total)
        logger.info(
            "Classifying %d news (batch-size:%d).",
            total,
            batch_size,
        )
        
        for start in tqdm(
            range(0, total, batch_size),
            desc="Classifying News",
            unit="batch",
        ):
            batch = news_df.iloc[start : start + batch_size]

            batch_result = self.classify_batch(batch)
            result_df = pd.concat(
                [
                    result_df,
                    batch_result,
                ],
                ignore_index=True,
            )

            result_df = result_df.drop_duplicates(subset=["CompanyName", "Title"])

            export_to_excel(
                data=result_df,
                file_path=context.paths.risk_news,
                sheet_name="RiskNews",
            )

        severity_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        result_df = (
            result_df.assign(
                SeverityOrder=result_df["Severity"].map(severity_order)
            )
            .sort_values(
                by=["SeverityOrder", "Date"],
                ascending=[True, False],
            )
            .drop(columns="SeverityOrder")
            .reset_index(drop=True)
        )
        severity_counts = result_df["Severity"].value_counts().to_dict()
        category_counts = result_df["Category"].value_counts().to_dict()

        logger.info(
            "News classification completed: identified %d relevant news.",
            len(result_df),
        )
        logger.info(f"Severity: {severity_counts}")
        logger.info(f"Category: {category_counts}")

        export_to_excel(
            data=result_df,
            file_path=context.paths.risk_news,
            sheet_name="RiskNews",
        )

        return result_df

    def run(
        self,
        context: ProjectContext,
        raw_news_df: pd.DataFrame,
        force_refresh=False,
    ):
        if not force_refresh:
            logger.info("Loading risk news...")
            risk_news_df = load_from_excel(
                context.paths.risk_news, sheet_name="RiskNews"
            )
            return risk_news_df

        risk_news_df = self.classify_news(raw_news_df, context)

        usage_stats = self.agent.provider.usage_stats["classifier"]
        logger.info("Total Gemini usage for classifier:")
        logger.info("%d requests | input=%d output=%d think=%d tool=%d total=%d", 
                    usage_stats["requests"], 
                    usage_stats["prompt_tokens"],
                    usage_stats["output_tokens"],
                    usage_stats["thoughts_tokens"],
                    usage_stats["tool_tokens"],
                    usage_stats["total_tokens"],
        )
        
        return risk_news_df
