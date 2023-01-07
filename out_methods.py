from pathlib import Path

import openpyxl

from constants import OUTPUT_FILEPATH, OUTPUT_EXTENSION


def to_excel(keys: list[str], values: list[list[str]]):
    filepath = Path(OUTPUT_FILEPATH).with_suffix(OUTPUT_EXTENSION)
    if not filepath.exists():
        wb = openpyxl.Workbook()
        wb.active.append(['Output', 'Restaurant ID', 'Value 1', 'Value 2', 'Value 3'])
    else:
        wb = openpyxl.load_workbook(filepath)

    for i in range(len(keys)):
        row = [keys[i]] + values[i]
        wb.active.append(row)

    wb.save(filepath)

