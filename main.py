import time
import logging
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager

from my_logging import get_logger
from out_methods import to_excel
from constants import (
    URL,
    MAX_RESTAURANTS_COUNT,
    MAX_REVIEWS_PER_RESTAURANT,
    OUTPUT_EXTENSION,

    IS_HEADLESS,
    WAIT_IMPLICITLY,

    SLEEP_SEARCH,
    SLEEP_RESTAURANT,
    SLEEP_REVIEWS_PAGE,
    SLEEP_REVIEW_INFO,
    SLEEP_WAIT_LOADING_TAG,

    WAIT_IS_LAST_PAGE,
    WAIT_RESTAURANT_NAME,
    WAIT_MENU_URL,
    WAIT_AVATAR,
    WAIT_CLOSE_REVIEWER_INFO,
    WAIT_TRANSLATION_TEXT,
    WAIT_CLOSE_TRANSLATION,

    TIMEOUT_REVIEWER_INFO,


    A_RESTAURANTS_HREFS,
    A_NEXT_SEARCH_PAGE,
    SPAN_IS_LAST_SEARCH_PAGE,
    A_NEXT_REVIEWS_PAGE,

    A_MENU,
    B_RATING_NUMBER,
    H1_NAME,
    BUTTON_POPUP_SCHEDULE,
    DIVS_SCHEDULE,
    SVG_RESTAURANT_RATING,

    DIVS_REVIEWS,
    SPAN_LANGUAGE_FILTER_ALL,
    INPUT_LANGUAGE_FILTER_ALL,
    DIV_AVATAR,
    DIV_LOADING_LIST_REVIEWS,
    DIV_LOADING_REVIEWER_INFO,
    DIV_ID_USER,
    H3_USERNAME,
    SPAN_COUNT_CONTRIBUTIONS,
    SPAN_EXCELLENT_REVIEWS,
    DIV_CLOSE_REVIEWER_INFO,
    SPAN_SHOW_MORE,
    P_REVIEW_TEXT,
    DIV_DATE_VISIT,
    SPAN_TRANSLATE,
    DIV_TRANSLATION,
    DIV_CLOSE_TRANSLATION,

)


def check_input_values():
    """ Check input variables """

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


def get_driver() -> webdriver.Chrome:
    """ Define settings, driver path using webdriver-manager, initialize Chrome driver"""
    
    # get chrome options object to add options
    options = webdriver.ChromeOptions()
    # disable web driver mode
    options.add_argument('--disable-blink-features=AutomationControlled')
    # headless mode
    options.headless = IS_HEADLESS
    # maximize window
    options.add_argument('--start-maximized')
    # get driver path using webdriver-manager
    driver_path = ChromeDriverManager().install()
    # initialize chrome webdriver
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    # set implicitly wait
    driver.implicitly_wait(WAIT_IMPLICITLY)
    return driver


def get_urls_restaurants(driver: webdriver.Chrome) -> list[str]:
    """ Collect restaurants urls from search page """

    # define list which will be returned with restaurants urls
    urls_restaurants = []
    # define page number just to log
    page = 1
    while True:
        # sleep
        time.sleep(SLEEP_SEARCH)
        # get count of collected urls to compare after finding elements
        count_urls_before = len(urls_restaurants)

        # while FIRST search page loading, first located list of restaurants that we needed,
        # after that list is loading "Delivery Available", "Outdoor Seating Available" etc...
        # so first we got needed elements, but after other elements loading,
        # location for list of restaurants changes, and we need to find them again
        # p.s. this extra list with "Delivery..." and others only on first search page
        try:
            # iterating over tags <a> which contains hrefs to restaurants
            for tag_a in driver.find_elements(*A_RESTAURANTS_HREFS):
                # compare count of restaurants with constant value
                if len(urls_restaurants) == MAX_RESTAURANTS_COUNT:
                    return urls_restaurants

                # extract href attribute
                url_to_restaurant = tag_a.get_attribute('href')
                # append href to list if it's not in it already
                if url_to_restaurant not in urls_restaurants:
                    urls_restaurants.append(url_to_restaurant)
        except StaleElementReferenceException:
            # elements changed position on the DOM
            pass

        # check if we collected any new urls. This solution to avoid especially configured
        # time.sleep() value. Waits until any not seen elements will be located on search page
        if count_urls_before == len(urls_restaurants):
            continue
        logging.info(f'{page=}. Collected {len(urls_restaurants)} restaurants urls')

        try:
            # explicit wait of element until page loads
            WebDriverWait(driver, timeout=WAIT_IS_LAST_PAGE).until(
                ec.presence_of_element_located(SPAN_IS_LAST_SEARCH_PAGE)
            )
            # if page is last return list of urls
            return urls_restaurants
        except TimeoutException:
            # click the button next page search result
            driver.find_element(*A_NEXT_SEARCH_PAGE).click()
            # increment page number
            page += 1


