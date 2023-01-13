# selenium constants for element path
from selenium.webdriver.common.by import By
# to create filepath which not OS dependency
from pathlib import Path

""" Input settings """
# directing this link first
URL: str = ''
# to test
# https://www.tripadvisor.com/Restaurants-g298507-St_Petersburg_Northwestern_District.html'
# https://www.tripadvisor.com/Restaurants-g42139-Detroit_Michigan.html'
# https://www.tripadvisor.com/Restaurants-g298484-Moscow_Central_Russia.html'
# https://www.tripadvisor.com/Restaurants-g187849-Milan_Lombardy.html'
# https://www.tripadvisor.ru/Restaurants-g155019-Toronto_Ontario.html'
# https://www.tripadvisor.ru/Restaurants-g298507-St_Petersburg_Northwestern_District.html'
# https://www.tripadvisor.ru/Restaurants-g298184-Tokyo_Tokyo_Prefecture_Kanto.html'
# https://www.tripadvisor.ru/Restaurants-g187323-Berlin.html'
# https://www.tripadvisor.ru/Restaurants-g42139-Detroit_Michigan.html'
# https://www.tripadvisor.ru/Restaurants-g298484-Moscow_Central_Russia.html'
# https://www.tripadvisor.ru/Restaurants-g187849-Milan_Lombardy.html'

# tested
# https://www.tripadvisor.com/Restaurants-g187314-Augsburg_Swabia_Bavaria.html
# https://www.tripadvisor.com/Restaurants-g60763-New_York_City_New_York.html
# https://www.tripadvisor.ru/Restaurants-g187147-Paris_Ile_de_France.html
# https://www.tripadvisor.com/Restaurants-g155019-Toronto_Ontario.html
# https://www.tripadvisor.com/Restaurants-g298184-Tokyo_Tokyo_Prefecture_Kanto.html
# https://www.tripadvisor.com/Restaurants-g187323-Berlin.html

# max count of restaurants to scrap
MAX_RESTAURANTS_COUNT: int = 10  # 30
# max count of review per restaurant to scrap
MAX_REVIEWS_PER_RESTAURANT: int = 300  # 100
# extension of output file
OUTPUT_EXTENSION: str = '.xlsx'
# string representation of filename for output file
OUTPUT_FILEPATH: str = r'output'
# if True, replace file without asking
APPEND_FILE: bool = True
# define filepath for output file
FILEPATH: Path = Path(OUTPUT_FILEPATH).with_suffix(OUTPUT_EXTENSION)

""" Driver settings """
# headless mode
IS_HEADLESS: bool = False
# implicitly wait https://www.selenium.dev/documentation/webdriver/waits/#implicit-wait
# this type of wait here because it's relate to every action of element finding
WAIT_IMPLICITLY: int = 0

""" SLEEPS AND WAITS """
# just sleeps from time module. These sleeps block main thread
# sleep while loading search page
SLEEP_SEARCH: int = 0
# sleep while loading restaurant page
SLEEP_RESTAURANT: int = 0
# sleep while page with reviews loading
SLEEP_REVIEWS_PAGE: int = 0  # 5
# sleep while loading reviewer info
SLEEP_REVIEW_INFO: int = 0  # 1
# sleep to wait until tag which will define loading is located on page.
SLEEP_WAIT_LOADING_TAG: float = 0.1
# sleep after driver quited
SLEEP_DRIVER_REFRESH: int = 120
# sleep after page urllib3.exceptions.MaxRetryError
SLEEP_RETRY_GET_PAGE: int = 60

# explicit wait https://www.selenium.dev/documentation/webdriver/waits/#explicit-wait
# waiting if <span class="nav next disabled"> is located on page
WAIT_IS_LAST_PAGE: int = 1
# wait until restaurant name is located on page
WAIT_RESTAURANT_NAME: int = 10
# wait for menu url
WAIT_MENU_URL: int = 2
# wait for avatar to be clickable
WAIT_AVATAR: int = 3
# wait for username
WAIT_USERNAME: int = 3
# wait to close the reviewer info
WAIT_CLOSE_REVIEWER_INFO: int = 3
# wait text of translation
WAIT_TRANSLATION_TEXT: int = 10
# wait to close translation overlay
WAIT_CLOSE_TRANSLATION: int = 1
# wait button change filter
WAIT_CHANGE_FILTER: int = 3
# wait page number
WAIT_PAGE_NUMBER: int = 5

# timeout if some element located/not located on page too long
TIMEOUT_LOADING: int = 20

# retries number to load page
RETRIES_LOAD_PAGE: int = 3

""" Elements attributes to locate them """
# page title
TITLE = (By.TAG_NAME, 'title')

