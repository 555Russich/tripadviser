# for sleep and timeouts
import time
# for logging instead of uses prints
import logging
# regular expressions to get id_restaurant from URL
import re

# selenium driver
from selenium import webdriver
# Service to use webdriver-manager
from selenium.webdriver.chrome.service import Service
# explicit wait https://www.selenium.dev/documentation/webdriver/waits/#explicit-wait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
# for type hints
from selenium.webdriver.remote.webdriver import WebElement
# for scrolling web page
from selenium.webdriver.common.action_chains import ActionChains
# exceptions
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
# for auto installation of webdriver
from webdriver_manager.chrome import ChromeDriverManager

# logging customization
from my_logging import get_logger
# methods to handle input and output values
from in_out_methods import check_input_values, to_excel
from constants import (
    URL,
    MAX_RESTAURANTS_COUNT,
    MAX_REVIEWS_PER_RESTAURANT,

    IS_HEADLESS,
    WAIT_IMPLICITLY,

    SLEEP_SEARCH,
    SLEEP_RESTAURANT,
    SLEEP_REVIEWS_PAGE,
    SLEEP_REVIEW_INFO,
    SLEEP_WAIT_LOADING_TAG,
    SLEEP_DRIVER_REFRESH,

    WAIT_IS_LAST_PAGE,
    WAIT_RESTAURANT_NAME,
    WAIT_MENU_URL,
    WAIT_AVATAR,
    WAIT_USERNAME,
    WAIT_CLOSE_REVIEWER_INFO,
    WAIT_TRANSLATION_TEXT,
    WAIT_CLOSE_TRANSLATION,
    WAIT_CHANGE_FILTER,
    WAIT_PAGE_NUMBER,

    TIMEOUT_LOADING,

    TITLE,
    A_RESTAURANTS_HREFS,
    A_NEXT_SEARCH_PAGE,
    SPAN_IS_LAST_SEARCH_PAGE,
    A_NEXT_REVIEWS_PAGE,
    CURRENT_PAGE_NUMBER,

    A_MENU,
    B_RATING_NUMBER,
    H1_NAME,
    BUTTON_POPUP_SCHEDULE,
    DIVS_SCHEDULE,
    SVG_RESTAURANT_RATING,

    DIV_REVIEW_CONTAINER,
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
    DIV_CLOSE_TRANSLATION
)


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

    while True:
        # sleep
        time.sleep(SLEEP_SEARCH)
        # get count of collected urls to compare after finding elements
        count_urls_before = len(urls_restaurants)

        # if page is single there is no button for next page
        is_only_one_page, page = is_single_page(driver)

        # while FIRST search page loading, first located list of restaurants that we needed,
        # after that list is loading "Delivery Available", "Outdoor Seating Available" etc...
        # so first we got needed elements, but after other elements loaded,
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

        # if page is single return collected urls
        if is_only_one_page:
            return urls_restaurants

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


def collect_restaurant_data(driver: webdriver.Chrome,
                            url: str,
                            restaurant_data: dict = None
                            ) -> dict:
    """ Directing restaurant url and collect all restaurant data in dictionary """

    # if restaurant data was not pass as argument, define new dict
    if restaurant_data is None:
        restaurant_data = {}

    # get restaurant ID using regular expression
    id_restaurant = re.search(r'(?<=-d)\d+(?=-)', url).group(0)
    restaurant_data['id'] = id_restaurant

    # load restaurant page
    driver.get(url)
    # sleep until restaurant page loading
    time.sleep(SLEEP_RESTAURANT)

    # data collecting
    restaurant_data = get_restaurant_info(driver, restaurant_data)
    restaurant_data['reviews'] = get_reviews_info(driver, id_restaurant)

    return restaurant_data


def get_restaurant_info(driver: webdriver.Chrome, restaurant_data: dict) -> dict:
    """ Collect information about restaurant """

    # wait until restaurant <h1> tag with name is located on page.
    # here is no data appending to keep order in dict, just waiting until name is located
    WebDriverWait(driver, timeout=WAIT_RESTAURANT_NAME).until(
        ec.presence_of_element_located(H1_NAME)
    )

    # rating number in search
    try:
        rating_number = driver.find_element(*B_RATING_NUMBER).text
        restaurant_data['number'] = rating_number
    except NoSuchElementException:
        pass

    # name of restaurant
    try:
        name = driver.find_element(*H1_NAME).text
        restaurant_data['name'] = name
    except NoSuchElementException:
        pass

    # restaurant url
    restaurant_data['URL'] = URL

    # url for menu
    try:
        # attribute href appending to <a> after some time
        a_menu = WebDriverWait(driver, timeout=WAIT_MENU_URL).until(
            ec.element_to_be_clickable(A_MENU)
        )
        url_menu = a_menu.get_attribute('href')
        restaurant_data['menu'] = url_menu
    except TimeoutException:
        pass

    # get working hours
    try:
        # press button to get full schedule
        driver.find_element(*BUTTON_POPUP_SCHEDULE).click()
        is_schedule_exists = True
    except NoSuchElementException:
        # schedule does not exists
        is_schedule_exists = False

    if is_schedule_exists:
        # iterate over every div with hours in schedule
        for div_working_hours in driver.find_elements(*DIVS_SCHEDULE):
            # split str by "\n", put in weekday first value and others in times_ranges
            weekday, *times_ranges = div_working_hours.text.splitlines()

            # getting only Sunday and Saturday schedule
            if weekday.lower() in ('sun', 'sat', 'вс', 'cб'):
                # check if hours not exists as key
                if not restaurant_data.get('hours'):
                    restaurant_data['hours'] = {}

                # define list for this weekday to append time ranges
                restaurant_data['hours'][weekday] = []
                # iterating over times_ranges (restaurant may close and open multiple times in one day)
                for time_range in times_ranges:
                    # split every time_range from open time to close time
                    parts_time_range = time_range.split(' - ')
                    restaurant_data['hours'][weekday].append(parts_time_range)

        # close schedule
        driver.find_element(*BUTTON_POPUP_SCHEDULE).click()

        # restaurant rating
        try:
            restaurant_rating = driver.find_element(*SVG_RESTAURANT_RATING).get_attribute('aria-label')
            restaurant_data['restaurant rating'] = restaurant_rating
        except NoSuchElementException:
            pass

    return restaurant_data


