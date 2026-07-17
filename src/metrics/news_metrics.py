import pandas as pd
from metrics.risk_score import calc_risk_score
from config import PERIODICITY


def calc_news_metrics(
    week_data: dict[str, pd.DataFrame], 
    quarter_data: dict[str, pd.DataFrame]
):
    results = []

    for ticker, analysis_df in week_data.items():
        if analysis_df.empty:
            results.append(
                {
                    "Ticker": ticker,
                    "NegSpike": 0,
                    "NegRatio": 0,
                    "VolSpike": 0,
                    "Sentiment": 0,
                }
            )
            continue

        quarter_df = quarter_data.get(ticker)
        if quarter_df is None or quarter_df.empty:
            print(
                f"{ticker}: no quarterly data available, skipping baseline comparison."
            )
            continue

        analysis_metrics = get_analysis_metrics(analysis_df)

        baseline_metrics = get_baseline_metrics(
            quarter_df,
            analysis_df["date"].min(),
        )

        if not baseline_metrics:
            continue

        news_volume_spike = (
            analysis_metrics["news_count"] / baseline_metrics["baseline_news_count"]
            if baseline_metrics["baseline_news_count"] > 0
            else 0
        )

        negative_news_spike = (
            analysis_metrics["neg_count"] / baseline_metrics["baseline_neg_count"]
            if baseline_metrics["baseline_neg_count"] > 0
            else 0
        )

        results.append(
            {
                "Ticker": ticker,
                "NegSpike": negative_news_spike,
                "NegRatio": analysis_metrics["neg_ratio"],
                "VolSpike": news_volume_spike,
                "Sentiment": analysis_metrics["sentiment"],
            }
        )

    results_df = pd.DataFrame(results)
    results_df["RiskScore"] = results_df.apply(
        calc_risk_score,
        axis=1,
    )

    results_df = results_df.sort_values(
        "RiskScore",
        ascending=False,
    ).reset_index(drop=True)

    return results_df



def get_analysis_metrics(analysis_df: pd.DataFrame):
    analysis_df = analysis_df.fillna(0)

    news_count = analysis_df["NEWS_HEAT_PUB_DNUMSTORIES"].sum()

    neg_count = (
        analysis_df["NEWS_NEG_SENTIMENT_COUNT"].sum()
        + analysis_df["CHINESE_NEWS_NEG_SNTMNT_COUNT"].sum()
    )
    total_sentiment_count = (
        neg_count
        + analysis_df["NEWS_POS_SENTIMENT_COUNT"].sum()
        + analysis_df["CHINESE_NEWS_POS_SNTMNT_COUNT"].sum()
        + analysis_df["NEWS_NEUTRAL_SENTIMENT_COUNT"].sum()
        + analysis_df["CHINESE_NEWS_NEUTRL_SNTMNT_COUNT"].sum()
    )

    neg_ratio = neg_count / total_sentiment_count if total_sentiment_count > 0 else 0

    sentiment_values = []
    if "NEWS_SENTIMENT_DAILY_AVG" in analysis_df:
        sentiment_values.append(analysis_df["NEWS_SENTIMENT_DAILY_AVG"])
    if "CHINESE_NEWS_SENTMNT_DAILY_AVG" in analysis_df:
        sentiment_values.append(analysis_df["CHINESE_NEWS_SENTMNT_DAILY_AVG"])
    sentiment = pd.concat(sentiment_values).mean() if sentiment_values else None

    return {
        "news_count": news_count,
        "neg_count": neg_count,
        "total_sentiment_count": total_sentiment_count,
        "neg_ratio": neg_ratio,
        "sentiment": sentiment,
    }


def get_baseline_metrics(
    quarter_df: pd.DataFrame,
    period_start: pd.Timestamp,
):
    baseline_df = quarter_df[quarter_df["date"] < period_start].fillna(0)

    if baseline_df.empty:
        return {}

    freq = PERIODICITY[0].upper()
    num_periods = baseline_df["date"].dt.to_period(freq).nunique()

    avg_period_news = baseline_df["NEWS_HEAT_PUB_DNUMSTORIES"].sum() / num_periods

    avg_period_neg = (
        baseline_df["NEWS_NEG_SENTIMENT_COUNT"].sum()
        + baseline_df["CHINESE_NEWS_NEG_SNTMNT_COUNT"].sum()
    ) / num_periods


    return {
        "baseline_news_count": avg_period_news,
        "baseline_neg_count": avg_period_neg,
    }