# tags <a> on search page to get restaurants hrefs
A_RESTAURANTS_HREFS = (By.XPATH, '//a[@class="Lwqic Cj b"]')
# <a> on search page to open next search page
A_NEXT_SEARCH_PAGE = (By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]')
# <span> which has defined class if this SEARCH page is last
SPAN_IS_LAST_SEARCH_PAGE = (By.XPATH, '//span[@class="nav next disabled"]')
# <a> on restaurant page to open next page with reviews. If page is last,
# this tag has class "disabled"
A_NEXT_REVIEWS_PAGE = (By.XPATH, '//a[contains(@class, "nav next ui_button primary")]')
# <span> on search page, <a> on restaurant page
CURRENT_PAGE_NUMBER = (By.XPATH, '//*[contains(@class, "current")][@data-page-number]')

# <a> with href to restaurant menu
A_MENU = (By.XPATH, '//span[@class="DsyBj cNFrA AsyOO"]/span/following-sibling::a[@href]')
# <b> contains "#n" rating number
B_RATING_NUMBER = (By.XPATH, '//a[@class="AYHFM"]/span/b')
# <h1> with restaurant name
H1_NAME = (By.XPATH, '//h1[@data-test-target="top-info-header"]')
# <span> to see all working hours for restaurant
BUTTON_POPUP_SCHEDULE = (By.XPATH, '//span[@class="mMkhr"]')
# tags <div> with working hours
DIVS_SCHEDULE = (By.CLASS_NAME, 'RiEuX')
# <svg> restaurant rating
SVG_RESTAURANT_RATING = (By.XPATH, '//*[local-name()="svg"][@aria-label]')

# <span> to change language filter to ALL
SPAN_LANGUAGE_FILTER_ALL = (
    By.XPATH, '//div[@data-param="filterLang"]/div[@data-value="ALL"]//span[@class="checkmark"]'
)
# <input> to indicate if filter ALL was selected
INPUT_LANGUAGE_FILTER_ALL = (By.XPATH, '//div[@data-param="filterLang"]//input[@value="ALL"]')
# <div> which has style display while loading list of reviews
DIV_LOADING_LIST_REVIEWS = (By.XPATH, '//div[@class="loadingBox"]/parent::div[@id]')
# tags <div> reviews
DIV_REVIEW_CONTAINER = (By.CLASS_NAME, 'review-container')
# <div> avatar of reviewer. relative search in div_review defined above
DIV_AVATAR = (By.CLASS_NAME, 'ui_avatar')
# <span> appears in the bottom of page after clicking on reviewer avatar
SPAN_REVIEWER_INFO = (By.XPATH, '//span[contains(@class, "ui_overlay ui_popover")]')
# <div> loading reviewer info and translation
DIV_LOADING_REVIEWER_INFO = (By.XPATH,
                             '//span[contains(@class, "ui_overlay ui_popover")]//div[@class="cssLoadingSpinner"]'
                             )
# <div> relative div_review which contains id in attribute
DIV_ID_USER = (By.XPATH, './/div[@data-reviewid]')
# <h3> with reviewer username
H3_USERNAME = (By.XPATH, '//span[contains(@class, "ui_overlay ui_popover")]//h3')
# <span> with count contributions
SPAN_COUNT_CONTRIBUTIONS = (By.XPATH, '//span[contains(@class, "ui_overlay ui_popover")]'
                                      '//span[@class="badgeTextReviewEnhancements"]'
                            )
# <span> with count of excellent reviews from this user
SPAN_EXCELLENT_REVIEWS = (By.XPATH,
                          '//span[contains(@class, "ui_overlay ui_popover")]'
                          '//span[@class="rowCountReviewEnhancements rowCellReviewEnhancements"]'
                          )
# <div> to close reviewer info
DIV_CLOSE_REVIEWER_INFO = (By.XPATH, '//span[contains(@class, "ui_overlay ui_popover")]/div[@class="ui_close_x"]')
# <span> clickable to show more text of reviews. One button activate all others on page.
# Relative to div_review
SPAN_SHOW_MORE = (By.XPATH, './/span[@class="taLnk ulBlueLinks"]')
# <p> which contains review text. Relative to div_review
P_REVIEW_TEXT = (By.TAG_NAME, 'p')
# <div> with date of visit. Relative to div_review
DIV_DATE_VISIT = (By.XPATH, './/div[@class="prw_rup prw_reviews_stay_date_hsx"]')
# <span> button for translation. Relative to div_review
SPAN_TRANSLATE = (By.XPATH, './div/div[@id]/div/div/div/span[@data-url]')
# <div> with translation text inside <span>
DIV_TRANSLATION = (By.XPATH, '//span[contains(@class, "ui_overlay ui_modal")]//div[@class="entry"]')
# <div> to close translation overlay
DIV_CLOSE_TRANSLATION = (By.XPATH, '//span[contains(@class, "ui_overlay ui_modal")]/div[@class="ui_close_x"]')