def get_reviews_info(driver: webdriver.Chrome,
                     id_restaurant: str
                     ) -> dict:
    """ Collect reviews for this restaurant. Append values to already existing lists """

    # define dict with all reviews data
    reviews_data = {}
    # define counter for case if for loop is empty
    count_reviews = 0
    # page_before may be defined later after "Access Denied", it's to skip already seen pages
    page_before = None

    # check if any review exists on page
    if len(driver.find_elements(*DIV_REVIEW_CONTAINER)) == 0:
        logging.info(f'0 reviews for {id_restaurant=}')
        return {}

    while True:

        # check if langauge filter was selected to "ALL languages"
        if not driver.find_element(*INPUT_LANGUAGE_FILTER_ALL).is_selected():
            # change language filter to "ALL languages"
            WebDriverWait(driver, timeout=WAIT_CHANGE_FILTER).until(
                ec.element_to_be_clickable(SPAN_LANGUAGE_FILTER_ALL)
            ).click()
            # mini-sleep to wait div loading located on page
            time.sleep(SLEEP_WAIT_LOADING_TAG)

        # wait until reviews block is loading after apply filter
        # same algorithm for waiting after new page of reviews, also for filters applying
        while True:
            div_loading = driver.find_element(*DIV_LOADING_LIST_REVIEWS)
            # when loading finished, <div style="display: none;"> or ''
            if div_loading.get_attribute('style') in ('display: none;', ''):
                break

        # sleep while reviews page loading
        time.sleep(SLEEP_REVIEWS_PAGE)

        # there is no pagination if it's single review page
        is_only_one_page, page = is_single_page(driver)

        # define counter to log how many reviews collected
        count_reviews_before = len(reviews_data)
        # iterate over every div review on page
        for div_review in driver.find_elements(*DIV_REVIEW_CONTAINER):

            # check if max reviews OR current page for restaurant already collected
            if MAX_REVIEWS_PER_RESTAURANT == count_reviews or \
                    (page_before and page < page_before):
                continue

            # get data for one review
            try:
                id_review, review_data = get_one_review(driver, div_review)
                # append review data to restaurant data
                reviews_data[id_review] = review_data
                count_reviews = len(reviews_data)
            except Exception:
                # reload page
                driver.refresh()
                # check string part contain in html
                if 'Access Denied' in driver.page_source:
                    # Getting url for current driver to remember current page of reviews. This is useless here,
                    # because tripadvisor redirecting new profile to first page...
                    url_before = driver.current_url
                    # remember page to skip in after driver reload
                    page_before = page
                    # close driver at all
                    driver.quit()
                    # delete driver object from memory
                    del driver
                    logging.info(f'Access denied, rebooting browser. {url_before=}')
                    time.sleep(SLEEP_DRIVER_REFRESH)
                    # get new driver
                    driver = get_driver()
                    # directing to previous URL
                    driver.get(url_before)
                    break
                else:
                    # any other exception shouldn't be handled for now
                    raise
        else:
            logging.info(f'Collected {count_reviews} reviews for {id_restaurant=}.'
                         f' From {page=} new reviews {count_reviews - count_reviews_before}')

            # return if page is only one OR if reviews count is equal max limit
            if is_only_one_page or MAX_REVIEWS_PER_RESTAURANT == count_reviews:
                return reviews_data

            # moving to button next page
            ActionChains(driver).move_to_element(
                driver.find_element(*A_NEXT_REVIEWS_PAGE)
            ).perform()
            # if A_NEXT_REVIEWS_PAGE has class="disabled" it is last page
            if 'disabled' in driver.find_element(*A_NEXT_REVIEWS_PAGE).get_attribute('class').split():
                return reviews_data
            else:
                # click to load new page
                driver.find_element(*A_NEXT_REVIEWS_PAGE).click()


