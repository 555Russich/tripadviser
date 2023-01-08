from pathlib import Path

import openpyxl

from constants import OUTPUT_FILEPATH, OUTPUT_EXTENSION


def to_excel(restaurant_data: dict) -> None:
    filepath = Path(OUTPUT_FILEPATH).with_suffix(OUTPUT_EXTENSION)
    if not filepath.exists():
        wb = openpyxl.Workbook()
        wb.active.append(['Output', 'Restaurant ID', 'Value 1', 'Value 2', 'Value 3'])
    else:
        wb = openpyxl.load_workbook(filepath)

    id_restaurant = restaurant_data.pop('id')
    for key, value in restaurant_data.items():
        if key == 'hours':
            for weekday, times_ranges in restaurant_data['hours'].items():
                for time_range in times_ranges:
                    row = [key, id_restaurant, weekday, *time_range]
                    wb.active.append(row)
        elif key == 'reviews':
            for id_review in restaurant_data['reviews']:
                for key_review, value_review in restaurant_data['reviews'][id_review].items():
                    row = [key_review, id_restaurant, id_review, value_review]
                    wb.active.append(row)
        else:
            row = [key, id_restaurant, value]
            wb.active.append(row)

    wb.save(filepath)
