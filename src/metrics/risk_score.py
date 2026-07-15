def calc_risk_score(row):

    neg_spike_score = min(
        row["NegSpike"] / 5 * 100,
        100,
    )

    neg_ratio_score = row["NegRatio"] * 100

    news_spike_score = min(
        row["VolSpike"] / 5 * 100,
        100,
    )

    sentiment_score = (1 - row["Sentiment"]) * 50

    return (
        neg_spike_score * 0.4
        + neg_ratio_score * 0.3
        + news_spike_score * 0.2
        + sentiment_score * 0.1
    )