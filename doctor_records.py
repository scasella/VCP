import requests
from selenium import webdriver
from collections import namedtuple
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pickle
import time
import pandas as pd

from utils import get_addresses, get_lat_long
from DoctorMap import DoctorMap

class DoctorRecords:
    def __init__(self):
        pass

    @classmethod
    def init_records(cls, quantity):
        doctors = [x for x in cls._get_doctor_records(quantity)]
        pickle.dump(doctors, open('doctors_info.p', 'wb'))
        doctors = pickle.load(open('doctors_info.p', 'rb'))
        for ind, d_dict in enumerate(doctors):
            doctors[ind]['lat_long_list'] = get_lat_long(d_dict['address'])
        pickle.dump(doctors, open('doctors_info.p', 'wb'))
        DObject = namedtuple('DObject', ['name', 'address', 'org', 'status', 'link', 'multiple', 'lat_long_list'])
        doctors = [DObject(name=x['name'], address=x['address'], org=x['org'], status=x['status'], link=x['link'], multiple=x['multiple'], lat_long_list=x['lat_long_list']) for x in doctors]
        temp_map = DoctorMap()
        for obj in doctors:
            temp_map.add_marker(name=obj.name, status=obj.status, org=obj.org, link=obj.link, multiple=obj.multiple, lat_long_list=obj.lat_long_list)
        temp_map.save_open()

    @classmethod
    def _get_doctor_records(cls, quantity):
        res = pd.read_csv('test3.csv')
        res = res.values.tolist()[:quantity]

        driver = webdriver.Chrome('chromedriver.exe')
        driver.get('https://www.google.com/search?q=test&oq=test&aqs=chrome..69i57.2306j0j7&sourceid=chrome&ie=UTF-8')
        
        for ind, val in enumerate(res):
            print(int(ind/len(res)*100), '%')
            name_list = val[0].split(' ')
            if name_list:
                multiple, status, link = cls._doctor_lookup(name_list[0], name_list[1], driver)
                name, address = val[0], val[1]+' '+val[2]
                org = val[3]
                yield {'name':name, 'address':address, 'org':org, 'status':status, 'link':link, 'multiple':multiple}
        driver.quit()

    @classmethod
    def _doctor_lookup(cls, first_name, last_name, driver):
        print(first_name, last_name)
        driver.get('https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx')
        while True:
            if 'First Name:' in driver.page_source: break
        with ActionChains(driver) as action:
            action.move_to_element(driver.find_element_by_css_selector('#ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_tbFirstName_Contact'))
            action.click()
            action.send_keys(first_name)
            action.move_to_element(driver.find_element_by_css_selector('#ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_tbLastName_Contact'))
            action.click()
            action.send_keys(last_name)
            action.move_to_element(driver.find_element_by_css_selector('#btnLookup'))
            action.click()
            action.perform()
        while True:
            if 'License Status' in driver.page_source: break
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if 'CO' in driver.page_source:
            try :
                status = soup.findAll('tr', {'class':'CavuGridRow'})[0].findAll('td')[3].get_text()
                multiple = True if len(soup.find('table', {'id':'ctl00_MainContentPlaceHolder_ucLicenseLookup_gvSearchResults'}).findAll('tr')) > 1 else False
                with ActionChains(driver) as action:
                    action.move_to_element(driver.find_element_by_css_selector('#ctl00_MainContentPlaceHolder_ucLicenseLookup_gvSearchResults_ctl03_HyperLinkDetail'))
                    action.click()
                    action.perform()
                while True:
                    if 'Lookup Detail View' in driver.page_source: break
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link = 'https://apps.colorado.gov/dora/licensing/Lookup'+str(soup.find('form', {'name':'form1'})['action'])[1:]
            except:
                status, link, multiple = 'None', 'None', False
        else:
            return 'None', 'None', False
        return multiple, status, link

DoctorRecords.init_records(250)