def collect_all_restaurant_data(driver: webdriver.Chrome,
                                url: str,
                                keys: list[str] = None,
                                values: list[list[str]] = None
                                ) -> tuple[list[str], list[list[str]]]:
    """ Load restaurant url and collect all restaurant data.
    Nested functions will fill keys and values lists.
    """

    # if keys and values was not pass as args, define new lists
    if not keys and not values:
        keys = []
        values = []

    # get restaurant ID using regular expression
    id_restaurant = re.search(r'(?<=-d)\d+(?=-)', url).group(0)

    # load restaurant page
    driver.get(url)
    # sleep until restaurant page loading
    time.sleep(SLEEP_RESTAURANT)

    def get_restaurant_info():
        """ Load restaurant page and collect information about restaurant """

        # wait until restaurant <h1> tag with name is located on page.
        # expecting if name of restaurant is located, then other elements located too
        # here is no data appending to keep order in lists, just waiting until name is located
        WebDriverWait(driver, timeout=WAIT_RESTAURANT_NAME).until(
            ec.presence_of_element_located(H1_NAME)
        )

        # rating number in search
        try:
            rating_number = driver.find_element(*B_RATING_NUMBER).text
            keys.append('number')
            values.append([id_restaurant, rating_number])
        except NoSuchElementException:
            pass

        # name of restaurant
        try:
            name = driver.find_element(*H1_NAME).text
            keys.append('name')
            values.append([id_restaurant, name])
        except NoSuchElementException:
            pass

        # restaurant url
        keys.append('URL')
        values.append([id_restaurant, URL])

        # url for menu
        try:
            # attribute href appending to <a> after some time
            a_menu = WebDriverWait(driver, timeout=WAIT_MENU_URL).until(
                ec.element_to_be_clickable(A_MENU)
            )
            url_menu = a_menu.get_attribute('href')
            keys.append('menu')
            values.append([id_restaurant, url_menu])
        except TimeoutException:
            pass

        is_schedule_exists = False
        # get working hours
        try:
            # press button to get full schedule
            driver.find_element(*BUTTON_POPUP_SCHEDULE).click()
            is_schedule_exists = True
        except NoSuchElementException:
            pass

        if is_schedule_exists:
            # iterate over every div with hours in schedule
            for div_working_hours in driver.find_elements(*DIVS_SCHEDULE):
                # split str by "\n", put in weekday first value and others in times_ranges
                weekday, *times_ranges = div_working_hours.text.splitlines()
                # getting only Sun and Sat values
                if weekday.lower() in ('sun', 'sat', 'вс', 'cб'):
                    # iterating over times_ranges (restaurant may close and open multiple times in one day)
                    for time_range in times_ranges:
                        # split every time_range from open time to close time
                        parts_time_range = time_range.split(' - ')
                        keys.append('hours')
                        values.append([id_restaurant, weekday, *parts_time_range])
            # close schedule
            driver.find_element(*BUTTON_POPUP_SCHEDULE).click()

        # restaurant rating
        try:
            restaurant_rating = driver.find_element(*SVG_RESTAURANT_RATING).get_attribute('aria-label')
            keys.append('restaurant rating')
            values.append([id_restaurant, restaurant_rating])
        except NoSuchElementException:
            pass

    def get_reviews_info():
        """ Collect reviews for this restaurant. Append values to already existing lists """

        page = 1
        reviews_per_restaurant = 0
        while True:
            # check if langauge filter was selected to ALL languages
            if not driver.find_element(*INPUT_LANGUAGE_FILTER_ALL).is_selected():
                # change language filter to all
                driver.find_element(*SPAN_LANGUAGE_FILTER_ALL).click()
                # mini-sleep to wait div loading located on page
                time.sleep(SLEEP_WAIT_LOADING_TAG)
                # wait until reviews block is loading after apply filter

            # same algorithm for waiting after new page of reviews, also for filters applying
            while True:
                div_loading = driver.find_element(*DIV_LOADING_LIST_REVIEWS)
                # when loading finished, <div style="display: none;"> or ''
                # logging.info(f'{div_loading.get_attribute("style")=}')
                if div_loading.get_attribute('style') in ('display: none;', ''):
                    break

            # sleep while reviews page loading
            time.sleep(SLEEP_REVIEWS_PAGE)

            # define counter to log how many reviews collected
            reviews_from_page = 0
            # iterate over every div review on page
            for div_review in driver.find_elements(*DIVS_REVIEWS):
                # check if max reviews for restaurant already collected
                if MAX_REVIEWS_PER_RESTAURANT == reviews_per_restaurant:
                    logging.info(f'Collected {reviews_per_restaurant} reviews for {id_restaurant=}.'
                                 f' from {page=} new reviews {reviews_from_page}')
                    return

                # scroll to reviewer avatar
                ActionChains(driver).move_to_element(
                    div_review.find_element(*DIV_AVATAR)
                ).perform()
                # click on reviewer avatar. WebDriverWait takes here div_review
                # to do relative search of DIV_AVATAR
                WebDriverWait(div_review, timeout=WAIT_AVATAR).until(
                    ec.element_to_be_clickable(DIV_AVATAR)
                ).click()
                # sleep until user info loading
                time.sleep(SLEEP_REVIEW_INFO)

                # wait until reviewer info loads
                time.sleep(SLEEP_WAIT_LOADING_TAG)
                timer_reviewer_info = time.time()
                while time.time() - timer_reviewer_info < TIMEOUT_REVIEWER_INFO:
                    try:
                        driver.find_element(*DIV_LOADING_REVIEWER_INFO)
                    except NoSuchElementException:
                        break
                else:
                    driver.refresh()

                # user id from <div data-reviewid="some_id">
                id_user = div_review.find_element(*DIV_ID_USER).get_attribute('data-reviewid')

                # username from <h3>
                username = div_review.find_element(*H3_USERNAME).text
                keys.append('username')
                values.append([id_restaurant, id_user, username])

                # count of reviews from this user
                count_reviews_user = driver.find_element(*SPAN_COUNT_CONTRIBUTIONS).text
                # get only numeric value
                count_reviews_user = count_reviews_user.split()[0]
                keys.append('countsReview')
                values.append([id_restaurant, id_user, count_reviews_user])

                # count of excellent reviews from this user
                try:
                    count_excellent_reviews = driver.find_element(*SPAN_EXCELLENT_REVIEWS).text
                    # count_excellent_reviews = count_excellent_reviews.strip()
                    keys.append('countExcellent')
                    values.append([id_restaurant, id_user, count_excellent_reviews])
                except NoSuchElementException:
                    pass

                # close the reviewer info <span> overlay
                WebDriverWait(driver, timeout=WAIT_CLOSE_REVIEWER_INFO).until(
                    ec.element_to_be_clickable(DIV_CLOSE_REVIEWER_INFO)
                ).click()

                def count_words_in_span_show_more():
                    """ Get words count in SPAN_SHOW_MORE. If text value of tag contains 2 words,
                     there is 'More' or 'Еще', otherwise there is 'Show less' or 'Показать меньше'
                    """
                    span_show_more = div_review.find_element(*SPAN_SHOW_MORE)
                    return len(span_show_more.text.split())

                # check is button "show more" exists?
                try:
                    div_review.find_element(*SPAN_SHOW_MORE)
                    is_button_show_more_exits = True
                except NoSuchElementException:
                    is_button_show_more_exits = False

                if is_button_show_more_exits and count_words_in_span_show_more() == 1:
                    # press button "MORE" to show all text of ALL reviews on this page
                    div_review.find_element(*SPAN_SHOW_MORE).click()
                    # wait until text fully loaded
                    while True:
                        try:
                            if count_words_in_span_show_more() == 2:
                                break
                        except (NoSuchElementException, StaleElementReferenceException):
                            continue

                # text of review
                text = div_review.find_element(*P_REVIEW_TEXT).text
                keys.append('review text')
                values.append([id_restaurant, id_user, text])

                # date of visit
                date_of_visit = div_review.find_element(*DIV_DATE_VISIT).text
                keys.append('date of visit')
                values.append([id_restaurant, id_user, date_of_visit])

                # translation
                try:
                    # click button "Google Translate"
                    div_review.find_element(*SPAN_TRANSLATE).click()
                    is_translation_exists = True
                    # sleep to wait loading tag is appeared on page
                    time.sleep(SLEEP_WAIT_LOADING_TAG)
                except NoSuchElementException:
                    is_translation_exists = False

                if is_translation_exists:
                    # while loading tag is located on page, running through loop
                    while True:
                        try:
                            driver.find_element(*DIV_LOADING_REVIEWER_INFO)
                        except NoSuchElementException:
                            # sleep after loading finishes to ,
                            time.sleep(SLEEP_WAIT_LOADING_TAG)
                            break

                    # getting translated text of review
                    text_translation = WebDriverWait(driver, timeout=WAIT_TRANSLATION_TEXT).until(
                        ec.presence_of_element_located(DIV_TRANSLATION)
                    ).text
                    keys.append('translation')
                    values.append([id_restaurant, id_user, text_translation])

                    # close overlay with translation
                    WebDriverWait(driver, timeout=WAIT_CLOSE_TRANSLATION).until(
                        ec.element_to_be_clickable(DIV_CLOSE_TRANSLATION)
                    ).click()

                # counters
                reviews_from_page += 1
                reviews_per_restaurant += 1

            # append data to excel
            to_excel(keys, values)
            logging.info(f'{reviews_per_restaurant} reviews for {id_restaurant=}.'
                         f' from {page=} new reviews {reviews_from_page}')

            # moving to button next page
            ActionChains(driver).move_to_element(
                driver.find_element(*A_NEXT_REVIEWS_PAGE)
            ).perform()
            # if A_NEXT_REVIEWS_PAGE has class="disabled" it is last page
            if driver.find_element(*A_NEXT_REVIEWS_PAGE).is_enabled():
                # click to load new page
                driver.find_element(*A_NEXT_REVIEWS_PAGE).click()
                # page counter
                page += 1
            else:
                break

    get_restaurant_info()
    get_reviews_info()
    return keys, values


def collect_data():
    check_input_values()
    driver = get_driver()
    try:
        driver.get(URL)
        urls_restaurants = get_urls_restaurants(driver)
        logging.info(f'Total collected {len(urls_restaurants)} restaurant urls')

        for i, url_restaurant in enumerate(urls_restaurants):
            logging.info(f'{i+1}/{len(urls_restaurants)} START scrapping {url_restaurant}')
            collect_all_restaurant_data(driver, url_restaurant)
            logging.info(f'{i+1}/{len(urls_restaurants)} END scrapping {url_restaurant=}')
        logging.info('\n')

    except Exception as ex:
        logging.error(ex, exc_info=True)
        driver.save_screenshot('debug.png')
        time.sleep(999)
    finally:
        driver.quit()


# Check if file is running "directly"
if __name__ == '__main__':
    # get own logger
    get_logger('scrapper.log')
    # run main function
    collect_data()
