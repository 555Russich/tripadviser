# for working with Microsoft Excel documents
import openpyxl
# logs instead of prints
import logging
# for creating .xml file
import xml.etree.ElementTree as ET

from constants import (
    URL,
    OUTPUT_EXTENSION,
    FILEPATH,
    MAX_RESTAURANTS_COUNT,
    MAX_REVIEWS_PER_RESTAURANT,
    APPEND_FILE
)


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

        # if we are here, replacing (or creating new) file
        if OUTPUT_EXTENSION == '.xlsx':
            # creating workbook
            wb = openpyxl.Workbook()
            # append first row to workbook
            wb.active.append(['Output', 'Restaurant ID', 'Value 1', 'Value 2', 'Value 3'])
            # save changes to file
            wb.save(FILEPATH)
        elif OUTPUT_EXTENSION == '.xml':
            # define root element
            root = ET.Element('data')
            # define tree and set root element
            tree = ET.ElementTree(root)
            # save changes to file
            tree.write(FILEPATH, encoding='utf-8')

    else:
        logging.error(f'{APPEND_FILE=}\nExpected variable APPEND_FILE with type bool')
        exit()


def to_excel(restaurant_data: dict) -> None:
    """ Appending restaurant data to existing xlsx.
     File must exist because it's creating while checking APPEND_FILE
     """

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


def to_xml(restaurant_data: dict) -> None:
    """ Appending restaurant data to existing xml.
     File must exist because it's creating while checking APPEND_FILE.
     Replace spaces in tag names. Also replace newlines as spaces in reviews texts
     """

    # parse existing file
    tree = ET.parse(FILEPATH)
    # get root "data" tag
    root = tree.getroot()
    # define tag "restaurant"
    restaurant_tag = ET.SubElement(root, 'restaurant')

    for key, value in restaurant_data.items():
        # replace spaces with underscores
        key = '_'.join(key.split())
        # create child under tag "restaurant"
        child_1 = ET.SubElement(restaurant_tag, key)
        if key == 'hours':
            # iterating over hours dict where weekday is key and time range is value
            for weekday, times_ranges in restaurant_data['hours'].items():
                for time_range in times_ranges:
                    # create tag "weekday" under tag "hours"
                    child_2 = ET.SubElement(child_1, weekday)
                    # join list of timeranges
                    child_2.text = ' - '. join(time_range)
        elif key == 'reviews':
            # iterate over every review collected for this restaurant
            for id_review in restaurant_data['reviews']:
                # create child review under tag "reviews"
                child_2 = ET.SubElement(child_1, 'review')
                # create child tag "id" under tag "review"
                child_3 = ET.SubElement(child_2, 'id')
                child_3.text = id_review
                # iterate over keys and values for this review
                for key_review, value_review in restaurant_data['reviews'][id_review].items():
                    # replace spaces as underscores
                    key_review = key_review.replace(' ', '_')
                    # create child tag under tag "review"
                    child_3 = ET.SubElement(child_2, key_review)
                    # replace newlines for not breaking xml structure
                    child_3.text = value_review.replace('\n', ' ')
        else:
            # if value is just str, append it
            child_1.text = value

    # set indent as "tab"
    ET.indent(tree, space='\t')
    # write changes to file
    tree.write(FILEPATH, encoding='utf-8')
