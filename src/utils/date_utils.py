import logging

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

@dataclass
class TimePeriod:
    periodicity: str

    analysis_lookback: int
    baseline_lookback: int

    analysis_start_date: date
    analysis_end_date: date

    baseline_start_date: date
    baseline_end_date: date


def _subtract(
    end_date: date,
    periodicity: str,
    lookback: int,
) -> date:

    periodicity = periodicity.upper()

    if periodicity == "DAILY":
        return end_date - timedelta(days=lookback)

    elif periodicity == "WEEKLY":
        return end_date - timedelta(weeks=lookback)

    elif periodicity == "MONTHLY":
        return end_date - relativedelta(months=lookback)

    elif periodicity == "QUARTERLY":
        return end_date - relativedelta(months=3 * lookback)

    elif periodicity == "YEARLY":
        return end_date - relativedelta(years=lookback)

    raise ValueError(f"Unsupported periodicity: {periodicity}")


def build_period(
    periodicity: str,
    analysis_lookback: int,
    baseline_lookback: int,
    end_date: date | None = None,
) -> TimePeriod:

    if end_date is None:
        end_date = datetime.today().date()

    analysis_start = _subtract(
        end_date,
        periodicity,
        analysis_lookback,
    )

    baseline_start = _subtract(
        end_date,
        periodicity,
        baseline_lookback,
    )

    return TimePeriod(
        periodicity=periodicity,
        analysis_lookback=analysis_lookback,
        baseline_lookback=baseline_lookback,
        analysis_start_date=analysis_start,
        analysis_end_date=end_date,
        baseline_start_date=baseline_start,
        baseline_end_date=end_date,
    )
