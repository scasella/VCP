from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from utils import get_addresses, get_lat_long
from GRatingsMap import GRatingsMap

class GoogleReviews:
    def __init__(self):
        pass
    
    @classmethod
    def go_google(cls, quantity):    
        chrome_options = Options()  
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
        driver.get('https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57.2306j0j7&sourceid=chrome&ie=UTF-8')
        ratings_dict = {}
        address_dict = get_addresses()
        #count = 0
        for key, val in address_dict.items():
            #if count > 20: break
            if (val[0][3] not in ratings_dict) and (val[0][1]+' '+val[0][2] not in [x[0] for _, x in ratings_dict.items()]) :
                ratings_dict[val[0][3]] = (val[0][1]+' '+val[0][2], tuple(x for x in cls._get_google_ratings(key, driver))) #name: (address, [(rating, link, count)] 
                #count+=1
        temp_map = GRatingsMap()
        for key, val in ratings_dict.items():
            if len(val[1]) == 0: continue
            temp_map.add_marker(key, ratings=[x[0] for x in val[1]], links=[x[1] for x in val[1]], counts=[x[2] for x in val[1]], lat_long_list=get_lat_long(val[0]))
        driver.quit()
        temp_map.save_open()

    @classmethod
    def _get_google_ratings(cls, search_term, driver):
        name_list = []
        while True: 
            if driver.find_elements_by_css_selector('input#lst-ib.gsfi'): break
        with ActionChains(driver) as action:
            action.move_to_element(driver.find_element_by_css_selector('input#lst-ib.gsfi'))
            action.click()
            action.send_keys(Keys.CONTROL, 'a')
            action.send_keys(Keys.BACKSPACE)
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
                            link = heading['href']
                            count = element.parent.parent.parent.select('div.slp.f')[0].get_text().replace(' ','').split('-')[1]
                            count = ''.join([x for x in count if x.isdigit()])
                            if count == '': count = '1'
                            if link.split('.')[1:2][0].lower() not in name_list:
                                name_list.append(link.split('.')[1:2][0].lower())
                                yield rating, link, count
                            else:
                                continue
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    if (soup.select('span.Fam1ne.EBe2gf')) and (soup.findAll('span', text=re.compile('Google review'))):
                        rating = soup.select('span.Fam1ne.EBe2gf')[0]['aria-label'][6:9]
                        count = soup.find('span', text=re.compile('Google review')).get_text().split(' ')[0]
                        link = 'https://www.google.com/search?q='+'+'.join(search_term.split(' '))
                        yield rating, link, count
                    break
                else:
                    time.sleep(1)

if __name__ == "__main__":
    GoogleReviews.go_google(150)