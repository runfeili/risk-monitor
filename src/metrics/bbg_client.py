from datetime import datetime
from configs import NEWS_FIELDS, FINANCIAL_FIELDS
from context import ProjectContext
from metrics.news_metrics import calc_news_metrics
from metrics.financial_metrics import calc_financial_metrics
from utils.excel_utils import export_to_excel, load_from_excel
from utils.network_utils import check_bbg_connection
import blpapi
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BloombergClient:
    def __init__(self, host="localhost", port=8194):

        self.session_options = blpapi.SessionOptions()
        self.session_options.setServerHost(host)
        self.session_options.setServerPort(port)
        self.session_options.setConnectTimeout(1000)
        self.session_options.setServiceCheckTimeout(1000)
        self.session = blpapi.Session(self.session_options)

        if not check_bbg_connection():
            raise RuntimeError(
                "Bloomberg unavailable. Please start and login to Bloomberg Terminal."
            )

        if not self.session.start():
            raise Exception(
                "Bloomberg unavailable. Please start and login to Bloomberg Terminal."
            )

        if not self.session.openService("//blp/refdata"):
            raise Exception(
                "Bloomberg unavailable. Please start and login to Bloomberg Terminal."
            )

        self.service = self.session.getService("//blp/refdata")

    def get_historical_data(
        self,
        tickers: list[str],
        fields: list[str],
        start_date: datetime,
        end_date: datetime,
        log=True,
    ):

        request = self.service.createRequest("HistoricalDataRequest")

        for ticker in tickers:
            request.append("securities", ticker)
        for field in fields:
            request.append("fields", field)

        request.set("startDate", start_date.strftime("%Y%m%d"))
        request.set("endDate", end_date.strftime("%Y%m%d"))

        # Set periodicity to DAILY to get daily data
        request.set("periodicitySelection", "DAILY")

        self.session.sendRequest(request)

        results = {}
        missing_tickers = []

        while True:
            event = self.session.nextEvent()

            for msg in event:
                if not msg.hasElement("securityData"):
                    continue

                security_data = msg.getElement("securityData")
                ticker = security_data.getElementAsString("security")
                field_data = security_data.getElement("fieldData")

                records = []

                for i in range(field_data.numValues()):
                    row = field_data.getValueAsElement(i)

                    record = {}

                    if row.hasElement("date"):
                        record["date"] = pd.to_datetime(
                            str(row.getElementAsDatetime("date"))
                        )

                    for field in fields:
                        if row.hasElement(field):
                            record[field] = row.getElementAsFloat(field)
                        else:
                            record[field] = None
                    records.append(record)

                df = pd.DataFrame(records)

                required_cols = [
                    "date",
                    *fields,
                ]

                for col in required_cols:
                    if col not in df.columns:
                        df[col] = None

                df = df[required_cols]

                if df.empty:
                    missing_tickers.append(ticker)
                    logger.debug(f"{ticker}: no data returned.")

                else:
                    df = df.sort_values("date").reset_index(drop=True)
                    logger.debug(f"{ticker}: {len(df)} rows loaded.")

                results[ticker] = df

            if event.eventType() == blpapi.Event.RESPONSE:
                break

        loaded_count = len(tickers) - len(missing_tickers)

        if log:
            logger.info(
                f"Loaded bloomberg data for "
                f"{loaded_count}/{len(tickers)} "
                f"tickers "
                f"from {start_date:%Y-%m-%d} "
                f"to {end_date:%Y-%m-%d}."
            )

        if missing_tickers:
            logger.warning(f"Missing data for {len(missing_tickers)} tickers.")
            logger.debug(
                "Missing tickers: ",
                "\n".join(f"  - {ticker}" for ticker in missing_tickers),
            )

        return results

    def get_reference_data(
        self,
        tickers: list[str],
        fields: list[str],
        overrides: dict[str, str] | None = None,
    ):
        request = self.service.createRequest("ReferenceDataRequest")

        for ticker in tickers:
            request.append("securities", ticker)

        for field in fields:
            request.append("fields", field)

        if overrides:
            override_element = request.getElement("overrides")
            for field_id, value in overrides.items():
                item = override_element.appendElement()
                item.setElement("fieldId", field_id)
                item.setElement("value", value)

        self.session.sendRequest(request)

        results = {}

        while True:
            event = self.session.nextEvent()

            for msg in event:
                if not msg.hasElement("securityData"):
                    continue

                security_array = msg.getElement("securityData")

                for i in range(security_array.numValues()):
                    security = security_array.getValueAsElement(i)

                    ticker = security.getElementAsString("security")
                    field_data = security.getElement("fieldData")

                    row = {}

                    for field in fields:
                        if field_data.hasElement(field):
                            elem = field_data.getElement(field)

                            if elem.isNull():
                                row[field] = None
                            else:
                                try:
                                    row[field] = elem.getValueAsFloat()
                                except Exception:
                                    row[field] = elem.getValueAsString()
                        else:
                            row[field] = None

                    results[ticker] = row

            if event.eventType() == blpapi.Event.RESPONSE:
                break

        return (
            pd.DataFrame.from_dict(results, orient="index")
            .reset_index()
            .rename(columns={"index": "Ticker"})
        )

    def run_news(
        self,
        context: ProjectContext,
    ):
        if context.paths.news_metric.exists():
            news_metric_df = load_from_excel(
                context.paths.news_metric, sheet_name="NewsMetrics"
            )
            if not news_metric_df.empty:
                logger.info("Loading Bloomberg news metrics...")
                return news_metric_df

        tickers = context.bbg_companies_df["Ticker"].dropna().tolist()
        analysis_data = self.get_historical_data(
            tickers=tickers,
            fields=NEWS_FIELDS,
            start_date=context.period.analysis_start_date,
            end_date=context.period.analysis_end_date,
        )
        baseline_data = self.get_historical_data(
            tickers=tickers,
            fields=NEWS_FIELDS,
            start_date=context.period.baseline_start_date,
            end_date=context.period.baseline_end_date,
        )
        results_df = calc_news_metrics(analysis_data, baseline_data)

        # Merge with company_list to show company names
        news_metric_df = results_df.merge(
            context.bbg_companies_df,
            on="Ticker",
            how="left",
        )
        cols = ["Ticker", "CompanyName"]
        cols += [col for col in news_metric_df.columns if col not in cols]
        news_metric_df = news_metric_df[cols]
        news_metric_df.drop(columns=["BloombergAvailable"])
        export_to_excel(
            data=news_metric_df,
            file_path=context.paths.news_metric, 
            sheet_name="NewsMetrics"
        )
        return news_metric_df

    def run_financial(
        self,
        context: ProjectContext,
    ):
        if context.paths.financial_metric.exists():
            financial_metric_df = load_from_excel(
                context.paths.financial_metric,
                sheet_name="FinancialMetrics",
            )
            if not financial_metric_df.empty:
                logger.info("Loading Bloomberg financial metrics...")
                return financial_metric_df

        tickers = context.bbg_companies_df["Ticker"].dropna().tolist()

        financial_data = self.get_reference_data(
            tickers=tickers,
            fields=FINANCIAL_FIELDS,
        )

        results_df = calc_financial_metrics(financial_data)

        financial_metric_df = results_df.merge(
            context.bbg_companies_df,
            on="Ticker",
            how="left",
        )

        cols = ["Ticker", "CompanyName"]
        cols += [col for col in financial_metric_df.columns if col not in cols]
        financial_metric_df = financial_metric_df[cols]

        financial_metric_df = financial_metric_df.drop(
            columns=["BloombergAvailable"],
            errors="ignore",
        )

        export_to_excel(
            data=financial_metric_df,
            file_path=context.paths.financial_metric,
            sheet_name="FinancialMetrics",
        )

        return financial_metric_df

    def _save_metric(
        self,
        results_df,
        company_df,
        output_path,
    ):
        metric_df = results_df.merge(
            company_df,
            on="Ticker",
            how="left",
        )

        cols = ["Ticker", "CompanyName"]
        cols += [c for c in metric_df.columns if c not in cols]
        metric_df = metric_df[cols]

        metric_df = metric_df.drop(
            columns=["BloombergAvailable"],
            errors="ignore",
        )

        export_to_excel(
            data=metric_df,
            file_path=output_path,
            sheet_name="Metrics",
        )

        return metric_df
