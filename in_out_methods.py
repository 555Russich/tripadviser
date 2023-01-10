# for working with Microsoft Excel documents
import openpyxl
# logs instead of prints
import logging

from constants import (
    URL,
    OUTPUT_EXTENSION,
    FILEPATH,
    MAX_RESTAURANTS_COUNT,
    MAX_REVIEWS_PER_RESTAURANT,
    APPEND_FILE
)


def to_excel(restaurant_data: dict) -> None:
    # load workbook
    wb = openpyxl.load_workbook(FILEPATH)

    # extract id from dict
    id_restaurant = restaurant_data.pop('id')
    # iterate over items
    for key, value in restaurant_data.items():
        # value with "hours" key contain dict inside with weekdays as keys and working hours as list
        if key == 'hours':
            for weekday, times_ranges in restaurant_data['hours'].items():
                for time_range in times_ranges:
                    # define row
                    row = [key, id_restaurant, weekday, *time_range]
                    # append row to workbook
                    wb.active.append(row)
        elif key == 'reviews':
            # iterate over every review collected for this restaurant
            for id_review in restaurant_data['reviews']:
                # iterate over keys and values for this review
                for key_review, value_review in restaurant_data['reviews'][id_review].items():
                    # define row
                    row = [key_review, id_restaurant, id_review, value_review]
                    # append row to workbook
                    wb.active.append(row)
        else:
            # define row
            row = [key, id_restaurant, value]
            # append row to workbook
            wb.active.append(row)

    # save changes to workbook
    wb.save(FILEPATH)


def check_input_values():
    """ Check input variables """

    def check_user_answer(question: str) -> bool:
        """ Ask user question and exit program at all if answer is 'no' """

        new_file = input(f'{question}\nEnter answer: ')
        # answer will be checked in lower case
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
                logging.info(f'File "{str(FILEPATH.absolute())}" will be overwritten')
        else:
            if FILEPATH.exists():
                check_user_answer(f'File "{str(FILEPATH.absolute())}" already exists. Do you want to replace it?')
            else:
                logging.error(f'Can\'t start scrapping. File "{str(FILEPATH.absolute())}" does not exists '
                              f'and was not created')
                exit()
                
        wb = openpyxl.Workbook()
        wb.active.append(['Output', 'Restaurant ID', 'Value 1', 'Value 2', 'Value 3'])
        wb.save(FILEPATH)
            
    else:
        logging.error(f'{APPEND_FILE=}\nExpected variable APPEND_FILE with type bool')
        exit()


if __name__ == '__main__':
    check_input_values()