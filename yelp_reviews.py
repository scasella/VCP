import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re
import pickle 
from collections import namedtuple
from utils import get_addresses, get_lat_long
from YelpMap import YelpMap

class Yelp:
    def __init__(self):
        return  
    
    def collect_links(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57.2306j0j7&sourceid=chrome&ie=UTF-8')
        address_dict = get_addresses()
        yelp_list = []
        for key in address_dict:
            link = self._get_google_link(key, 'yelp')
            print(link)
            if link != 'None' and link not in yelp_list: yelp_list.append(link)

        with open('yelp_links.p', 'wb') as f:
            pickle.dump(yelp_list, f)
        self.driver.quit()

    @classmethod
    def build_map(cls):
        #yelp_list_of_dicts = [x for x in cls.access_links()]
        #pickle.dump(yelp_list_of_dicts, open('yelp_info.p', 'wb'))
        yelp_list_of_dicts = pickle.load(open('yelp_info.p', 'rb'))

        for ind, d_dict in enumerate(yelp_list_of_dicts):
            yelp_list_of_dicts[ind]['lat_long_list'] = get_lat_long(d_dict['address'])
        YObject = namedtuple('YObject', ['name', 'address', 'rating', 'reviews', 'link', 'lat_long_list'])
        yelps = [YObject(name=x['name'], address=x['address'], rating=x['rating'], reviews=x['reviews'], link=x['link'], lat_long_list=x['lat_long_list']) for x in yelp_list_of_dicts]

        temp_map = YelpMap()
        for obj in yelps:
            temp_map.add_marker(name=obj.name, rating=obj.rating, reviews=obj.reviews, link=obj.link, lat_long_list=obj.lat_long_list)
        temp_map.save_open()

    @classmethod
    def access_links(cls):
        try:
            temp_list = pickle.load(open('yelp_links.p', 'rb'))
            yelp_list = []
            for x in temp_list:
                if x not in yelp_list:
                    yelp_list.append(x)
            print(len(yelp_list))
        except:
            print('Yelp list does not exist. Run Yelp.collect_links(address_list, get_google_link)')
            return 
        for ind, val in enumerate(yelp_list):
            print(int(ind/len(yelp_list)*100),'%')
            yield cls._do_yelp_pages(val)

    @classmethod
    def _do_yelp_pages(cls, link):
        output_dict = {'name':'', 'address':'', 'rating':'', 'reviews':[], 'link':link}
        res = requests.get(link+'?sort_by=rating_asc')
        soup = BeautifulSoup(res.content, 'html.parser')
        header_rating = soup.findAll('div', {'title':re.compile(' star rating')})
        if header_rating:
            if (int(header_rating[0]['title'][0]) not in [x for x in range(1,6)]): #or (int(soup.find('span', {'class':'review-count rating-qualifier'}).get_text().replace('\n','').replace('  ','')[:2]) < 10): 
                return output_dict
            try:
                output_dict['name'] = soup.findAll('h1', {'class':'biz-page-title'})[0].get_text().replace('\n','').replace('\r','').replace('  ','')
            except:
                return output_dict
            address = ', '.join(soup.findAll('address')[0].strings).replace(' ,','').replace('  ','').replace('\n','').replace('\r','')[2:][:-2]
            output_dict['address'] = address[:-5]+' '+address[-5:]
            output_dict['rating'] = header_rating[0]['title'][:3]
        else:
            return output_dict
        if soup.findAll('div', {'title':'1.0 star rating'}):
            for element in soup.findAll('div', {'title':'1.0 star rating'}):
                try:
                    date = element.parent.nextSibling.nextSibling.text.replace('\n','').replace('  ','')
                    text = element.parent.parent.nextSibling.nextSibling.nextSibling.nextSibling.text.replace('\n','').replace('  ','').replace('\xa0','').replace('  ',' ').replace("\\", "")
                    output_dict['reviews'].append((date, text))
                except:
                    continue
        elif soup.findAll('div', {'title':'2.0 star rating'}):
            for element in soup.findAll('div', {'title':'2.0 star rating'}):
                try: 
                    date = element.parent.nextSibling.nextSibling.text.replace('\n','').replace('  ','')
                    text = element.parent.parent.nextSibling.nextSibling.nextSibling.nextSibling.text.replace('\n','').replace('  ','').replace('\xa0','').replace('  ',' ').replace("\\", "")
                    output_dict['reviews'].append((date, text))
                except:
                    continue
        return output_dict

    def _get_google_link(self, search_term, regex_term):
        while True: 
            if self.driver.find_elements_by_css_selector('input#lst-ib.gsfi'): break
        with ActionChains(self.driver) as action:
            action.move_to_element(self.driver.find_element_by_css_selector('input#lst-ib.gsfi'))
            action.click()
            [action.send_keys(Keys.RIGHT) for x in range(150)]
            [action.send_keys(Keys.BACKSPACE) for x in range(150)]
            action.send_keys(' '.join(search_term.lower().split(' ')[:-1]))
            action.move_to_element(self.driver.find_element_by_xpath('//*[@id="mKlEF"]'))
            action.click()
            action.perform()
            while True:
                if 'results' in self.driver.page_source:
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    soup = soup.findAll('cite', text=re.compile(regex_term))
                    if soup:
                        link = soup[-1].parent.parent.parent.previousSibling.find('a')['href']
                    else:
                        link = 'None'
                    return link
                else:
                    time.sleep(1)

#new_yelp = Yelp()
#new_yelp.collect_links(address_dict, get_google_link)
Yelp.build_map()