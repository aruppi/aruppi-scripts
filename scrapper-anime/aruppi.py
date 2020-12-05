from selenium import webdriver as wb # This is for calling the webdriver as wb
from selenium.webdriver.chrome.options import Options as ChromeOptions # This are the options, if there any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, unquote
from os import path
import os
from pathlib import PurePosixPath
import json

chrome_path = path.join(os.getcwd() + "\\chromedriver.exe") # This is the relative ChromeDriver path

ch_options = ChromeOptions()
ch_options.add_argument("--user-data-dir=C:\\Utilizadores\\guill\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
ch_options.add_argument("--start-maximized")

# This gets the first anime of the listAnimes
driver = wb.Chrome(executable_path=chrome_path, options=ch_options)

# This starts the inital scrapper
def animeflv_scrapper(anime_title):
    """
    This is the scrapper for the animeflv page
    @PARAMS anime_title, search the anime by the title
    then he will save all the information from the anime
    and return the object.
    """

    # I'm just creating the dict here
    anime_result_animeflv = {}

    try:
        driver.implicitly_wait(10)
        driver.get("https://www3.animeflv.net/")
        
    except:
        print("The page didn't load, sorry")
        return False

    search_bar = driver.find_element_by_id("search-anime")
    search_bar.send_keys(anime_title)

    try:
        anime_result = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.title"))
        )
    except:
        return False

    for anime_r in anime_result:

        if anime_r.text.lower() == anime_title.lower():
            
            anime_r.click()

            # Now formatting into the dict
            anime_result_animeflv['id'] = driver.find_element_by_css_selector("h1.Title").text.lower().replace(" ", "-")
            anime_result_animeflv['genres'] = [genre.text.lower() for genre in driver.find_elements_by_css_selector(".Nvgnrs a")]
            anime_result_animeflv['status'] = driver.find_element_by_css_selector(".AnmStts").text.lower()
            anime_result_animeflv['description'] = driver.find_element_by_css_selector(".Description").text

            #print(anime_result_animeflv)
            
            return anime_result_animeflv

    driver.find_element_by_css_selector(".MasResultados").click()

    anime_list = driver.find_elements_by_css_selector("h3.Title")

    for anime_r in anime_list:
        
        if anime_r.text.lower() == anime_title.lower():

            anime_r.click()

            # Now formatting into the dict
            anime_result_animeflv['id'] = driver.find_element_by_css_selector("h1.Title").text.lower().replace(" ", "-")
            anime_result_animeflv['genres'] = [genre.text.lower() for genre in driver.find_elements_by_css_selector(".Nvgnrs a")]
            anime_result_animeflv['status'] = driver.find_element_by_css_selector(".AnmStts").text.lower()
            anime_result_animeflv['description'] = driver.find_element_by_css_selector(".Description").text

            #print(anime_result_animeflv)
            
            return anime_result_animeflv

def jkanime_scrapper(anime_title):
    """
    This is the scrapper for the jkanime page
    @PARAMS anime_title, search the anime by the title
    then he will save all the information from the anime
    and return the object.
    """

    # I'm just creating the dict here
    anime_result_jkanime = {}

    try:
        driver.implicitly_wait(10)
        driver.get("https://www.jkanime.net/")
    except:
        print("The page didn't load, sorry")
        return False

    search_bar = driver.find_element_by_id("search_input")
    search_bar.send_keys(anime_title)
    search_bar.send_keys(Keys.ENTER)

    anime_list = driver.find_elements_by_css_selector("h2.portada-title")

    for anime_r in anime_list:
        if anime_r.text.lower() == anime_title.lower():

            anime_r.click()
            
            anime_result_jkanime['id'] = driver.find_element_by_css_selector(".sinopsis-box h2").text.lower().replace(" ", "-")
            anime_result_jkanime['genres'] = [genre.text.lower() for genre in driver.find_elements_by_xpath('//span[contains(text(), "Genero")]/following-sibling::span//a')]
            anime_result_jkanime['description'] = driver.find_element_by_css_selector(".sinopsis-box p").text
            anime_result_jkanime['status'] = driver.find_element_by_xpath("//div[@class='info-field']//span[text()='Estado:']/following-sibling::span").text.lower()
            
            #print(anime_result_jkanime)
            
            return anime_result_jkanime

def myanimelist_scrapper(anime_title):
    """
    This is the scrapper for the MyAnimeList page
    @PARAMS anime_title, search the anime by the title
    then he will save all the information from the anime
    and return the object
    """

    anime_result_myanimelist = {}

    try:
        driver.implicitly_wait(10)
        driver.get("https://www.myanimelist.net/")
    except:
        print("The page didn't load, sorry")
        return False

    search_bar = driver.find_element_by_id("topSearchText")
    search_bar.send_keys(anime_title)
    
    try:
        anime_result = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.info.anime div.name"))
        )
    except:
        return False

    for anime_r in anime_result:
        if anime_r.text.lower() == anime_title.lower():

            anime_r.click()

            parsed_path = PurePosixPath(
                            unquote(
                                    urlparse(
                                        driver.current_url
                                    ).path
                                )
                            ).parts

            anime_result_myanimelist['score'] = driver.find_element_by_css_selector("div.score-label").text
            anime_result_myanimelist['imageurl'] = driver.find_element_by_css_selector("a img.lazyloaded").get_attribute("src")
            anime_result_myanimelist['id'] = parsed_path[2]

            return anime_result_myanimelist


def start_scrapper(anime_title):
    """
    This starts the scrapper script, he goes to
    animeflv and extract the data from the page,
    if there is no data, go to jkanime and extract
    data
    """

    anime_data = animeflv_scrapper(anime_title)
    myanimelist_obj = myanimelist_scrapper(anime_title)

    if anime_data and myanimelist_obj:
        anime_data['ranking'] = myanimelist_obj['score']
        anime_data['poster'] = myanimelist_obj['imageurl']
        anime_data['mal_id'] = myanimelist_obj['id']

        driver.quit()

        return anime_data
    else:
        anime_data = jkanime_scrapper(anime_title)
        
        if anime_data and myanimelist_obj:
            anime_data['ranking'] = myanimelist_obj['score']
            anime_data['poster'] = myanimelist_obj['imageurl']
            anime_data['mal_id'] = myanimelist_obj['id']

            driver.quit()

            return anime_data
        else:
            print("I didn't found the anime you are searching for t.t")
            driver.quit()
            return "Sorry"

animeResult = start_scrapper("tokyo ghoul") # -> Change the title for other animes !

# Have fun !
with open('animeParsed.json', 'w', encoding='utf-8') as fp:
    json.dump(animeResult, fp, indent=4, ensure_ascii=False )