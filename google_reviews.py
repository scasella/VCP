from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from utils import get_addresses, get_lat_long
from GRatingsMap import GRatingsMap

class GoogleReviews:
    def __init__(self):
        pass
    
    @classmethod
    def go_google(cls, quantity):
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get('https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57.2306j0j7&sourceid=chrome&ie=UTF-8')
        ratings_dict = {}
        address_dict = get_addresses()
        count = 0
        for key in address_dict:
            count += 1
            print(int(count/quantity*100),'%')
            if count > quantity: break
            ratings_dict[key] = [x for x in cls._get_google_ratings(key, driver)] #[(text, rating, link)]
        temp_map = GRatingsMap()
        for key, val in ratings_dict.items():
            temp_map.add_marker(name=address_dict[key][0][3], texts=[x[0] for x in val], ratings=[x[1] for x in val], links=[x[2] for x in val], lat_long_list=get_lat_long((address_dict[key][0][1]+' '+address_dict[key][0][2])))
        driver.quit()
        temp_map.save_open()

    @classmethod
    def _get_google_ratings(cls, search_term, driver):
        while True: 
            if driver.find_elements_by_css_selector('input#lst-ib.gsfi'): break
        with ActionChains(driver) as action:
            action.move_to_element(driver.find_element_by_css_selector('input#lst-ib.gsfi'))
            action.click()
            [action.send_keys(Keys.RIGHT) for x in range(100)]
            [action.send_keys(Keys.BACKSPACE) for x in range(100)]
            action.send_keys(' '.join(search_term.lower().split(' ')[:-1]))
            action.move_to_element(driver.find_element_by_xpath('//*[@id="mKlEF"]'))
            action.click()
            action.perform()
            while True:
                if 'results' in driver.page_source:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    soup = soup.findAll('span', {'class':'tPhRLe'})
                    if soup:
                        for element in soup:
                            rating = element['aria-label'][6:9]
                            heading = element.parent.parent.previousSibling.parent.parent.previousSibling.find('a')
                            text, link = heading.text, heading['href']
                            yield (text, rating, link)
                    else:
                        yield ('', '', '')
                    break
                else:
                    time.sleep(1)


GoogleReviews.go_google(250)