def get_one_review(driver: webdriver.Chrome, div_review: WebElement) -> tuple[str, dict]:
    # define dict which contains information about one review
    review_data = {}

    # user id from <div data-reviewid="some_id">
    id_review = div_review.find_element(*DIV_ID_USER).get_attribute('data-reviewid')

    # scroll to reviewer avatar
    ActionChains(driver).move_to_element(
        div_review.find_element(*DIV_AVATAR)
    ).perform()
    # click on reviewer avatar. WebDriverWait takes here div_review as argument to do
    # relative search of DIV_AVATAR
    WebDriverWait(div_review, timeout=WAIT_AVATAR).until(
        ec.element_to_be_clickable(DIV_AVATAR)
    ).click()
    # sleep until user info loading
    time.sleep(SLEEP_REVIEW_INFO)

    # wait until reviewer info loads
    if not wait_loop_with_timeout(driver, DIV_LOADING_REVIEWER_INFO):
        raise Exception('Probably access denied to website')

    # username from <h3>
    username = WebDriverWait(div_review, timeout=WAIT_USERNAME).until(
        ec.presence_of_element_located(H3_USERNAME)
    ).text
    review_data['username'] = username

    # count of reviews from this user
    count_reviews_user = driver.find_element(*SPAN_COUNT_CONTRIBUTIONS).text
    # get only numeric value
    count_reviews_user = count_reviews_user.split()[0]
    review_data['countsReview'] = count_reviews_user

    # count of excellent reviews from this user
    try:
        count_excellent_reviews = driver.find_element(*SPAN_EXCELLENT_REVIEWS).text
        # count_excellent_reviews = count_excellent_reviews.strip()
        review_data['countExcellent'] = count_excellent_reviews
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
        is_button_show_more_exists = True
    except NoSuchElementException:
        is_button_show_more_exists = False

    if is_button_show_more_exists and count_words_in_span_show_more() == 1:
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
    review_data['review text'] = text

    # date of visit
    date_of_visit = div_review.find_element(*DIV_DATE_VISIT).text
    review_data['date of visit'] = date_of_visit

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
        if not wait_loop_with_timeout(driver, DIV_LOADING_REVIEWER_INFO):
            raise Exception('Probably access denied to website')

        # getting translated text of review
        text_translation = WebDriverWait(driver, timeout=WAIT_TRANSLATION_TEXT).until(
            ec.presence_of_element_located(DIV_TRANSLATION)
        ).text
        review_data['translation'] = text_translation

        # close overlay with translation
        WebDriverWait(driver, timeout=WAIT_CLOSE_TRANSLATION).until(
            ec.element_to_be_clickable(DIV_CLOSE_TRANSLATION)
        ).click()

    return id_review, review_data


def is_single_page(driver: webdriver.Chrome) -> tuple[bool, int]:
    try:
        # parse current page number
        page = WebDriverWait(driver, timeout=WAIT_PAGE_NUMBER).until(
            ec.visibility_of_element_located(CURRENT_PAGE_NUMBER)
        ).text
        # str to int
        page = int(page)
        is_single = False
    except TimeoutException:
        is_single = True
        page = 1
    return is_single, page


def wait_loop_with_timeout(driver: webdriver.Chrome, element_path: tuple[str, str]) -> bool:
    """ Wait with timeout until some loading element is located on page """
    # little sleep before start check
    time.sleep(SLEEP_WAIT_LOADING_TAG)
    # start timer
    timer_reviewer_info = time.time()
    # loop while timer has not expired or element disappeared
    while time.time() - timer_reviewer_info < TIMEOUT_LOADING:
        try:
            driver.find_element(*element_path)
        except NoSuchElementException:
            time.sleep(SLEEP_WAIT_LOADING_TAG)
            return True
    return False


def collect_data():
    # checking input values from constants.py
    check_input_values()
    # getting driver
    driver = get_driver()

    try:
        # directing URL from constants.py
        driver.get(URL)

        # check if page exists and 404 not is beginning of title
        if driver.find_element(*TITLE).text.startswith('404'):
            logging.error(f'Page with {URL=} does not exists')
            exit()

        # collecting restaurants urls
        urls_restaurants = get_urls_restaurants(driver)
        logging.info(f'Total collected {len(urls_restaurants)} restaurant urls')

        # iterating over restaurants urls and collecting data
        for i, url_restaurant in enumerate(urls_restaurants):
            logging.info(f'{i+1}/{len(urls_restaurants)} START scrapping {url_restaurant}')
            restaurant_data = collect_restaurant_data(driver, url_restaurant)
            to_excel(restaurant_data)
            logging.info(f'{i+1}/{len(urls_restaurants)} END scrapping {url_restaurant=}')
        logging.info('\n')
    except Exception as ex:
        logging.error(ex, exc_info=True)
        try:
            driver.save_screenshot('debug.png')
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
        except:
            pass
    finally:
        # fully close driver anyway
        driver.quit()


# Check if file is running "directly"
if __name__ == '__main__':
    # get own logger
    get_logger('scrapper.log')
    # run main function
    collect_data()
