import pandas as pd
import logging
import os

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Alignment


logger = logging.getLogger(__name__)


def load_from_excel(excel_file, sheet_name=None):
    if not Path(excel_file).exists():
        return pd.DataFrame()
    return pd.read_excel(excel_file, sheet_name=sheet_name)
    

def export_to_excel(
    data,
    file_path,
):
    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        if isinstance(data, pd.DataFrame):
            data.to_excel(
                file_path,
                index=False,
            )

        elif isinstance(data, dict):
            with pd.ExcelWriter(
                file_path,
                engine="openpyxl",
            ) as writer:
                for sheet_name, df in data.items():
                    df.to_excel(
                        writer,
                        sheet_name=sheet_name,
                        index=False,
                    )

        else:
            raise TypeError("data must be DataFrame or dict[str, DataFrame]")

    except PermissionError:
        logger.exception(f"Excel file is open: {file_path}")
        raise

    wb = load_workbook(file_path)

    for ws in wb.worksheets:
        for col in ws.iter_cols():
            header = str(col[0].value)

            if header == "CompanyName":
                ws.column_dimensions[col[0].column_letter].width = 30
            elif header in ["Title","Reason", "TitleCN","ReasonCN", "Summary"]:
                ws.column_dimensions[col[0].column_letter].width = 40
            elif header == "Url":
                ws.column_dimensions[col[0].column_letter].width = 70
                for cell in col[1:]:
                    if not cell.value:
                        continue
                    cell.hyperlink = str(cell.value)
                    cell.style = "Hyperlink"
            
            for cell in col[1:]:
                cell.alignment = Alignment(
                    wrap_text=True,
                    vertical="center",
                )
                if not isinstance(cell.value, float):
                    continue
                if "Ratio" in header:
                    cell.number_format = "0.00%"
                else:
                    cell.number_format = "0.000"

    wb.save(file_path)

    return file_path


def check_output_files():

    files = []
    

    for file_path in files:
        file_path = Path(file_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not file_path.exists():
            continue

        try:
            os.rename(
                file_path,
                file_path,
            )

        except PermissionError:
            raise PermissionError(f"Please close Excel file: {file_path}")
