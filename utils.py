from geopy.geocoders import Nominatim
import pandas as pd

def get_addresses():
    res = pd.read_csv('test3.csv')
    res = res.values.tolist()
    address_dict = {}
    for row in res:
        co_name = row[3]+' '+row[2]
        if co_name not in address_dict:
            address_dict[co_name] = [row]
        else:
            address_dict[co_name].append(row)
    return address_dict

def get_lat_long(address):
    geolocator = Nominatim()
    try:
        location = geolocator.geocode(address)
    except:
        return ('','')    
    if location == None: return ('', '')
    return [float(location.latitude), float(location.longitude)]
