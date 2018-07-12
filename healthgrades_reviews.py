import requests
from collections import namedtuple
from bs4 import BeautifulSoup
import pickle
import time
import pandas as pd
import re
import pickle  

from HealthgradesMap import HealthgradesMap
from utils import get_addresses, get_lat_long

class Healthgrades:
    
    @classmethod
    def main(cls):
        links_dict = cls._get_doctor_links()
        pickle.dump(links_dict, open('healthgrade_links.p', 'wb'))
        print('Exported')

        healthgrades_list = [x for x in cls._healthgrades_page(links_dict) if x != 'error'] #[(name, address, rating, malpractice, sanctions, board), ...]
        out_list = []
        for ind, val in enumerate(healthgrades_list):
            temp_val = [x for x in val if val.index(x) != 1]
            temp_val.append(get_lat_long(val[1]))
            out_list.append(temp_val)
        hg_map = HealthgradesMap()
        for val in out_list:
            hg_map.add_marker(*val)
        hg_map.save_open()

    @classmethod
    def _get_doctor_links(cls):
        data = get_addresses()
        links_dict = pickle.load(open('healthgrade_links.p', 'rb'))
        #links_dict = {} #{link: (name, address)}
        for _, val in data.items():
            for name_list in val: 
                full_name = name_list[0].lower().capitalize()
                address = name_list[1]+' '+name_list[2]
                city = name_list[2]
                #print(int(ind/len(res)*100), '%')
                name, link = cls._search_google_links(full_name, city)
                if link not in links_dict and link != '':
                    print(link)
                    links_dict[link] = (name, address)
                if len(links_dict) > 200: break
            if len(links_dict) > 200: break
        return links_dict
            
    @classmethod
    def _search_google_links(cls, full_name, city):
        query = '+'.join((full_name.split(' ')+city.split(' ')))
        try:
            res = requests.get('https://www.google.com/search?q=healthgrades+'+query)
        except:
            return ('', '')
        soup = BeautifulSoup(res.content, 'html.parser')
        soup = soup.findAll('a', href=re.compile('https://www.healthgrades.com/providers/'))
        try: 
            link = soup[0]['href'].replace("/url?q=","").split('&')[0]
            return (full_name, link)
        except: 
            return ('', '')
        
    @classmethod
    def _healthgrades_page(cls, links_dict):
        for key, val in links_dict.items():
            try:
                link = key
                response = requests.get(link)
                soup = BeautifulSoup(response.content, 'html.parser')
                inner_soup = soup.find('div', {'data-qa-target':'star-rating-summary'}).find('div', {'class':'filled'})
                rating = len(inner_soup.findAll('span', {'class':'hg3-i-star-full'}))+len(inner_soup.findAll('span', {'class':'hg3-i-star-half'}))*0.5
                name = soup.find('h1', {'data-qa-target':'ProviderDisplayName'}).text
                address = val[1]
                malpractice, sanctions, board = not(('No malpractice history' in str(soup)) or ('not collect malpractice' in str(soup))), not('No sanctions history' in str(soup)), not('No board actions' in str(soup))
                #print(link, sum([malpractice, sanctions, board]))
                yield (name, address, rating, link, malpractice, sanctions, board)
            except Exception as e:
                print(e)
                yield 'error'

if __name__ == "__main__":
    Healthgrades.main()