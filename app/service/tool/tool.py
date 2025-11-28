import httpx
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment

CENTER_ALIGNED = Alignment(horizontal='center', vertical='center')


def auto_cells_width(sheet: Worksheet):
    for col in sheet.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        sheet.column_dimensions[col_letter].width = max_length + 4


def set_column_width(sheet: Worksheet, column_letter: str, width: int):
    sheet.column_dimensions[column_letter].width = width


def align_row_center(sheet: Worksheet, rows: list):
    for row_to_align in rows:
        for cell in sheet[row_to_align]:
            cell.alignment = CENTER_ALIGNED


def align_column_center(sheet: Worksheet, columns: list):
    for column_to_align in columns:
        for cell in sheet[column_to_align]:
            cell.alignment = CENTER_ALIGNED