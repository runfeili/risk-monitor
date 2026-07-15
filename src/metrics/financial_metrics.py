import pandas as pd

def calc_financial_metrics(df: pd.DataFrame):
    df = df.fillna(0)
    df = df.sort_values(
        "SALES_REV_TURN",
        ascending=False,
    ).reset_index(drop=True)

    return df
