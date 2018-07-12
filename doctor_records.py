import requests
from collections import namedtuple
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
        DObject = namedtuple('DObject', ['name', 'address', 'org', 'status', 'link', 'lat_long_list'])
        doctors = [DObject(name=x['name'], address=x['address'], org=x['org'], status=x['status'], link=x['link'], lat_long_list=x['lat_long_list']) for x in doctors]
        temp_map = DoctorMap()
        for obj in doctors:
            temp_map.add_marker(name=obj.name, status=obj.status, org=obj.org, link=obj.link, lat_long_list=obj.lat_long_list)
        temp_map.save_open()

    @classmethod
    def _get_doctor_records(cls, quantity):
        res = pd.read_csv('test3.csv')
        temp = res.values.tolist()
        res = []
        for val in temp:
            if val not in res: res.append(val)
       
        for ind, val in enumerate(res):
            if ind > quantity: break
            print(int(ind/quantity*100), '%')
            name_list = val[0].split(' ')
            if name_list:
                sesh = requests.Session()
                status, link = cls._doctor_lookup(name_list[0], name_list[1], sesh)
                name, address = val[0], val[1]+' '+val[2]
                org = val[3]
                yield {'name':name, 'address':address, 'org':org, 'status':status, 'link':link}

    @classmethod
    def _doctor_lookup(cls, first_name, last_name, sesh):
        print(first_name, last_name)
        res = sesh.get('https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx')
        res = BeautifulSoup(res.content, 'html.parser')
        v_state = res.find('input', {'id':'__VIEWSTATE'})['value']
        v_generator = res.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

        headers = {
            'Origin': 'https://apps.colorado.gov',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'X-MicrosoftAjax': 'Delta=true',
            'X-TS-AJAX-Request': 'true',
            'Referer': 'https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx',
        }

        data = [
            ('ctl00$ScriptManager1', 'ctl00$MainContentPlaceHolder$ucLicenseLookup$UpdtPanelGridLookup|ctl00$MainContentPlaceHolder$ucLicenseLookup$UpdtPanelGridLookup'),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$ddCredPrefix', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbLicenseNumber', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$ddSubCategory', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbFirstName_Contact', first_name),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbLastName_Contact', last_name),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbDBA_Contact', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbCity_ContactAddress', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$ddStates', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ctl03$tbZipCode_ContactAddress', ''),
            ('ctl00$MainContentPlaceHolder$ucLicenseLookup$ResizeLicDetailPopupID_ClientState', '0,0'),
            ('ctl00$OutsidePlaceHolder$ucLicenseDetailPopup$ResizeLicDetailPopupID_ClientState', '0,0'),
            ('__EVENTTARGET', 'ctl00$MainContentPlaceHolder$ucLicenseLookup$UpdtPanelGridLookup'),
            ('__EVENTARGUMENT', '4~~5'),
            ('__VIEWSTATE', v_state),
            ('__VIEWSTATEGENERATOR', v_generator),
            ('__ASYNCPOST', 'true'),
            ('', ''),
            ]

        response = requests.post('https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx', headers=headers, data=data)
                
        if 'CO' in str(response.content):
            try:
                res = BeautifulSoup(response.content, 'html.parser')
                rows = res.findAll('table', {'id':'ctl00_MainContentPlaceHolder_ucLicenseLookup_gvSearchResults'})[0].findAll('tbody')[0].findAll('tr')
                correct_row = cls._get_correct_row(rows)
                print(correct_row)
                if correct_row == 'None': raise Exception('No license found')
                if correct_row == 'Multiple': return ('Multiple', 'https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx')
                status = rows[correct_row].findAll('td')[3].get_text()
                link = cls._get_license_link(sesh, response.content, correct_row)
            except Exception as e:
                print(e)
                status, link = ('None', 'None')
        else:
            return ('None', 'None')
        print(status)
        return status, link

    @classmethod
    def _get_correct_row(cls, rows):
        if len(rows) == 0: return 'None'
        for ind, row in enumerate(rows):
            cells = row.findAll('td')
            if (cells[2].get_text()[:2] in ['DR','AC','PS']) and ('grand junction' in cells[5].get_text().lower()): 
                return ind
        for ind, row in enumerate(rows):
            cells = row.findAll('td')
            if (cells[2].get_text()[:2] in ['DR','AC','PS']) and ('co' in cells[6].get_text().lower()): 
                return ind
        for ind, row in enumerate(rows):
            cells = row.findAll('td')
            if ('grand junction' in cells[5].get_text().lower()): 
                return ind
        return 'Multiple' 

    @classmethod
    def _get_license_link(cls, sesh, source, row):
        link_str = 'ctl00_MainContentPlaceHolder_ucLicenseLookup_gvSearchResults_ctl0'+str(row+3)+'_HyperLinkDetail'
        
        link_id = str(BeautifulSoup(source, 'html.parser').find('a', {'id':link_str})['href'].split('(')[1].split(')')[0].replace("'",''))
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Accept': 'text/html, */*; q=0.01',
            'Referer': 'https://apps.colorado.gov/dora/licensing/Lookup/LicenseLookup.aspx',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'X-TS-AJAX-Request': 'true',
        }
        params = (
            ('id', link_id),
        )
        res = sesh.get('https://apps.colorado.gov/dora/licensing/Lookup/licensedetail.aspx', headers=headers, params=params)
        license_link = BeautifulSoup(res.content, 'html.parser').find('form', {'name':'form1'})['action'][1:]
        link = 'https://apps.colorado.gov/dora/licensing/Lookup'+license_link
        return link

if __name__ == "__main__":
    DoctorRecords.init_records(200)