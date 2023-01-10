import openpyxl
import logging

from constants import (
    URL,
    OUTPUT_FILEPATH,
    OUTPUT_EXTENSION,
    FILEPATH,
    MAX_RESTAURANTS_COUNT,
    MAX_REVIEWS_PER_RESTAURANT,
    APPEND_FILE
)


def to_excel(restaurant_data: dict) -> None:
    if not FILEPATH.exists():
        wb = openpyxl.Workbook()
        wb.active.append(['Output', 'Restaurant ID', 'Value 1', 'Value 2', 'Value 3'])
    else:
        wb = openpyxl.load_workbook(FILEPATH)

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

    wb.save(FILEPATH)


def check_input_values():
    """ Check input variables """

    def check_user_answer(question: str) -> bool:
        new_file = input(f'{question}\nEnter answer: ')
        if new_file.lower() == 'y':
            return True
        elif new_file.lower() == 'n':
            exit()
        else:
            logging.error(f'Expected answer is "y" or "n" (yes or no)')

    # Check variable URL is object of str class and starts like link to tripadvisor
    if isinstance(URL, str):
        if URL.startswith('https://www.tripadvisor'):
            pass
        else:
            logging.error(f'{URL=}\nURL should be directing to tripadvisor domain.')
            exit()
    else:
        logging.error(f'{URL=}\nExpected variable URL with type str.')
        exit()

    # Check variable RESTAURANTS_COUNT is object of int class
    if not isinstance(MAX_RESTAURANTS_COUNT, int):
        logging.error(f'{MAX_RESTAURANTS_COUNT=}\nExpected variable RESTAURANTS_COUNT with type int.')
        exit()

    # Check variable MAX_REVIEWS_PER_RESTAURANT is object of int class
    if not isinstance(MAX_REVIEWS_PER_RESTAURANT, int):
        logging.error(f'{MAX_REVIEWS_PER_RESTAURANT=}\nExpected variable MAX_REVIEWS_PER_RESTAURANT with type int.')
        exit()

    # Check variable OUTPUT_EXTENSION is object of str and starts with dot
    if isinstance(OUTPUT_EXTENSION, str):
        if OUTPUT_EXTENSION.startswith('.'):
            if OUTPUT_EXTENSION in ('.xlsx', '.xml'):
                pass
            else:
                logging.error(f'{OUTPUT_EXTENSION=}\nExpected variable OUTPUT_EXTENSION would be ".xlsx" or ".xml"')
                exit()
        else:
            logging.error(f'{OUTPUT_EXTENSION=}\nExpected variable OUTPUT_EXTENSION starts with dot.')
            exit()
    else:
        logging.error(f'{OUTPUT_EXTENSION=}\nExpected variable OUTPUT_EXTENSION with type str.')
        exit()

    # check APPEND_FILE variable
    if isinstance(APPEND_FILE, bool):
        if APPEND_FILE:
            if not FILEPATH.exists():
                check_user_answer(f'File "{str(FILEPATH.absolute())}" does not exist. '
                                  f'Do you want to create new file?')
        else:
            if FILEPATH.exists():
                check_user_answer(f'File "{str(FILEPATH.absolute())}" already exists. Do you want to replace it?')
    else:
        logging.error(f'{APPEND_FILE=}\nExpected variable APPEND_FILE with type bool')
        exit()


if __name__ == '__main__':
    check_input_values()