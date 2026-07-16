import pandas as pd
import logging
import os

from pathlib import Path
from openpyxl.styles import Alignment
from numbers import Number


logger = logging.getLogger(__name__)


def load_from_excel(excel_file, sheet_name=None):
    if not Path(excel_file).exists():
        return pd.DataFrame()
    return pd.read_excel(excel_file, sheet_name=sheet_name)


def export_to_excel(
    data: pd.DataFrame | dict[str, pd.DataFrame],
    file_path: Path | str,
    sheet_name="Sheet1",
):
    file_path = Path(file_path)
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        if isinstance(data, pd.DataFrame):
            data = {sheet_name: data}

        with pd.ExcelWriter(
            file_path,
            engine="openpyxl",
        ) as writer:
            for sheet_name, df in data.items():
                df = format_dataframe(df)

                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

                worksheet = writer.sheets[sheet_name]

                format_worksheet(worksheet)

    except PermissionError:
        logger.exception(f"Excel file is open: {file_path}")
        raise


def format_worksheet(ws):
    for column in ws.columns:
        name = column[0].value
        wrap = name != "Url"

        for cell in column[1:]:
            cell.alignment = Alignment(
                wrap_text=wrap,
                vertical="top",
            )

            if isinstance(cell.value, Number):
                if "Ratio" in name:
                    cell.number_format = "0.00%"
                else:
                    cell.number_format = "0.###"

            if name == "Url" and cell.value:
                cell.hyperlink = str(cell.value)
                cell.style = "Hyperlink"

        if name == "CompanyName":
            width = 30

        elif name in ["Title", "Reason", "TitleCN", "ReasonCN", "Summary"]:
            width = 40

        elif name == "Url":
            width = 70

        else:
            width = 10

        ws.column_dimensions[column[0].column_letter].width = width


def format_dataframe(df):

    df = df.copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

    return df
