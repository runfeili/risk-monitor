import pandas as pd


def calc_financial_metrics(
    company_df: pd.DataFrame,
    index_df: pd.DataFrame,
):
    if company_df.empty:
        return pd.DataFrame()

    company_df = company_df.copy()

    results_df = company_df.merge(
        index_df,
        on="Index",
        how="left",
    )

    results_df["EXCESS_DECLINE_3M"] = (
        results_df["CHG_PCT_3M"] - results_df["INDEX_CHG_PCT_3M"]
    ).fillna(0)

    results_df["EXCESS_DECLINE_6M"] = (
        results_df["CHG_PCT_6M"] - results_df["INDEX_CHG_PCT_6M"]
    ).fillna(0)

    results_df = results_df.sort_values(
        by=[
            "CHG_PCT_3M",
            "EXCESS_DECLINE_3M",
        ],
        ascending=[
            True,
            True,
        ],
    ).reset_index(drop=True)

    results_df = results_df.rename(
        columns={
            "CHG_PCT_3M": "Stock_3M",
            "INDEX_CHG_PCT_3M": "Benchmark_3M",
            "EXCESS_DECLINE_3M": "Relative_3M",
            "CHG_PCT_6M": "Stock_6M",
            "INDEX_CHG_PCT_6M": "Benchmark_6M",
            "EXCESS_DECLINE_6M": "Relative_6M",
        }
    )

    return results_df

